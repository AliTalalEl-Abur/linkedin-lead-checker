import logging
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.analysis_cache import build_profile_hash, cache_analysis, get_cached_analysis
from app.core.config import get_settings
from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.usage import (
    BudgetStatus,
    check_usage_limit,
    evaluate_budget_status,
    get_usage_stats,
    record_usage,
)
from app.models.user import User
from app.schemas.ai_responses import DimensionScores, FitScoringResult, ICPConfig
from app.schemas.analyze import (
    AnalyzeProfileRequest,
    AnalyzeProfileResponse,
    AnalyzeLinkedInRequest,
    AnalyzeLinkedInWithModeRequest,
    AnalyzeLinkedInResponse,
    AnalyzeLinkedInUI,
    AnalyzeStableResponse,
)
from app.services import get_ai_service, run_fit, run_decision

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["analyze"])

FREE_COPY = "Upgrade to unlock full AI-powered analysis."
PRO_COPY = "AI-powered profile analysis for smarter outreach."
NO_BUDGET_COPY = "Analysis temporarily unavailable. Upgrade to unlock."
AI_LAUNCHING_SOON = "AI analysis launching soon. Be among the first!"
FREE_BANNER = "Quick Analysis"
FREE_MESSAGE = "Upgrade to unlock full AI-powered insights."
AI_SOON_MESSAGE = "Full AI analysis coming soon - join the waitlist!"

# Free tier insights - valuable but limited
FREE_INSIGHTS = [
    "Profile shows professional experience relevant to B2B outreach",
    "Active LinkedIn presence with industry connections",
    "Career progression indicates decision-making authority",
    "Engagement patterns suggest openness to business opportunities",
    "Profile completeness indicates professional communication preference",
    "Industry alignment with typical target market profiles"
]


def _score_to_stars(score: float) -> int:
    return max(1, min(5, int(round(score / 20))))


def _stable_response(
    *,
    mode: str,
    score: float,
    insights: list[str],
    decision: bool,
    remaining: int | None = None,
) -> AnalyzeStableResponse:
    return AnalyzeStableResponse(
        mode=mode,
        score=score,
        stars=_score_to_stars(score),
        insights=insights,
        decision=decision,
        remaining=remaining,
    )


def _preview_stable_response(profile: dict, user: User) -> AnalyzeStableResponse:
    import random

    base_score = 65.0 + (hash(str(profile)) % 16)
    selected_insights = random.sample(FREE_INSIGHTS, min(3, len(FREE_INSIGHTS)))
    logger.info(
        "Preview response generated (no AI call): user_id=%d, plan=%s",
        user.id,
        user.plan,
    )
    return _stable_response(
        mode="preview",
        score=base_score,
        insights=selected_insights,
        decision=True,
        remaining=None,
    )


def _extract_identity(profile_data: dict) -> Tuple[str, str]:
    """Extract name and headline from profile data."""
    name = (
        profile_data.get("name")
        or profile_data.get("full_name")
        or profile_data.get("fullName")
        or " ".join(
            filter(
                None,
                [
                    profile_data.get("first_name") or profile_data.get("firstName"),
                    profile_data.get("last_name") or profile_data.get("lastName"),
                ],
            )
        )
    )
    headline = (
        profile_data.get("headline")
        or profile_data.get("title")
        or profile_data.get("occupation")
        or "Potential lead"
    )
    return name or "This lead", headline


def _determine_preview(user: User, budget_status: BudgetStatus, db: Session) -> Tuple[bool, str | None]:
    """Determine if user gets free tier or full AI analysis."""
    # CRITICAL: Check OPENAI_ENABLED first
    settings = get_settings()
    if not settings.openai_enabled:
        logger.warning(
            "AI_CALL_BLOCKED_OPENAI_DISABLED: user_id=%d, plan=%s",
            user.id,
            user.plan,
        )
        return True, "openai_disabled"
    
    if budget_status.reason == "exhausted":
        logger.critical(
            "Global AI budget exhausted (spend=%.2f, budget=%.2f)",
            budget_status.spend,
            budget_status.budget,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=NO_BUDGET_COPY,
        )

    # Commercial activation: no subscribers yet (AI not active)
    if budget_status.reason == "no_subscribers":
        logger.info(
            "AI_LAUNCHING_SOON: No subscribers yet - showing preview (user_id=%d, plan=%s)",
            user.id,
            user.plan,
        )
        return True, "no_subscribers"

    if budget_status.reason == "no_budget":
        if user.plan in {"pro", "team", "starter", "business"}:
            logger.warning(
                "User attempted real analysis without budget (user_id=%d, plan=%s, reason=%s)",
                user.id,
                user.plan,
                budget_status.reason,
            )
        return True, budget_status.reason

    # CRITICAL: Check if user has active subscription
    if user.plan not in {"starter", "pro", "business"}:
        logger.warning(
            "AI_CALL_BLOCKED_NO_SUBSCRIPTION: user_id=%d, plan=%s",
            user.id,
            user.plan,
        )
        return True, "free_plan"
    
    # CRITICAL: Check remaining_analyses BEFORE allowing AI call
    usage_stats = get_usage_stats(user, db)
    if usage_stats["remaining"] <= 0:
        logger.warning(
            "AI_CALL_BLOCKED_LIMIT_REACHED: user_id=%d, plan=%s, used=%d, limit=%d",
            user.id,
            user.plan,
            usage_stats["used"],
            usage_stats["limit"],
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "monthly_limit_reached",
                "message": "You've reached your monthly AI analysis limit. Upgrade your plan to keep analyzing LinkedIn profiles without interruptions.",
                "used": usage_stats["used"],
                "limit": usage_stats["limit"],
                "plan": user.plan
            }
        )

    return False, None


