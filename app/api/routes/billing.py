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
    plan: str = "pro"  # "starter", "pro", or "business"


class CheckoutResponse(BaseModel):
    """Response with Stripe checkout session details."""
    sessionId: str
    url: str


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """
    Create a Stripe checkout session for upgrading to paid plan.
    
    Plans:
    - Starter: $9/month - 40 analyses/month
    - Pro: $19/month - 150 analyses/month
    - Team: $49/month - 500 analyses/month
    
    After successful payment, a Stripe webhook will update the user's plan.
    
    SECURITY: Only accepts configured price_ids for the three plans above.
    """
    if not request.return_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="return_url required")

    plan = request.plan.lower().strip() if request.plan else "pro"
    if plan not in ("starter", "pro", "team"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid plan. Must be 'starter', 'pro', or 'team'"
        )

    try:
        result = stripe_service.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
            return_url=request.return_url,
            plan=plan,
        )
        logger.info(
            "CHECKOUT_SESSION_CREATED | user_id=%s | email=%s | plan=%s | authenticated=true",
            current_user.id,
            current_user.email,
            plan
        )
        return CheckoutResponse(**result)
    except ValueError as e:
        # Validation errors (invalid plan, missing price_id, etc.)
        logger.error(
            "CHECKOUT_SESSION_FAILED | user_id=%s | email=%s | plan=%s | error=%s | type=validation",
            current_user.id,
            current_user.email,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "CHECKOUT_SESSION_FAILED | user_id=%s | email=%s | plan=%s | error=%s | type=unexpected",
            current_user.id,
            current_user.email,
            plan,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
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
    Processes:
    - checkout.session.completed: Updates user.plan based on metadata (starter/pro/business)
    - customer.subscription.deleted: Reverts user.plan to "free"
    - customer.subscription.updated: Handles upgrades/downgrades between plans
    """
    # Get raw body and signature header
    body = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature")

    try:
        event = stripe_service.verify_webhook_signature(body, signature)
    except Exception as e:
        logger.warning("WEBHOOK_SIGNATURE_INVALID | error=%s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle specific events
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    
    logger.info("WEBHOOK_RECEIVED | event_type=%s", event_type)

    if event_type == "checkout.session.completed":
        stripe_service.handle_checkout_completed(event_data, db)
        logger.info("WEBHOOK_PROCESSED | event_type=%s | status=success", event_type)
        return {"status": "ok", "event": event_type}

    elif event_type == "customer.subscription.deleted":
        stripe_service.handle_subscription_deleted(event_data, db)
        return {"status": "ok", "event": event_type}
    
    elif event_type == "customer.subscription.updated":
        stripe_service.handle_subscription_updated(event_data, db)
        return {"status": "ok", "event": event_type}

    else:
        # Acknowledge but ignore other event types
        logger.info(f"Ignoring Stripe event: {event_type}")
        return {"status": "ok", "event": event_type}
