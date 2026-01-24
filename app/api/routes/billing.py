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

@router.post("/checkout-session", summary="Create Stripe Checkout Session")
def create_checkout_session(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = get_settings()

    if not settings.stripe_api_key or not settings.stripe_price_pro_id:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    stripe.api_key = settings.stripe_api_key

    # Ensure customer exists
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            metadata={"user_id": str(current_user.id)},
        )
        customer_id = customer.id
        current_user.stripe_customer_id = customer_id
        db.add(current_user)
        db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": settings.stripe_price_pro_id, "quantity": 1}],
        customer=customer_id,
        success_url=f"{settings.stripe_success_url}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=settings.stripe_cancel_url,
        client_reference_id=str(current_user.id),
        metadata={"user_id": str(current_user.id)},
    )

    return {"url": session.url}

@router.post("/portal-session", summary="Create Stripe Billing Portal Session")
def create_portal_session(current_user: User = Depends(get_current_user)):
    settings = get_settings()

    if not settings.stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer for user")

    stripe.api_key = settings.stripe_api_key

    portal = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=settings.stripe_success_url,
    )
    return {"url": portal.url}

@router.post("/webhook", summary="Stripe webhook endpoint")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()

    if not settings.stripe_api_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook not configured")

    stripe.api_key = settings.stripe_api_key
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=settings.stripe_webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle relevant event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        plan = session.get("metadata", {}).get("plan", "pro")

        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
        elif customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        else:
            user = None

        if user:
            user.plan = plan
            if customer_id:
                user.stripe_customer_id = customer_id
            if subscription_id:
                user.stripe_subscription_id = subscription_id
            db.add(user)
            db.commit()

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.canceled"):
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        if customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.plan = "free"
                user.stripe_subscription_id = None
                db.add(user)
                db.commit()

    return {"ok": True}

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
        business_price_id=settings.stripe_price_business_id,
    )


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create Stripe checkout session for subscription upgrade",
    description="Requires authentication. Returns sessionId and checkout URL for Starter, Pro, or Business plan.",
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
    - Business: $49/month - 500 analyses/month
    
    After successful payment, a Stripe webhook will update the user's plan.
    """
    if not request.return_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="return_url required")

    plan = request.plan.lower().strip() if request.plan else "pro"
    if plan not in ("starter", "pro", "business"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="plan must be 'starter', 'pro', or 'business'"
        )

    try:
        result = stripe_service.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
            return_url=request.return_url,
            plan=plan,
        )
        return CheckoutResponse(**result)
    except Exception as e:
        logger.error(f"Failed to create checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        logger.warning(f"Webhook signature verification failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle specific events
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        stripe_service.handle_checkout_completed(event_data, db)
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