def _serve_cached_profile(db: Session, profile_hash: str) -> AnalyzeProfileResponse | None:
    cached = get_cached_analysis(db, profile_hash, "profile")
    if not cached:
        return None
    logger.info("Serving cached profile analysis (hash=%s)", profile_hash)
    cached.setdefault("preview", False)
    cached.setdefault("message", PRO_COPY)
    return AnalyzeProfileResponse(**cached)


def _serve_cached_linkedin(db: Session, profile_hash: str) -> AnalyzeLinkedInResponse | None:
    cached = get_cached_analysis(db, profile_hash, "linkedin")
    if not cached:
        return None
    logger.info("Serving cached LinkedIn analysis (hash=%s)", profile_hash)
    cached.setdefault("preview", False)
    cached["cache_hit"] = True
    return AnalyzeLinkedInResponse(**cached)


def _free_tier_profile_response(profile_data: dict, user: User, db: Session, preview_reason: str | None = None) -> AnalyzeProfileResponse:
    """Generate free tier response without consuming AI credits."""
    import random
    
    usage_stats = get_usage_stats(user, db)
    name, headline = _extract_identity(profile_data)
    
    # Generate consistent but varied score (60-80 range)
    score = 65.0 + (hash(str(profile_data)) % 16)  # 65-80
    
    # Select 3 insights
    selected_insights = random.sample(FREE_INSIGHTS, min(3, len(FREE_INSIGHTS)))
    insights_text = "\n".join([f"• {insight}" for insight in selected_insights])
    
    # Determine banner and message based on preview reason
    banner = FREE_BANNER
    message = FREE_MESSAGE
    
    if preview_reason == "no_subscribers":
        banner = "Preview Mode"
        message = AI_SOON_MESSAGE
    elif preview_reason == "openai_disabled":
        banner = "Preview Mode"
        message = AI_LAUNCHING_SOON
    
    reasoning = f"{banner}\n\n{insights_text}\n\n💡 {message}\n\nLead: {name} | {headline}"
    
    logger.info(
        "Free tier response generated (no AI call): user_id=%d, plan=%s, reason=%s",
        user.id,
        user.plan,
        preview_reason or "free_plan"
    )
    
    return AnalyzeProfileResponse(
        should_contact=True,
        score=score,
        reasoning=reasoning,
        usage_remaining=usage_stats["remaining"],
        preview=True,
        message=message,
    )


def _preview_linkedin_response(profile: dict, user: User, message: str, preview_reason: str | None = None) -> AnalyzeLinkedInResponse:
    """Generate free tier LinkedIn response without consuming AI credits."""
    import random
    
    name, headline = _extract_identity(profile)
    
    # Generate consistent but varied score (60-80 range)
    base_score = 65.0 + (hash(str(profile)) % 16)  # 65-80
    
    # Select 3 insights
    selected_insights = random.sample(FREE_INSIGHTS, min(3, len(FREE_INSIGHTS)))
    
    # Determine banner based on preview reason
    banner = FREE_BANNER
    if preview_reason in ["no_subscribers", "openai_disabled"]:
        banner = "Preview Mode - AI Launching Soon"
    
    logger.info(
        "LinkedIn free tier response generated (no AI call): user_id=%d, plan=%s, reason=%s",
        user.id,
        user.plan,
        preview_reason or "free_plan"
    )
    
    qualification = FitScoringResult(
        overall_score=base_score,
        dimension_scores=DimensionScores(
            seniority_match=base_score - 5.0,
            industry_match=base_score,
            company_size_match=base_score - 7.0,
            skills_match=base_score + 5.0,
            experience_match=base_score - 2.0,
            engagement_level=base_score - 10.0,
        ),
        positive_signals=selected_insights,
        negative_signals=["⚠️ Upgrade for full AI-powered analysis"],
        data_quality=70.0,
        confidence=50.0,
    )
    
    ui = AnalyzeLinkedInUI(
        should_contact=True,
        priority="medium",
        score=base_score,
        reasoning=f"{banner}\\n\\n💡 {message}\\n\\nLead: {name} | {headline}",
        key_points=selected_insights,
        suggested_approach="🔓 Unlock full AI analysis for personalized outreach recommendations.",
        red_flags=["Upgrade for personalized AI-powered insights"],
        next_steps="Subscribe to unlock full AI-powered lead analysis.",
    )
    
    return AnalyzeLinkedInResponse(
        qualification=qualification,
        ui=ui,
        plan=user.plan,
        preview=True,
        message=message,
        cache_hit=False,
    )


