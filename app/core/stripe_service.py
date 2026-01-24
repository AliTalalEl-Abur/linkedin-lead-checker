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

    def __init__(self, api_key: str, webhook_secret: str, starter_price_id: Optional[str] = None, pro_price_id: Optional[str] = None, business_price_id: Optional[str] = None):
        """
        Initialize Stripe service.
        
        Args:
            api_key: Stripe secret API key
            webhook_secret: Stripe webhook signing secret
            starter_price_id: Stripe price ID for Starter plan ($9/mo - 40 analyses/month)
            pro_price_id: Stripe price ID for Pro plan ($19/mo - 150 analyses/month)
            business_price_id: Stripe price ID for Business plan ($49/mo - 500 analyses/month)
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret
        self.starter_price_id = starter_price_id
        self.pro_price_id = pro_price_id
        self.business_price_id = business_price_id

    def create_checkout_session(
        self,
        user_id: str,
        email: str,
        return_url: str,
        plan: str = "pro",
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for Starter, Pro or Business plan upgrade.
        
        Args:
            user_id: User ID for metadata
            email: Customer email
            return_url: URL to return to after checkout (include {CHECKOUT_SESSION_ID} placeholder)
                       e.g., "https://example.com/checkout?session_id={CHECKOUT_SESSION_ID}"
            plan: Plan to subscribe to ("starter", "pro", or "business")
        
        Returns:
            dict with:
                - sessionId: Stripe checkout session ID
                - url: Direct checkout URL (if customer has no existing subscription)
        
        Raises:
            stripe.error.StripeError: If session creation fails
        """
        # Select price ID based on plan
        if plan == "starter" and self.starter_price_id:
            price_id = self.starter_price_id
        elif plan == "business" and self.business_price_id:
            price_id = self.business_price_id
        elif plan == "pro" and self.pro_price_id:
            price_id = self.pro_price_id
        else:
            # Default to pro if specified plan not configured
            price_id = self.pro_price_id or self.starter_price_id or self.business_price_id
            if not price_id:
                raise ValueError("No Stripe price IDs configured")
            plan = "pro"
        
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

    def handle_subscription_updated(
        self,
        subscription: Dict[str, Any],
        db: Session,
    ) -> Optional[User]:
        """
        Handle customer.subscription.updated webhook event.
        Updates user plan when subscription changes (upgrades/downgrades).
        
        Args:
            subscription: Stripe subscription object
            db: Database session
        
        Returns:
            Updated User object, or None if user not found
        """
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        status = subscription.get("status")
        
        # Find user by stripe_customer_id
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            logger.warning(f"Subscription updated for unknown customer {customer_id}")
            return None
        
        # If subscription is cancelled or past_due, revert to free
        if status in ["canceled", "unpaid", "past_due"]:
            user.plan = "free"
            logger.info(f"Reverted user {user.id} to free plan, subscription status: {status}")
            db.commit()
            return user
        
        # If subscription is active or trialing, determine plan from price
        if status in ["active", "trialing"]:
            # Get the price ID from subscription items
            items = subscription.get("items", {}).get("data", [])
            if not items:
                logger.warning(f"No subscription items found for {subscription_id}")
                return user
            
            price_id = items[0].get("price", {}).get("id")
            
            # Determine plan based on price_id
            plan = "free"
            if price_id == self.starter_price_id:
                plan = "starter"
            elif price_id == self.pro_price_id:
                plan = "pro"
            elif price_id == self.business_price_id:
                plan = "business"
            else:
                logger.warning(f"Unknown price_id {price_id} for subscription {subscription_id}")
                return user
            
            user.plan = plan
            user.stripe_subscription_id = subscription_id
            logger.info(f"Updated user {user.id} to {plan} plan via subscription update")
            db.commit()
            return user
        
        # For other statuses, log but don't change plan
        logger.info(f"Subscription {subscription_id} status: {status}, no plan change")
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
