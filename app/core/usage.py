import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.utils import get_current_week_key
from app.models.usage_event import UsageEvent
from app.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class BudgetStatus:
    budget: float
    spend: float
    active_pro_users: int
    active_team_users: int
    allowed: bool
    reason: str | None = None  # "no_subscribers", "no_budget", "exhausted"


def _current_month_window() -> Tuple[datetime, datetime]:
    """Return UTC month start and now for spend calculations."""
    now = datetime.now(timezone.utc)
    start = datetime(year=now.year, month=now.month, day=1, tzinfo=timezone.utc)
    return start, now


def get_active_subscriber_counts(db: Session) -> Tuple[int, int]:
    """Count active paid subscribers by plan (pro/team)."""
    pro_count = db.query(func.count(User.id)).filter(User.plan == "pro").scalar() or 0
    team_count = db.query(func.count(User.id)).filter(User.plan == "team").scalar() or 0
    return int(pro_count), int(team_count)


def get_monthly_ai_spend(db: Session) -> float:
    """Calculate accumulated AI spend for the current month."""
    start, now = _current_month_window()
    total = (
        db.query(func.coalesce(func.sum(UsageEvent.cost_usd), 0))
        .filter(UsageEvent.created_at >= start, UsageEvent.created_at <= now)
        .scalar()
    )
    try:
        return float(total or 0)
    except Exception:
        return 0.0


def evaluate_budget_status(db: Session) -> BudgetStatus:
    """
    Compute global budget availability based on active subscribers and spend.

    GLOBAL_MONTHLY_AI_BUDGET = (active_pro_users * revenue_per_pro_user) +
                               (active_team_users * revenue_per_team_user)
    - If no active paid users -> force preview (no OpenAI)
    - If budget <= 0 -> OpenAI disabled
    - If spend >= budget -> OpenAI disabled (CRITICAL)
    """
    settings = get_settings()
    active_pro, active_team = get_active_subscriber_counts(db)
    budget = (active_pro * settings.revenue_per_pro_user) + (active_team * settings.revenue_per_team_user)
    spend = get_monthly_ai_spend(db)

    if active_pro == 0 and active_team == 0:
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=active_team,
            allowed=False,
            reason="no_subscribers",
        )

    if budget <= 0:
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=active_team,
            allowed=False,
            reason="no_budget",
        )

    if spend >= budget:
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=active_team,
            allowed=False,
            reason="exhausted",
        )

    return BudgetStatus(
        budget=budget,
        spend=spend,
        active_pro_users=active_pro,
        active_team_users=active_team,
        allowed=True,
    )


def check_usage_limit(user: User, db: Session) -> None:
    """
    Enforce rate limit and paid-plan caps BEFORE any OpenAI call.

    Order enforced here: rate limit -> plan limit -> abuse signal logging.
    Free plan should be handled by the caller (preview mode) and must not
    reach this function.
    """
    settings = get_settings()

    if settings.disable_all_analyses:
        logger.warning(
            "KILL SWITCH TRIGGERED: All analyses disabled (user_id=%d, plan=%s)",
            user.id,
            user.plan,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily disabled. Please try again later.",
        )

    if user.plan == "free":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="See example lead analysis. Upgrade to unlock real checks.",
        )

    # RATE LIMIT: 1 analysis every 30 seconds
    if user.last_analysis_at:
        time_since_last = datetime.now(timezone.utc) - user.last_analysis_at
        if time_since_last.total_seconds() < settings.rate_limit_seconds:
            seconds_remaining = settings.rate_limit_seconds - int(time_since_last.total_seconds())
            logger.warning(
                "Rate limit exceeded for user_id=%d (plan=%s, wait=%ds)",
                user.id,
                user.plan,
                seconds_remaining,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit: Please wait {seconds_remaining} seconds before next analysis.",
            )

    week_key = get_current_week_key()
    usage_query = db.query(func.count(UsageEvent.id)).filter(
        UsageEvent.user_id == user.id,
        UsageEvent.week_key == week_key,
        UsageEvent.event_type == "profile_analysis",
    )
    usage_count = usage_query.scalar() or 0

    if user.plan == "pro":
        limit = settings.usage_limit_pro
        limit_label = "PRO"
    elif user.plan == "team":
        limit = settings.usage_limit_team
        limit_label = "TEAM"
    else:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="See example lead analysis. Upgrade to unlock real checks.",
        )

    predicted_usage = usage_count + 1

    # Early abuse signal: >=80% of weekly limit consumed within 24h (observability only)
    first_event = (
        db.query(UsageEvent)
        .filter(
            UsageEvent.user_id == user.id,
            UsageEvent.week_key == week_key,
            UsageEvent.event_type == "profile_analysis",
        )
        .order_by(UsageEvent.created_at.asc())
        .first()
    )
    if (
        limit > 0
        and predicted_usage >= int(limit * 0.8)
        and first_event
        and (datetime.now(timezone.utc) - first_event.created_at) <= timedelta(hours=24)
    ):
        logger.warning(
            "Early abuse signal: user_id=%d plan=%s usage=%d/%d window<24h",
            user.id,
            user.plan,
            predicted_usage,
            limit,
        )

    if usage_count >= limit:
        logger.warning(
            "%s plan weekly limit reached for user_id=%d (%d/%d)",
            limit_label,
            user.id,
            usage_count,
            limit,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've reached your weekly fair-use limit ({limit} analyses/week). Limit resets next Monday.",
        )

    # Pre-mark last_analysis_at to enforce rate-limit even if AI fails (PRO/TEAM)
    user.last_analysis_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()


def record_usage(
    user: User,
    db: Session,
    event_type: str = "profile_analysis",
    *,
    cost_usd: float | None = None,
) -> UsageEvent:
    """
    Record a usage event after successful analysis.

    - Creates UsageEvent with week_key for weekly tracking (PRO/TEAM)
    - Updates User.last_analysis_at for rate limiting
    - Associates cost for budget accounting

    CRITICAL: Only call this AFTER OpenAI API call succeeds.
    """
    settings = get_settings()
    week_key = get_current_week_key()

    resolved_cost = Decimal(str(cost_usd if cost_usd is not None else settings.ai_cost_per_analysis_usd))

    usage_event = UsageEvent(
        user_id=user.id,
        event_type=event_type,
        week_key=week_key,
        cost_usd=resolved_cost,
    )
    db.add(usage_event)

    if user.plan == "free":
        user.lifetime_analyses_count += 1

    user.last_analysis_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(usage_event)

    return usage_event


def get_usage_stats(user: User, db: Session) -> dict:
    """
    Get usage statistics for current period.
    
    - FREE: Returns lifetime usage (no reset)
    - PRO/TEAM: Returns weekly usage (ISO week)
    """
    settings = get_settings()
    
    if user.plan == "free":
        # FREE: lifetime usage
        used = user.lifetime_analyses_count
        limit = settings.usage_limit_free
        return {
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
        }
    
    # PRO/TEAM: weekly usage
    week_key = get_current_week_key()
    usage_count = (
        db.query(func.count(UsageEvent.id))
        .filter(
            UsageEvent.user_id == user.id,
            UsageEvent.week_key == week_key,
            UsageEvent.event_type == "profile_analysis",
        )
        .scalar()
    )
    
    # Get limit based on plan
    if user.plan == "pro":
        limit = settings.usage_limit_pro
    elif user.plan == "team":
        limit = settings.usage_limit_team
    else:
        limit = 0
    
    remaining = max(0, limit - usage_count)
    
    return {
        "week_key": week_key,
        "used": usage_count,
        "limit": limit,
        "remaining": remaining,
        "plan": user.plan,
    }
