import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.utils import get_current_month_key
from app.models.usage_event import UsageEvent
from app.models.user import User

logger = logging.getLogger(__name__)

# Track if AI has been activated (first subscriber)
_ai_activation_logged = False


def _log_ai_activation_if_first(db: Session, subscriber_count: int) -> None:
    """
    Log when AI activates for the FIRST TIME (first paying subscriber).
    This is a critical business event: we can now start using OpenAI.
    """
    global _ai_activation_logged
    
    if not _ai_activation_logged and subscriber_count > 0:
        _ai_activation_logged = True
        logger.warning(
            "🚀🚀🚀 AI COMMERCIALLY ACTIVATED! 🚀🚀🚀 | "
            "subscribers=%d | OpenAI API calls NOW ENABLED | "
            "We have REVENUE - safe to pay OpenAI costs",
            subscriber_count
        )


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


def get_active_subscriber_counts(db: Session) -> Tuple[int, int, int]:
    """Count active paid subscribers by plan (starter/pro/team)."""
    starter_count = db.query(func.count(User.id)).filter(User.plan == "starter").scalar() or 0
    pro_count = db.query(func.count(User.id)).filter(User.plan == "pro").scalar() or 0
    team_count = db.query(func.count(User.id)).filter(User.plan == "team").scalar() or 0
    return int(starter_count), int(pro_count), int(team_count)


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

    COMMERCIAL ACTIVATION SYSTEM:
    - OpenAI only activates if OPENAI_ENABLED=true AND at least 1 active subscriber
    - If OPENAI_ENABLED=false -> returns "openai_disabled"
    - If no active subscribers -> returns "no_subscribers" (AI launching soon)
    - If budget exhausted -> returns "exhausted" (CRITICAL)
    
    This ensures we NEVER PAY OPENAI BEFORE WE HAVE REVENUE.

    GLOBAL_MONTHLY_AI_BUDGET = (active_starter_users * revenue_per_starter_user) +
                               (active_pro_users * revenue_per_pro_user) +
                               (active_team_users * revenue_per_team_user)
    """
    settings = get_settings()
    
    # CRITICAL: Check if OpenAI is globally enabled first
    if not settings.openai_enabled:
        logger.info("AI_DISABLED: OPENAI_ENABLED=false - OpenAI calls blocked globally")
        return BudgetStatus(
            budget=0.0,
            spend=0.0,
            active_pro_users=0,
            active_team_users=0,
            allowed=False,
            reason="openai_disabled",
        )
    
    active_starter, active_pro, active_business = get_active_subscriber_counts(db)
    total_subscribers = active_starter + active_pro + active_business
    
    budget = (
        (active_starter * settings.revenue_per_starter_user) +
        (active_pro * settings.revenue_per_pro_user) +
        (active_business * settings.revenue_per_business_user)
    )
    spend = get_monthly_ai_spend(db)

    # Check for first activation (0 -> 1+ subscribers)
    if total_subscribers > 0:
        _log_ai_activation_if_first(db, total_subscribers)

    if total_subscribers == 0:
        logger.info(
            "AI_NOT_ACTIVATED: No active subscribers yet (OPENAI_ENABLED=true but no revenue)"
        )
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=0,
            allowed=False,
            reason="no_subscribers",
        )

    if budget <= 0:
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=0,
            allowed=False,
            reason="no_budget",
        )

    if spend >= budget:
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=0,
            allowed=False,
            reason="exhausted",
        )

    return BudgetStatus(
        budget=budget,
        spend=spend,
        active_pro_users=active_pro,
        active_team_users=0,
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

    # MONTHLY LIMITS: Use monthly_analyses_count from user model (set by Stripe webhook)
    # Fallback to UsageEvent count if monthly_analyses_count is None (legacy users)
    if user.monthly_analyses_count is not None:
        usage_count = user.monthly_analyses_count
    else:
        # Legacy: count from UsageEvent table
        month_key = get_current_month_key()
        usage_query = db.query(func.count(UsageEvent.id)).filter(
            UsageEvent.user_id == user.id,
            UsageEvent.month_key == month_key,
            UsageEvent.event_type == "profile_analysis",
        )
        usage_count = usage_query.scalar() or 0

    # Get limit based on plan
    if user.plan == "starter":
        limit = settings.usage_limit_starter
        limit_label = "STARTER"
    elif user.plan == "pro":
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

    # Early abuse signal: >=80% of monthly limit consumed within 24h (observability only)
    first_event = (
        db.query(UsageEvent)
        .filter(
            UsageEvent.user_id == user.id,
            UsageEvent.month_key == month_key,
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

    # HARD CAP: Block if limit reached
    if usage_count >= limit:
        logger.warning(
            "%s plan monthly limit reached for user_id=%d (%d/%d)",
            limit_label,
            user.id,
            usage_count,
            limit,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've reached your monthly limit ({limit} analyses/month). Your limit will reset on the 1st of next month.",
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

    - Creates UsageEvent with month_key for monthly tracking (STARTER/PRO/TEAM)
    - Updates User.last_analysis_at for rate limiting
    - Associates cost for budget accounting

    CRITICAL: Only call this AFTER OpenAI API call succeeds.
    """
    settings = get_settings()
    month_key = get_current_month_key()

    resolved_cost = Decimal(str(cost_usd if cost_usd is not None else settings.ai_cost_per_analysis_usd))

    usage_event = UsageEvent(
        user_id=user.id,
        event_type=event_type,
        month_key=month_key,
        cost_usd=resolved_cost,
    )
    db.add(usage_event)

    if user.plan == "free":
        user.lifetime_analyses_count += 1
    else:
        # PAID PLANS: Increment monthly counter (reset by Stripe webhook)
        if user.monthly_analyses_count is None:
            user.monthly_analyses_count = 0
        user.monthly_analyses_count += 1

    user.last_analysis_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(usage_event)

    return usage_event


def get_usage_stats(user: User, db: Session) -> dict:
    """
    Get usage statistics for current period.
    
    - FREE: Returns lifetime usage (no reset)
    - STARTER/PRO/BUSINESS: Returns monthly usage (YYYY-MM)
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
    
    # STARTER/PRO/TEAM: monthly usage (use monthly_analyses_count from user)
    # Fallback to UsageEvent count if monthly_analyses_count is None (legacy users)
    if user.monthly_analyses_count is not None:
        usage_count = user.monthly_analyses_count
    else:
        # Legacy: count from UsageEvent table
        month_key = get_current_month_key()
        usage_count = (
            db.query(func.count(UsageEvent.id))
            .filter(
                UsageEvent.user_id == user.id,
                UsageEvent.month_key == month_key,
                UsageEvent.event_type == "profile_analysis",
            )
            .scalar()
        )
    
    # Get limit based on plan
    if user.plan == "starter":
        limit = settings.usage_limit_starter
    elif user.plan == "pro":
        limit = settings.usage_limit_pro
    elif user.plan == "team":
        limit = settings.usage_limit_team
    else:
        limit = 0
    
    remaining = max(0, limit - usage_count)
    
    return {
        "month_key": get_current_month_key(),
        "used": usage_count,
        "limit": limit,
        "remaining": remaining,
        "plan": user.plan,
        "reset_at": user.monthly_analyses_reset_at,
    }
