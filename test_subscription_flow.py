"""
Subscription Flow Testing Utility

Helps verify that subscription purchases work correctly.
Use this after manually purchasing a subscription through Stripe Checkout.
"""

import os
import sys
from dotenv import load_dotenv
import stripe
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment
load_dotenv()

# Stripe setup
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Database setup
try:
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select
except ImportError:
    print("⚠️  Warning: Could not import database models")
    print("   This script requires the backend app to be importable")
    SessionLocal = None
    User = None


def check_stripe_subscription(email: str):
    """Check subscription status in Stripe for an email"""
    print(f"\n🔍 Checking Stripe for customer: {email}")
    print("="*70)
    
    # Find customer
    customers = stripe.Customer.list(email=email, limit=10)
    
    if not customers.data:
        print(f"❌ No customer found with email: {email}")
        return None
    
    customer = customers.data[0]
    print(f"✅ Customer found:")
    print(f"   • ID: {customer.id}")
    print(f"   • Email: {customer.email}")
    print(f"   • Created: {datetime.fromtimestamp(customer.created).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get subscriptions
    subscriptions = stripe.Subscription.list(customer=customer.id, limit=10)
    
    if not subscriptions.data:
        print(f"\n⚠️  No subscriptions found for this customer")
        return None
    
    print(f"\n📋 Subscriptions ({len(subscriptions.data)}):")
    
    for i, sub in enumerate(subscriptions.data, 1):
        print(f"\n   Subscription {i}:")
        print(f"   • ID: {sub.id}")
        print(f"   • Status: {sub.status}")
        print(f"   • Current Period: {datetime.fromtimestamp(sub.current_period_start).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d')}")
        
        if sub.items and sub.items.data:
            for item in sub.items.data:
                price = item.price
                print(f"   • Price ID: {price.id}")
                print(f"   • Amount: ${price.unit_amount/100:.2f}/{price.recurring.interval}")
                
                # Identify plan
                if price.id == os.getenv('STRIPE_PRICE_STARTER_ID'):
                    print(f"   • Plan: ⭐ Starter")
                elif price.id == os.getenv('STRIPE_PRICE_PRO_ID'):
                    print(f"   • Plan: 💎 Pro")
                elif price.id == os.getenv('STRIPE_PRICE_TEAM_ID'):
                    print(f"   • Plan: 👥 Team")
                else:
                    print(f"   • Plan: ❓ Unknown")
    
    return customer.id, subscriptions.data


def check_database_user(email: str):
    """Check user status in database"""
    print(f"\n🗄️  Checking Database for user: {email}")
    print("="*70)
    
    if not SessionLocal or not User:
        print("❌ Database models not available")
        return None
    
    try:
        db = SessionLocal()
        
        # Find user
        stmt = select(User).where(User.email == email)
        user = db.execute(stmt).scalar_one_or_none()
        
        if not user:
            print(f"❌ No user found with email: {email}")
            db.close()
            return None
        
        print(f"✅ User found:")
        print(f"   • ID: {user.id}")
        print(f"   • Email: {user.email}")
        print(f"   • Plan: {user.plan or 'free'}")
        print(f"   • Stripe Customer ID: {user.stripe_customer_id or 'None'}")
        print(f"   • Stripe Subscription ID: {user.stripe_subscription_id or 'None'}")
        print(f"   • Analyses Used: {user.analyses_used}/{user.analyses_limit}")
        print(f"   • Subscription Status: {user.subscription_status or 'None'}")
        
        if user.subscription_end_date:
            print(f"   • Subscription End: {user.subscription_end_date.strftime('%Y-%m-%d')}")
        
        db.close()
        return user
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return None


def verify_subscription(email: str):
    """Complete verification of subscription flow"""
    print("\n" + "="*70)
    print("🧪 SUBSCRIPTION FLOW VERIFICATION")
    print("="*70)
    print(f"\nTesting email: {email}")
    
    # Step 1: Check Stripe
    stripe_result = check_stripe_subscription(email)
    
    # Step 2: Check Database
    db_user = check_database_user(email)
    
    # Step 3: Compare and validate
    print("\n" + "="*70)
    print("📊 VERIFICATION RESULTS")
    print("="*70)
    
    issues = []
    
    # Check if customer exists in Stripe
    if not stripe_result:
        issues.append("❌ No customer found in Stripe")
    else:
        customer_id, subscriptions = stripe_result
        
        # Check if subscription is active
        active_subs = [s for s in subscriptions if s.status == 'active']
        if not active_subs:
            issues.append("⚠️  No active subscriptions in Stripe")
        else:
            print(f"✅ Stripe: {len(active_subs)} active subscription(s)")
    
    # Check if user exists in database
    if not db_user:
        issues.append("❌ User not found in database")
    else:
        print(f"✅ Database: User exists")
        
        # Check if subscription info is synced
        if not db_user.stripe_customer_id:
            issues.append("⚠️  Database: Missing stripe_customer_id")
        else:
            print(f"✅ Database: Has stripe_customer_id")
        
        if not db_user.stripe_subscription_id:
            issues.append("⚠️  Database: Missing stripe_subscription_id")
        else:
            print(f"✅ Database: Has stripe_subscription_id")
        
        if db_user.plan == 'free' or not db_user.plan:
            issues.append("⚠️  Database: User still on 'free' plan")
        else:
            print(f"✅ Database: User on '{db_user.plan}' plan")
        
        # Check limits
        expected_limits = {
            'starter': 40,
            'pro': 150,
            'team': 500
        }
        
        if db_user.plan in expected_limits:
            expected_limit = expected_limits[db_user.plan]
            if db_user.analyses_limit != expected_limit:
                issues.append(f"⚠️  Database: Incorrect limit (expected {expected_limit}, got {db_user.analyses_limit})")
            else:
                print(f"✅ Database: Correct analyses limit ({db_user.analyses_limit})")
    
    # Compare Stripe and Database
    if stripe_result and db_user:
        customer_id, subscriptions = stripe_result
        
        if db_user.stripe_customer_id != customer_id:
            issues.append("⚠️  Customer ID mismatch between Stripe and Database")
        else:
            print(f"✅ Sync: Customer ID matches")
        
        # Check subscription ID
        active_subs = [s for s in subscriptions if s.status == 'active']
        if active_subs:
            stripe_sub_id = active_subs[0].id
            if db_user.stripe_subscription_id != stripe_sub_id:
                issues.append("⚠️  Subscription ID mismatch between Stripe and Database")
            else:
                print(f"✅ Sync: Subscription ID matches")
    
    # Final result
    print("\n" + "="*70)
    if not issues:
        print("🎉 ALL CHECKS PASSED!")
        print("   Subscription flow is working correctly")
        return True
    else:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Possible causes:")
        print("   • Webhook not received yet (wait a few seconds)")
        print("   • Webhook endpoint not configured")
        print("   • Webhook handler has errors")
        print("   • Database sync issue")
        return False


def list_recent_checkouts():
    """List recent checkout sessions"""
    print("\n" + "="*70)
    print("🛒 Recent Checkout Sessions")
    print("="*70)
    
    sessions = stripe.checkout.Session.list(limit=10)
    
    if not sessions.data:
        print("No recent checkout sessions found")
        return
    
    for i, session in enumerate(sessions.data, 1):
        print(f"\n{i}. Checkout Session:")
        print(f"   • ID: {session.id}")
        print(f"   • Status: {session.status}")
        print(f"   • Email: {session.customer_email or session.customer_details.email if session.customer_details else 'N/A'}")
        print(f"   • Amount: ${session.amount_total/100:.2f}")
        print(f"   • Created: {datetime.fromtimestamp(session.created).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if session.subscription:
            print(f"   • Subscription: {session.subscription}")


def interactive_test():
    """Interactive testing mode"""
    print("\n" + "="*70)
    print("🧪 Subscription Flow Testing")
    print("="*70)
    print("\nOptions:")
    print("1. Verify subscription for an email")
    print("2. List recent checkout sessions")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        email = input("\nEnter email to verify: ").strip()
        if email:
            verify_subscription(email)
        else:
            print("❌ Email is required")
    
    elif choice == "2":
        list_recent_checkouts()
    
    elif choice == "3":
        print("\n👋 Goodbye!")
        return False
    
    else:
        print("❌ Invalid option")
    
    return True


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode
        email = sys.argv[1]
        verify_subscription(email)
    else:
        # Interactive mode
        while interactive_test():
            input("\nPress Enter to continue...")
            print("\n")


if __name__ == "__main__":
    main()