@router.post("", response_model=AnalyzeStableResponse, summary="Analyze LinkedIn profile with mode")
def analyze_linkedin_with_mode(
    request: AnalyzeLinkedInWithModeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request,
):
    """Analyze LinkedIn data with explicit mode: preview or ai."""
    request_id = getattr(getattr(http_request, "state", None), "request_id", "unknown")
    logger.info(
        "ANALYZE_REQUEST | request_id=%s | user_id=%d | mode=%s",
        request_id,
        current_user.id,
        request.mode,
    )
    profile = request.profile_extract or {}
    if request.profile_url:
        profile.setdefault("profile_url", request.profile_url)

    if request.mode == "preview":
        return _preview_stable_response(profile, current_user)

    settings = get_settings()
    if settings.disable_all_analyses:
        logger.warning("KILL SWITCH TRIGGERED: All analyses disabled (user_id=%d)", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily disabled. Please try again later.",
        )

    if not settings.openai_enabled:
        logger.warning(
            "AI_CALL_BLOCKED_OPENAI_DISABLED: user_id=%d, plan=%s",
            current_user.id,
            current_user.plan,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently disabled. Please try again later.",
        )

    paid_plans = {"starter", "pro", "team", "business"}
    active_statuses = {"active", "trialing"}
    if current_user.plan not in paid_plans or current_user.subscription_status not in active_statuses:
        logger.warning(
            "AI_CALL_BLOCKED_NO_SUBSCRIPTION: user_id=%d, plan=%s, status=%s",
            current_user.id,
            current_user.plan,
            current_user.subscription_status,
        )
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required to run AI analysis.",
        )

    usage_stats = get_usage_stats(current_user, db)
    if usage_stats["remaining"] <= 0:
        logger.warning(
            "AI_CALL_BLOCKED_LIMIT_REACHED: user_id=%d, plan=%s, used=%d, limit=%d",
            current_user.id,
            current_user.plan,
            usage_stats["used"],
            usage_stats["limit"],
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You've reached your monthly AI analysis limit.",
        )

    check_usage_limit(current_user, db)

    if current_user.icp_config_json:
        icp_config = ICPConfig(**current_user.icp_config_json)
    else:
        icp_config = ICPConfig(
            target_industries=None,
            target_seniority=None,
            company_size_min=0,
            company_size_max=1_000_000,
            required_skills=[],
            min_years_experience=0,
            target_locations=None,
            exclude_keywords=None,
        )

    logger.info(
        "AI_CALL_APPROVED: Starting LinkedIn analysis (user_id=%d, plan=%s, remaining=%d)",
        current_user.id,
        current_user.plan,
        usage_stats["remaining"],
    )

    try:
        fit = run_fit(profile, icp_config)
        decision = run_decision(fit, profile)
    except RuntimeError as e:
        logger.error("OpenAI API error for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again in a few moments.",
        )
    except ValueError as e:
        logger.error("Invalid AI response for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service returned invalid response. Please try again.",
        )
    except Exception as e:
        logger.error(
            "Unexpected error in LinkedIn analysis for user_id=%d: %s",
            current_user.id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )

    record_usage(current_user, db, cost_usd=settings.ai_cost_per_analysis_usd)
    updated_usage = get_usage_stats(current_user, db)

    insights = list(decision.key_points or [])
    if not insights and decision.reasoning:
        insights = [decision.reasoning]

    return _stable_response(
        mode="ai",
        score=decision.score,
        insights=insights,
        decision=decision.should_contact,
        remaining=updated_usage["remaining"],
    )


