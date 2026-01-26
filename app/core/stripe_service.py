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

    def __init__(self, api_key: str, webhook_secret: str, starter_price_id: Optional[str] = None, pro_price_id: Optional[str] = None, team_price_id: Optional[str] = None):
        """
        Initialize Stripe service.
        
        Args:
            api_key: Stripe secret API key
            webhook_secret: Stripe webhook signing secret
            starter_price_id: Stripe price ID for Starter plan ($9/mo - 40 analyses/month)
            pro_price_id: Stripe price ID for Pro plan ($19/mo - 150 analyses/month)
            team_price_id: Stripe price ID for Team plan ($49/mo - 500 analyses/month)
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret
        self.starter_price_id = starter_price_id
        self.pro_price_id = pro_price_id
        self.team_price_id = team_price_id
        
        # Build whitelist of allowed price IDs (SECURITY: Anti-fraud protection)
        self.allowed_price_ids = {
            starter_price_id: "starter",
            pro_price_id: "pro",
            team_price_id: "team",
        }
        # Remove None values
        self.allowed_price_ids = {k: v for k, v in self.allowed_price_ids.items() if k is not None}
        
        # Reverse mapping: plan -> price_id
        self.plan_to_price_id = {
            "starter": starter_price_id,
            "pro": pro_price_id,
            "team": team_price_id,
        }
        
        logger.info(
            "StripeService initialized | allowed_price_ids=%s | plans=%s",
            list(self.allowed_price_ids.keys()),
            list(self.plan_to_price_id.keys())
        )
    
    def validate_price_id(self, price_id: str) -> str:
        """
        Validate that a price_id is in the allowed whitelist.
        
        Args:
            price_id: Stripe price ID to validate
        
        Returns:
            Plan name ("starter", "pro", or "team")
        
        Raises:
            ValueError: If price_id is not allowed
        """
        if price_id not in self.allowed_price_ids:
            logger.error(
                "SECURITY_VIOLATION | Attempted to use unauthorized price_id=%s | allowed_ids=%s",
                price_id,
                list(self.allowed_price_ids.keys())
            )
            raise ValueError(
                f"Invalid price_id. Only the following prices are accepted: "
                f"{', '.join(self.allowed_price_ids.keys())}"
            )
        
        plan = self.allowed_price_ids[price_id]
        logger.info("PRICE_VALIDATED | price_id=%s | plan=%s", price_id, plan)
        return plan
    
    def get_price_id_for_plan(self, plan: str) -> str:
        """
        Get the price_id for a given plan.
        
        Args:
            plan: Plan name ("starter", "pro", or "team")
        
        Returns:
            Stripe price ID
        
        Raises:
            ValueError: If plan is invalid or price_id not configured
        """
        if plan not in self.plan_to_price_id:
            raise ValueError(f"Invalid plan '{plan}'. Must be: starter, pro, or team")
        
        price_id = self.plan_to_price_id[plan]
        if not price_id:
            raise ValueError(f"Price ID not configured for plan '{plan}'")
        
        return price_id

    def create_checkout_session(
        self,
        user_id: str,
        email: str,
        return_url: str,
        plan: str = "pro",
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for Starter, Pro or Team plan upgrade.
        
        Args:
            user_id: User ID for metadata
            email: Customer email
            return_url: URL to return to after checkout (include {CHECKOUT_SESSION_ID} placeholder)
                       e.g., "https://example.com/checkout?session_id={CHECKOUT_SESSION_ID}"
            plan: Plan to subscribe to ("starter", "pro", or "team")
        
        Returns:
            dict with:
                - sessionId: Stripe checkout session ID
                - url: Direct checkout URL (if customer has no existing subscription)
        
        Raises:
            stripe.error.StripeError: If session creation fails
            ValueError: If plan is invalid or not configured
        """
        # SECURITY: Validate plan name
        plan = plan.lower().strip()
        if plan not in ["starter", "pro", "team"]:
            logger.error(
                "CHECKOUT_FAILED | user_id=%s | plan=%s | error=invalid_plan",
                user_id,
                plan
            )
            raise ValueError(f"Invalid plan '{plan}'. Must be: starter, pro, or team")
        
        # SECURITY: Get validated price_id for plan
        try:
            price_id = self.get_price_id_for_plan(plan)
        except ValueError as e:
            logger.error(
                "CHECKOUT_FAILED | user_id=%s | plan=%s | error=%s",
                user_id,
                plan,
                str(e)
            )
            raise
        
        # SECURITY: Double-check price_id is in whitelist
        try:
            validated_plan = self.validate_price_id(price_id)
            if validated_plan != plan:
                logger.error(
                    "CHECKOUT_FAILED | user_id=%s | plan_mismatch=%s!=%s",
                    user_id,
                    plan,
                    validated_plan
                )
                raise ValueError(f"Plan validation mismatch: {plan} != {validated_plan}")
        except ValueError as e:
            logger.error(
                "CHECKOUT_FAILED | user_id=%s | plan=%s | error=%s",
                user_id,
                plan,
                str(e)
            )
            raise
        
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
            logger.info(
                "CHECKOUT_STARTED | user_id=%s | email=%s | plan=%s | session_id=%s | price_id=%s",
                user_id,
                email,
                plan,
                session.id,
                price_id
            )
            return {
                "sessionId": session.id,
                "url": session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(
                "CHECKOUT_FAILED | user_id=%s | plan=%s | error=%s",
                user_id,
                plan,
                str(e)
            )
            raise

    def handle_checkout_completed(
        self,
        session: Dict[str, Any],
        db: Session,
    ) -> Optional[User]:
        """
        Handle checkout.session.completed webhook event.
        Updates user plan based on validated price_id from subscription.
        
        SECURITY: Validates price_id against whitelist to prevent unauthorized plans.
        """
        user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        plan_from_metadata = session.get("metadata", {}).get("plan")

        if not user_id:
            logger.warning("CHECKOUT_COMPLETED | ERROR: no user_id in metadata")
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("CHECKOUT_COMPLETED | ERROR: user_id=%s not found", user_id)
            return None
        
        # SECURITY: Fetch subscription to get actual price_id paid
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            items = subscription.get("items", {}).get("data", [])
            
            if not items:
                logger.error(
                    "CHECKOUT_COMPLETED | ERROR: No subscription items | user_id=%s | subscription_id=%s",
                    user_id,
                    subscription_id
                )
                return None
            
            # Get actual price_id that was paid
            actual_price_id = items[0].get("price", {}).get("id")
            
            if not actual_price_id:
                logger.error(
                    "CHECKOUT_COMPLETED | ERROR: No price_id in subscription | user_id=%s",
                    user_id
                )
                return None
            
            # SECURITY: Validate price_id is authorized
            try:
                validated_plan = self.validate_price_id(actual_price_id)
            except ValueError as e:
                logger.error(
                    "CHECKOUT_COMPLETED | SECURITY_VIOLATION | user_id=%s | unauthorized_price_id=%s | error=%s",
                    user_id,
                    actual_price_id,
                    str(e)
                )
                # Revert to free plan if unauthorized price detected
                user.plan = "free"
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                db.commit()
                return user
            
            # SECURITY: Verify metadata plan matches actual price
            if plan_from_metadata and plan_from_metadata != validated_plan:
                logger.warning(
                    "CHECKOUT_COMPLETED | PLAN_MISMATCH | user_id=%s | metadata_plan=%s | actual_plan=%s | using_actual",
                    user_id,
                    plan_from_metadata,
                    validated_plan
                )
            
            # Use validated plan from actual price_id
            user.plan = validated_plan
            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            db.commit()
            
            logger.info(
                "CHECKOUT_COMPLETED | user_id=%s | email=%s | plan=%s | price_id=%s | customer_id=%s | subscription_id=%s | validated=true",
                user_id,
                user.email,
                validated_plan,
                actual_price_id,
                customer_id,
                subscription_id
            )
            return user
            
        except stripe.error.StripeError as e:
            logger.error(
                "CHECKOUT_COMPLETED | ERROR: Failed to fetch subscription | user_id=%s | subscription_id=%s | error=%s",
                user_id,
                subscription_id,
                str(e)
            )
            return None

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
            logger.warning("SUBSCRIPTION_DELETED | ERROR: customer_id=%s not found", customer_id)
            return None

        old_plan = user.plan
        user.plan = "free"
        db.commit()
        
        logger.info(
            "SUBSCRIPTION_DELETED | user_id=%s | email=%s | previous_plan=%s | customer_id=%s",
            user.id,
            user.email,
            old_plan,
            customer_id
        )
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
            
            # SECURITY: Validate price_id against whitelist
            try:
                plan = self.validate_price_id(price_id)
            except ValueError as e:
                logger.error(
                    "SUBSCRIPTION_UPDATED | SECURITY_VIOLATION | user_id=%s | unauthorized_price_id=%s | error=%s | reverting_to_free",
                    user.id,
                    price_id,
                    str(e)
                )
                # Revert to free if unauthorized price detected
                user.plan = "free"
                db.commit()
                return user
            
            user.plan = plan
            user.stripe_subscription_id = subscription_id
            logger.info(
                "SUBSCRIPTION_ACTIVATED | user_id=%s | email=%s | plan=%s | subscription_id=%s | status=%s | price_id=%s | validated=true",
                user.id,
                user.email,
                plan,
                subscription_id,
                status,
                price_id
            )
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
