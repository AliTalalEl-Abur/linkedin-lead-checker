"""
Billing endpoints for checkout and subscription management.
POST /billing/checkout - Create Stripe checkout session
POST /webhook/stripe - Handle Stripe webhook events
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import stripe

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from app.core.stripe_service import StripeService
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    """Request to create a Stripe checkout session."""
    return_url: str  # URL to redirect after checkout (should include {CHECKOUT_SESSION_ID})
    plan: str = "pro"  # "starter", "pro", or "team" - ONLY these values accepted


class CheckoutResponse(BaseModel):
    """Response with Stripe checkout session details."""
    sessionId: str
    url: str


class BillingStatusResponse(BaseModel):
    """Response with user billing status."""
    plan: str
    usage_current: int
    usage_limit: int
    reset_date: str | None
    can_analyze: bool
    subscription_status: str | None


def get_stripe_service() -> StripeService:
    """Get Stripe service instance with config from environment."""
    settings = get_settings()
    return StripeService(
        api_key=settings.stripe_api_key,
        webhook_secret=settings.stripe_webhook_secret,
        starter_price_id=settings.stripe_price_starter_id,
        pro_price_id=settings.stripe_price_pro_id,
        team_price_id=settings.stripe_price_team_id,
    )


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create Stripe checkout session for subscription upgrade",
    description="Requires authentication. Returns sessionId and checkout URL for Starter, Pro, or Team plan.",
    responses={
        200: {"description": "Checkout session created successfully"},
        401: {"description": "Not authenticated"},
        400: {"description": "Invalid request"},
    },
)
def create_checkout_session(
    request: CheckoutRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),  # ✅ SECURITY: JWT authentication required
    db: Session = Depends(get_db),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """
    Create a Stripe checkout session for upgrading to paid plan.
    
    🔒 SECURITY FEATURES:
    - ✅ JWT authentication required (current_user dependency)
    - ✅ Strict plan validation (only: starter, pro, team)
    - ✅ Price ID whitelist validation in StripeService
    - ✅ User metadata attached to Stripe session
    - ✅ All validation errors logged with user context
    
    Plans:
    - Starter: $9/month - 40 analyses/month
    - Pro: $19/month - 150 analyses/month
    - Team: $49/month - 500 analyses/month
    
    After successful payment, a Stripe webhook will update the user's plan.
    
    BLOCKED: Any plan not in the whitelist or invalid price_id.
    """
    request_id = getattr(getattr(http_request, "state", None), "request_id", "unknown")

    # VALIDATION 1: return_url is required
    if not request.return_url:
        logger.warning(
            "CHECKOUT_REJECTED | request_id=%s | user_id=%s | reason=missing_return_url",
            request_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="return_url is required"
        )
    
    # VALIDATION 2: return_url must include {CHECKOUT_SESSION_ID} placeholder
    if "{CHECKOUT_SESSION_ID}" not in request.return_url:
        logger.warning(
            "CHECKOUT_REJECTED | request_id=%s | user_id=%s | reason=invalid_return_url",
            request_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="return_url must include {CHECKOUT_SESSION_ID} placeholder"
        )

    # VALIDATION 3: Strict plan validation (whitelist only)
    plan = request.plan.lower().strip() if request.plan else None
    if not plan:
        logger.warning(
            "CHECKOUT_REJECTED | request_id=%s | user_id=%s | reason=missing_plan",
            request_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="plan is required"
        )
    
    # VALIDATION 4: Plan must be one of the allowed values
    ALLOWED_PLANS = ("starter", "pro", "team")
    if plan not in ALLOWED_PLANS:
        logger.warning(
            "CHECKOUT_REJECTED | request_id=%s | user_id=%s | plan=%s | reason=invalid_plan",
            request_id,
            current_user.id,
            plan,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid plan '{plan}'. Must be one of: {', '.join(ALLOWED_PLANS)}"
        )

    try:
        # VALIDATION 5: StripeService validates price_id whitelist
        # This ensures only configured price_ids from .env are used
        result = stripe_service.create_checkout_session(
            user_id=str(current_user.id),  # Convert to string for Stripe metadata
            email=current_user.email,
            return_url=request.return_url,
            plan=plan,
        )
        
        logger.info(
            "CHECKOUT_SESSION_CREATED | request_id=%s | user_id=%s | plan=%s | session_id=%s | authenticated=true",
            request_id,
            current_user.id,
            plan,
            result.get('sessionId', 'unknown')
        )
        
        return CheckoutResponse(**result)
        
    except ValueError as e:
        # Validation errors (invalid plan, missing price_id, unauthorized price_id)
        logger.error(
            "CHECKOUT_SESSION_FAILED | request_id=%s | user_id=%s | plan=%s | error=%s | type=validation",
            request_id,
            current_user.id,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Checkout validation failed: {str(e)}",
        )
    
    except stripe.error.InvalidRequestError as e:
        # Stripe API errors (invalid price_id, configuration issues)
        logger.error(
            "CHECKOUT_SESSION_FAILED | request_id=%s | user_id=%s | plan=%s | error=%s | type=stripe_invalid",
            request_id,
            current_user.id,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe configuration. Please contact support.",
        )
    
    except stripe.error.StripeError as e:
        # Other Stripe errors (network, authentication, etc.)
        logger.error(
            "CHECKOUT_SESSION_FAILED | request_id=%s | user_id=%s | plan=%s | error=%s | type=stripe_error",
            request_id,
            current_user.id,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service temporarily unavailable. Please try again.",
        )
    
    except Exception as e:
        # Unexpected errors
        logger.error(
            "CHECKOUT_SESSION_FAILED | request_id=%s | user_id=%s | plan=%s | error=%s | type=unexpected",
            request_id,
            current_user.id,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session. Please try again later.",
        )


@router.post(
    "/webhook/stripe",
    summary="Stripe webhook endpoint",
    description="Handles Stripe events (checkout.session.completed, customer.subscription.deleted)",
    responses={
        200: {"description": "Webhook processed"},
        400: {"description": "Invalid signature"},
    },
)
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """
    Handle Stripe webhook events.
    
    Verifies webhook signature using HMAC-SHA256.
    
    Supported Events:
    - checkout.session.completed: User completed payment, activate subscription
    - customer.subscription.created: Subscription created (alternative to checkout)
    - customer.subscription.deleted: Subscription canceled, revert to free
    - customer.subscription.updated: Subscription modified (plan changes, etc.)
    
    All handlers implement idempotency to prevent duplicate processing.
    """
    # Get raw body and signature header
    body = await request.body()
    signature = request.headers.get("stripe-signature")

    request_id = getattr(getattr(request, "state", None), "request_id", "unknown")

    if not signature:
        logger.warning("WEBHOOK_REJECTED | request_id=%s | reason=missing_signature", request_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature")

    try:
        event = stripe_service.verify_webhook_signature(body, signature)
    except Exception as e:
        logger.warning("WEBHOOK_SIGNATURE_INVALID | request_id=%s | error=%s", request_id, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle specific events
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    event_id = event.get("id", "unknown")
    
    logger.info(
        "WEBHOOK_RECEIVED | request_id=%s | event_type=%s | event_id=%s",
        request_id,
        event_type,
        event_id
    )

    if event_type == "checkout.session.completed":
        result = stripe_service.handle_checkout_completed(event_data, db)
        if result:
            logger.info(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | user_id=%s | status=success",
                request_id,
                event_type,
                event_id,
                result.id
            )
        else:
            logger.warning(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | status=failed",
                request_id,
                event_type,
                event_id
            )
        return {"status": "ok", "event": event_type}

    elif event_type == "customer.subscription.created":
        result = stripe_service.handle_subscription_created(event_data, db)
        if result:
            logger.info(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | user_id=%s | status=success",
                request_id,
                event_type,
                event_id,
                result.id
            )
        else:
            logger.warning(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | status=failed",
                request_id,
                event_type,
                event_id
            )
        return {"status": "ok", "event": event_type}

    elif event_type == "customer.subscription.deleted":
        result = stripe_service.handle_subscription_deleted(event_data, db)
        if result:
            logger.info(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | user_id=%s | status=success",
                request_id,
                event_type,
                event_id,
                result.id
            )
        return {"status": "ok", "event": event_type}
    
    elif event_type == "customer.subscription.updated":
        result = stripe_service.handle_subscription_updated(event_data, db)
        if result:
            logger.info(
                "WEBHOOK_PROCESSED | request_id=%s | event_type=%s | event_id=%s | user_id=%s | status=success",
                request_id,
                event_type,
                event_id,
                result.id
            )
        return {"status": "ok", "event": event_type}

    else:
        # Acknowledge but ignore other event types
        logger.info(
            "WEBHOOK_IGNORED | request_id=%s | event_type=%s | event_id=%s | reason=not_handled",
            request_id,
            event_type,
            event_id
        )
        return {"status": "ok", "event": event_type}


@router.get(
    "/status",
    response_model=BillingStatusResponse,
    summary="Get user billing status and usage limits",
    description="Returns current plan, usage, limits, and whether user can perform AI analyses"
)
def get_billing_status(
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BillingStatusResponse:
    """
    Get comprehensive billing status for current user.
    
    Returns:
    - plan: Current plan (free, starter, pro, team)
    - usage_current: Current monthly usage count
    - usage_limit: Monthly usage limit for current plan
    - reset_date: When monthly usage resets (None for free plan)
    - can_analyze: Whether user has analyses remaining
    - subscription_status: Stripe subscription status (active, canceled, etc.)
    """
    settings = get_settings()
    
    # Get usage limits by plan
    usage_limits = {
        "free": settings.usage_limit_free,
        "starter": settings.usage_limit_starter,
        "pro": settings.usage_limit_pro,
        "team": settings.usage_limit_team,
    }
    
    plan = current_user.plan or "free"
    usage_limit = usage_limits.get(plan, settings.usage_limit_free)
    
    # For paid plans, use monthly counter; for free, use lifetime
    if plan == "free":
        usage_current = current_user.lifetime_analyses_count or 0
    else:
        usage_current = current_user.monthly_analyses_count or 0
    
    # Can analyze if under limit
    can_analyze = usage_current < usage_limit
    
    # Format reset date
    reset_date = None
    if current_user.monthly_analyses_reset_at:
        reset_date = current_user.monthly_analyses_reset_at.isoformat()
    
    request_id = getattr(getattr(http_request, "state", None), "request_id", "unknown")
    logger.info(
        "BILLING_STATUS_CHECKED | request_id=%s | user_id=%s | plan=%s | usage=%s/%s | can_analyze=%s | subscription_status=%s",
        request_id,
        current_user.id,
        plan,
        usage_current,
        usage_limit,
        can_analyze,
        current_user.subscription_status
    )
    
    return BillingStatusResponse(
        plan=plan,
        usage_current=usage_current,
        usage_limit=usage_limit,
        reset_date=reset_date,
        can_analyze=can_analyze,
        subscription_status=current_user.subscription_status
    )
