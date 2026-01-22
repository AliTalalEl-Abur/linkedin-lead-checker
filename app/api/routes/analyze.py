import logging
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, status
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
    AnalyzeLinkedInResponse,
    AnalyzeLinkedInUI,
)
from app.services import get_ai_service, run_fit, run_decision

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["analyze"])

FREE_COPY = "See example lead analysis. Upgrade to unlock real checks."
PRO_COPY = "Unlimited lead checks (fair use). Real AI-powered analysis."
NO_BUDGET_COPY = "Real-time analysis temporarily unavailable. Upgrade to unlock."
PREVIEW_BANNER = "Example result - upgrade to unlock real lead checks"


def _extract_identity(profile_data: dict) -> Tuple[str, str]:
    """Return best-effort (name, headline) tuple for preview copy."""
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


def _determine_preview(user: User, budget_status: BudgetStatus) -> Tuple[bool, str | None]:
    """Apply fundamental gating rules to decide preview vs real analysis."""
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

    if budget_status.reason in {"no_subscribers", "no_budget"}:
        if user.plan in {"pro", "team"}:
            logger.warning(
                "User attempted real analysis without budget (user_id=%d, plan=%s, reason=%s)",
                user.id,
                user.plan,
                budget_status.reason,
            )
        return True, budget_status.reason

    if user.plan not in {"pro", "team"}:
        return True, "free_plan"

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


def _preview_profile_response(profile_data: dict, user: User, db: Session) -> AnalyzeProfileResponse:
    usage_stats = get_usage_stats(user, db)
    name, headline = _extract_identity(profile_data)
    return AnalyzeProfileResponse(
        should_contact=True,
        score=72.0,
        reasoning=f"{PREVIEW_BANNER}. Lead: {name} - {headline}",
        usage_remaining=usage_stats["remaining"],
        preview=True,
        message=FREE_COPY,
    )


def _preview_linkedin_response(profile: dict, user: User, message: str) -> AnalyzeLinkedInResponse:
    name, headline = _extract_identity(profile)
    qualification = FitScoringResult(
        overall_score=72.0,
        dimension_scores=DimensionScores(
            seniority_match=70.0,
            industry_match=72.0,
            company_size_match=68.0,
            skills_match=75.0,
            experience_match=70.0,
            engagement_level=65.0,
        ),
        positive_signals=[
            f"Relevant headline: {headline}",
            "Recent role aligns with ICP",
            "Engagement signals look promising",
        ],
        negative_signals=["Preview mode - real AI disabled"],
        data_quality=70.0,
        confidence=55.0,
    )
    ui = AnalyzeLinkedInUI(
        should_contact=True,
        priority="medium",
        score=72.0,
        reasoning=f"{PREVIEW_BANNER}. Lead: {name} - {headline}",
        key_points=[
            "Example signals only",
            "Upgrade to unlock live checks",
            "No usage consumed in preview",
        ],
        suggested_approach="Preview only: upgrade for AI-personalized outreach.",
        red_flags=["Preview result - not AI validated"],
        next_steps="Upgrade to Pro for real-time, AI-powered analysis.",
    )
    return AnalyzeLinkedInResponse(
        qualification=qualification,
        ui=ui,
        plan=user.plan,
        preview=True,
        message=message,
        cache_hit=False,
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
    preview_mode, preview_reason = _determine_preview(current_user, budget_status)
    profile_data = request.linkedin_profile_data or {}

    if preview_mode:
        logger.info(
            "Preview Mode activated for user_id=%d (plan=%s, reason=%s)",
            current_user.id,
            current_user.plan,
            preview_reason,
        )
        return _preview_profile_response(profile_data, current_user, db)

    profile_hash = build_profile_hash(profile_data)
    cached_response = _serve_cached_profile(db, profile_hash)
    if cached_response:
        return cached_response

    # Rate limit and plan cap
    check_usage_limit(current_user, db)

    # Get user's ICP config (if set)
    icp_config = None
    if current_user.icp_config_json:
        icp_config = ICPConfig(**current_user.icp_config_json)

    logger.info("Starting profile analysis for user_id=%d (plan=%s)", current_user.id, current_user.plan)

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
    preview_mode, preview_reason = _determine_preview(current_user, budget_status)
    profile = request.profile_extract or {}

    if preview_mode:
        logger.info(
            "Preview Mode activated for LinkedIn endpoint (user_id=%d, plan=%s, reason=%s)",
            current_user.id,
            current_user.plan,
            preview_reason,
        )
        preview_message = NO_BUDGET_COPY if preview_reason in {"no_subscribers", "no_budget"} else FREE_COPY
        return _preview_linkedin_response(profile, current_user, preview_message)

    profile_hash = build_profile_hash(profile)
    cached_response = _serve_cached_linkedin(db, profile_hash)
    if cached_response:
        return cached_response

    # Rate limit and plan cap
    check_usage_limit(current_user, db)

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

    logger.info("Starting LinkedIn analysis for user_id=%d (plan=%s)", current_user.id, current_user.plan)

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