@router.post("/profile", response_model=AnalyzeProfileResponse, summary="Analyze LinkedIn profile")
def analyze_profile(
    request: AnalyzeProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze a LinkedIn profile with strict economic safety rails."""
    settings = get_settings()

    if settings.disable_all_analyses:
        logger.warning("KILL SWITCH TRIGGERED: All analyses disabled (user_id=%d)", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily disabled. Please try again later.",
        )

    if current_user.plan == "free" and settings.disable_free_plan:
        logger.warning("Free plan disabled via kill switch (user_id=%d)", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=FREE_COPY,
        )

    if current_user.plan == "free" and settings.disable_free_plan:
        logger.warning("Free plan disabled via kill switch (user_id=%d)", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=FREE_COPY,
        )

    budget_status = evaluate_budget_status(db)
    preview_mode, preview_reason = _determine_preview(current_user, budget_status, db)
    profile_data = request.linkedin_profile_data or {}

    if preview_mode:
        # Log based on specific reason
        if preview_reason == "limit_reached":
            logger.warning(
                "AI_CALL_BLOCKED_LIMIT_REACHED: Preview mode (user_id=%d, plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
        elif preview_reason in {"free_plan", "openai_disabled"}:
            logger.info(
                "AI_CALL_BLOCKED_NO_SUBSCRIPTION: Preview mode (user_id=%d, plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
        else:
            logger.info(
                "Preview Mode activated for user_id=%d (plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
        return _free_tier_profile_response(profile_data, current_user, db, preview_reason)

    profile_hash = build_profile_hash(profile_data)
    cached_response = _serve_cached_profile(db, profile_hash)
    if cached_response:
        return cached_response

    # Rate limit and plan cap
    check_usage_limit(current_user, db)

    # CRITICAL SAFETY CHECK: Double-verify before OpenAI call
    settings = get_settings()
    if not settings.openai_enabled:
        logger.error(
            "AI_CALL_BLOCKED_OPENAI_DISABLED: Critical safety check failed - OpenAI disabled but reached AI call point (user_id=%d)",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently disabled. Please try again later.",
        )
    
    # Double-check remaining analyses
    usage_stats = get_usage_stats(current_user, db)
    if usage_stats["remaining"] <= 0:
        logger.error(
            "AI_CALL_BLOCKED_LIMIT_REACHED: Critical safety check failed - limit reached but passed validation (user_id=%d, used=%d, limit=%d)",
            current_user.id,
            usage_stats["used"],
            usage_stats["limit"],
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've reached your monthly limit ({usage_stats['limit']} analyses/month). Your limit will reset on the 1st of next month.",
        )

    # Get user's ICP config (if set)
    icp_config = None
    if current_user.icp_config_json:
        icp_config = ICPConfig(**current_user.icp_config_json)

    logger.info(
        "AI_CALL_APPROVED: Starting profile analysis (user_id=%d, plan=%s, remaining=%d)",
        current_user.id,
        current_user.plan,
        usage_stats["remaining"],
    )

    try:
        ai_service = get_ai_service()
        decision = ai_service.analyze_profile(
            profile_data=profile_data,
            icp_config=icp_config,
        )
    except RuntimeError as e:
        logger.error("OpenAI API error for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again in a few moments.",
        )
    except ValueError as e:
        logger.error("Invalid AI response for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service returned invalid response. Please try again.",
        )
    except Exception as e:
        logger.error(
            "Unexpected error in profile analysis for user_id=%d: %s",
            current_user.id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )

    # Record usage event AFTER successful analysis
    record_usage(current_user, db, cost_usd=settings.ai_cost_per_analysis_usd)
    logger.info("Analysis successful for user_id=%d, decision=%s", current_user.id, decision.should_contact)

    usage_stats = get_usage_stats(current_user, db)
    response = AnalyzeProfileResponse(
        should_contact=decision.should_contact,
        score=decision.score,
        reasoning=decision.reasoning,
        usage_remaining=usage_stats["remaining"],
        preview=False,
        message=PRO_COPY,
    )

    cache_analysis(
        db,
        profile_hash=profile_hash,
        response_type="profile",
        payload=response.model_dump(),
        user_id=current_user.id,
    )

    return response


@router.post("/linkedin", response_model=AnalyzeLinkedInResponse, summary="Analyze extracted LinkedIn profile")
def analyze_linkedin(
    request: AnalyzeLinkedInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze extracted LinkedIn data following the mandated execution order."""
    settings = get_settings()

    if settings.disable_all_analyses:
        logger.warning("KILL SWITCH TRIGGERED: All analyses disabled (user_id=%d)", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analysis service temporarily disabled. Please try again later.",
        )

    budget_status = evaluate_budget_status(db)
    preview_mode, preview_reason = _determine_preview(current_user, budget_status, db)
    profile = request.profile_extract or {}

    if preview_mode:
        # Log based on specific reason
        if preview_reason == "limit_reached":
            logger.warning(
                "AI_CALL_BLOCKED_LIMIT_REACHED: Preview mode for LinkedIn (user_id=%d, plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
            preview_message = "You've reached your monthly analysis limit. Upgrade or wait for your limit to reset."
        elif preview_reason in {"free_plan", "openai_disabled"}:
            logger.info(
                "AI_CALL_BLOCKED_NO_SUBSCRIPTION: Preview mode for LinkedIn (user_id=%d, plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
            preview_message = FREE_COPY
        elif preview_reason == "no_subscribers":
            logger.info(
                "AI_LAUNCHING_SOON: No active subscribers yet - showing preview (user_id=%d, plan=%s)",
                current_user.id,
                current_user.plan,
            )
            preview_message = AI_SOON_MESSAGE
        else:
            logger.info(
                "Preview Mode activated for LinkedIn endpoint (user_id=%d, plan=%s, reason=%s)",
                current_user.id,
                current_user.plan,
                preview_reason,
            )
            preview_message = NO_BUDGET_COPY if preview_reason == "no_budget" else FREE_COPY
        return _preview_linkedin_response(profile, current_user, preview_message, preview_reason)

    profile_hash = build_profile_hash(profile)
    cached_response = _serve_cached_linkedin(db, profile_hash)
    if cached_response:
        return cached_response

    # Rate limit and plan cap
    check_usage_limit(current_user, db)

    # CRITICAL SAFETY CHECK: Double-verify before OpenAI call
    settings = get_settings()
    if not settings.openai_enabled:
        logger.error(
            "AI_CALL_BLOCKED_OPENAI_DISABLED: Critical safety check failed - OpenAI disabled but reached AI call point (user_id=%d)",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently disabled. Please try again later.",
        )
    
    # Double-check remaining analyses
    usage_stats = get_usage_stats(current_user, db)
    if usage_stats["remaining"] <= 0:
        logger.error(
            "AI_CALL_BLOCKED_LIMIT_REACHED: Critical safety check failed - limit reached but passed validation (user_id=%d, used=%d, limit=%d)",
            current_user.id,
            usage_stats["used"],
            usage_stats["limit"],
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You've reached your monthly limit ({usage_stats['limit']} analyses/month). Your limit will reset on the 1st of next month.",
        )

    # Load ICP from user or default
    if current_user.icp_config_json:
        icp_config = ICPConfig(**current_user.icp_config_json)
    else:
        icp_config = ICPConfig(
            target_industries=None,
            target_seniority=None,
            company_size_min=0,
            company_size_max=1_000_000,
            required_skills=[],
            min_years_experience=0,
            target_locations=None,
            exclude_keywords=None,
        )

    logger.info(
        "AI_CALL_APPROVED: Starting LinkedIn analysis (user_id=%d, plan=%s, remaining=%d)",
        current_user.id,
        current_user.plan,
        usage_stats["remaining"],
    )

    try:
        fit = run_fit(profile, icp_config)
        decision = run_decision(fit, profile)
    except RuntimeError as e:
        logger.error("OpenAI API error for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again in a few moments.",
        )
    except ValueError as e:
        logger.error("Invalid AI response for user_id=%d: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service returned invalid response. Please try again.",
        )
    except Exception as e:
        logger.error(
            "Unexpected error in LinkedIn analysis for user_id=%d: %s",
            current_user.id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )

    # Record successful usage only after valid response
    record_usage(current_user, db, cost_usd=settings.ai_cost_per_analysis_usd)
    logger.info(
        "LinkedIn analysis successful for user_id=%d, decision=%s",
        current_user.id,
        decision.should_contact,
    )

    ui = AnalyzeLinkedInUI(
        should_contact=decision.should_contact,
        priority=decision.priority,
        score=decision.score,
        reasoning=decision.reasoning,
        key_points=decision.key_points,
        suggested_approach=decision.suggested_approach,
        red_flags=decision.red_flags,
        next_steps=decision.next_steps,
    )

    response = AnalyzeLinkedInResponse(
        qualification=fit,
        ui=ui,
        plan=current_user.plan,
        preview=False,
        message=PRO_COPY,
        cache_hit=False,
    )

    cache_analysis(
        db,
        profile_hash=profile_hash,
        response_type="linkedin",
        payload=response.model_dump(),
        user_id=current_user.id,
    )

    return response
