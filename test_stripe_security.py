"""
Test script para verificar las validaciones anti-fraude de Stripe.

Este script prueba:
1. Validación de price_ids permitidos
2. Rechazo de price_ids no autorizados
3. Validación de planes
4. Mapeo correcto de price_id a plan
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.stripe_service import StripeService

load_dotenv()

def test_stripe_security():
    """Test Stripe security validations."""
    
    print("="*80)
    print("🔒 Testing Stripe Security Validations")
    print("="*80)
    print()
    
    # Initialize service
    settings_dict = {
        'api_key': os.getenv("STRIPE_SECRET_KEY"),
        'webhook_secret': os.getenv("STRIPE_WEBHOOK_SECRET"),
        'starter_price_id': os.getenv("STRIPE_PRICE_STARTER_ID"),
        'pro_price_id': os.getenv("STRIPE_PRICE_PRO_ID"),
        'team_price_id': os.getenv("STRIPE_PRICE_TEAM_ID"),
    }
    
    if not settings_dict['api_key']:
        print("❌ STRIPE_SECRET_KEY not found in .env")
        return False
    
    stripe_service = StripeService(**settings_dict)
    
    print("✅ StripeService initialized")
    print(f"   Allowed price IDs: {len(stripe_service.allowed_price_ids)}")
    print()
    
    # Test 1: Validate allowed price_ids
    print("📋 Test 1: Validating Allowed Price IDs")
    print("-" * 80)
    
    for price_id, expected_plan in stripe_service.allowed_price_ids.items():
        try:
            plan = stripe_service.validate_price_id(price_id)
            if plan == expected_plan:
                print(f"✅ {price_id} → {plan}")
            else:
                print(f"❌ {price_id} → Expected {expected_plan}, got {plan}")
                return False
        except Exception as e:
            print(f"❌ {price_id} → Error: {e}")
            return False
    
    print()
    
    # Test 2: Reject unauthorized price_ids
    print("🚫 Test 2: Rejecting Unauthorized Price IDs")
    print("-" * 80)
    
    fake_price_ids = [
        "price_1SrkwsPc1lhDefcv1sbYqMeG",  # Old $9.99 price
        "price_1SRzEpPc1lhDefcvbT1byOEA",  # Old Plus $12
        "price_1SRzEoPc1lhDefcvXD8Swmh1",  # Old Base $8
        "price_1SrmCwPc1lhDefcvdBqLWlbL",  # Old Team $39
        "price_fake123456789",  # Completely fake
    ]
    
    for fake_price_id in fake_price_ids:
        try:
            plan = stripe_service.validate_price_id(fake_price_id)
            print(f"❌ {fake_price_id} → SHOULD HAVE BEEN REJECTED but got {plan}")
            return False
        except ValueError as e:
            print(f"✅ {fake_price_id} → Rejected correctly")
        except Exception as e:
            print(f"⚠️  {fake_price_id} → Unexpected error: {e}")
            return False
    
    print()
    
    # Test 3: Plan to price_id mapping
    print("🗺️  Test 3: Plan to Price ID Mapping")
    print("-" * 80)
    
    for plan in ["starter", "pro", "team"]:
        try:
            price_id = stripe_service.get_price_id_for_plan(plan)
            if price_id:
                print(f"✅ {plan} → {price_id}")
            else:
                print(f"⚠️  {plan} → Not configured")
        except ValueError as e:
            print(f"❌ {plan} → Error: {e}")
            return False
    
    print()
    
    # Test 4: Invalid plans
    print("🚫 Test 4: Rejecting Invalid Plans")
    print("-" * 80)
    
    invalid_plans = ["business", "plus", "base", "premium", "fake"]
    
    for invalid_plan in invalid_plans:
        try:
            price_id = stripe_service.get_price_id_for_plan(invalid_plan)
            print(f"❌ {invalid_plan} → SHOULD HAVE BEEN REJECTED but got {price_id}")
            return False
        except ValueError:
            print(f"✅ {invalid_plan} → Rejected correctly")
        except Exception as e:
            print(f"⚠️  {invalid_plan} → Unexpected error: {e}")
            return False
    
    print()
    
    # Test 5: Whitelist verification
    print("🔍 Test 5: Whitelist Integrity")
    print("-" * 80)
    
    expected_plans = {"starter", "pro", "team"}
    actual_plans = set(stripe_service.allowed_price_ids.values())
    
    if actual_plans == expected_plans:
        print(f"✅ Whitelist contains exactly expected plans: {expected_plans}")
    else:
        print(f"❌ Whitelist mismatch!")
        print(f"   Expected: {expected_plans}")
        print(f"   Actual: {actual_plans}")
        return False
    
    # Check no None values
    if None in stripe_service.allowed_price_ids:
        print("❌ Whitelist contains None price_id")
        return False
    else:
        print("✅ Whitelist has no None values")
    
    print()
    
    # Summary
    print("="*80)
    print("📊 Test Summary")
    print("="*80)
    print()
    print("✅ All security validations passed!")
    print()
    print("🔒 Security Features Verified:")
    print("   ✅ Only 3 price_ids accepted (Starter, Pro, Team)")
    print("   ✅ Old price_ids rejected ($9.99, $12, $8, $39)")
    print("   ✅ Fake price_ids rejected")
    print("   ✅ Invalid plans rejected")
    print("   ✅ Plan-to-price mapping works correctly")
    print("   ✅ Price-to-plan validation works correctly")
    print()
    print("🛡️  Anti-fraud protection: ACTIVE")
    print()
    
    return True


if __name__ == "__main__":
    success = test_stripe_security()
    sys.exit(0 if success else 1)
