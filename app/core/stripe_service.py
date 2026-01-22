"""
Stripe payment service for handling checkouts and subscriptions.
Manages:
- Creating checkout sessions for "Pro" plan upgrade
- Handling webhook events (checkout completed, subscription deleted)
- Syncing user plan status with Stripe
"""

import logging
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.orm import Session
from app.models.user import User

logger = logging.getLogger(__name__)


class StripeService:
    """Service for Stripe payment integration."""

    def __init__(self, api_key: str, webhook_secret: str, pro_price_id: str, team_price_id: Optional[str] = None):
        """
        Initialize Stripe service.
        
        Args:
            api_key: Stripe secret API key
            webhook_secret: Stripe webhook signing secret
            pro_price_id: Stripe price ID for Pro plan ($19/mo - 100 analyses/week)
            team_price_id: Stripe price ID for Team plan ($39/mo - 300 analyses/week)
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret
        self.pro_price_id = pro_price_id
        self.team_price_id = team_price_id

    def create_checkout_session(
        self,
        user_id: str,
        email: str,
        return_url: str,
        plan: str = "pro",
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for Pro or Team plan upgrade.
        
        Args:
            user_id: User ID for metadata
            email: Customer email
            return_url: URL to return to after checkout (include {CHECKOUT_SESSION_ID} placeholder)
                       e.g., "https://example.com/checkout?session_id={CHECKOUT_SESSION_ID}"
            plan: Plan to subscribe to ("pro" or "team")
        
        Returns:
            dict with:
                - sessionId: Stripe checkout session ID
                - url: Direct checkout URL (if customer has no existing subscription)
        
        Raises:
            stripe.error.StripeError: If session creation fails
        """
        # Select price ID based on plan
        if plan == "team" and self.team_price_id:
            price_id = self.team_price_id
        else:
            price_id = self.pro_price_id
            plan = "pro"  # Default to pro if team not configured
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{return_url}&status=success",
                cancel_url=f"{return_url}&status=cancel",
                customer_email=email,
                client_reference_id=user_id,
                metadata={
                    "user_id": user_id,
                    "plan": plan,
                },
            )
            logger.info(f"Created {plan} checkout session {session.id} for user {user_id}")
            return {
                "sessionId": session.id,
                "url": session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session for user {user_id}: {str(e)}")
            raise

    def handle_checkout_completed(
        self,
        session: Dict[str, Any],
        db: Session,
    ) -> Optional[User]:
        """
        Handle checkout.session.completed webhook event.
        Updates user plan based on metadata.plan (pro/team) and saves Stripe IDs.
        """
        user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        plan = session.get("metadata", {}).get("plan", "pro")

        if not user_id:
            logger.warning("Checkout completed but no user_id in metadata")
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Checkout completed for unknown user {user_id}")
            return None

        user.plan = plan
        user.stripe_customer_id = customer_id
        user.stripe_subscription_id = subscription_id
        db.commit()
        
        logger.info(f"Updated user {user_id} to {plan} plan, subscription {subscription_id}")
        return user

    def handle_subscription_deleted(
        self,
        subscription: Dict[str, Any],
        db: Session,
    ) -> Optional[User]:
        """
        Handle customer.subscription.deleted webhook event.
        Reverts user plan to "free" when subscription is cancelled.
        
        Args:
            subscription: Stripe subscription object
            db: Database session
        
        Returns:
            Updated User object, or None if user not found
        """
        customer_id = subscription.get("customer")
        
        # Find user by stripe_customer_id
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.warning(f"Subscription deleted for unknown customer {customer_id}")
            return None

        user.plan = "free"
        db.commit()
        
        logger.info(f"Reverted user {user.id} to free plan, subscription deleted")
        return user

    def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature using signing secret.
        
        Args:
            payload: Raw request body
            signature: Signature header from Stripe (Stripe-Signature)
        
        Returns:
            Parsed event object if signature is valid
        
        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret,
            )
            logger.info(f"Valid Stripe webhook: {event['type']}")
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.warning(f"Invalid webhook signature: {str(e)}")
            raise
