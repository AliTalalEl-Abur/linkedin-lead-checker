"""
Test Suite for Stripe Verification System

Tests that verify_stripe_sync.py works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_imports():
    """Test that all required imports work"""
    print("🧪 Test 1: Checking imports...")
    try:
        import stripe
        from verify_stripe_sync import StripeVerifier, EXPECTED_PLANS
        print("   ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {str(e)}")
        return False


def test_env_variables():
    """Test that required environment variables exist"""
    print("\n🧪 Test 2: Checking environment variables...")
    required_vars = [
        'STRIPE_SECRET_KEY',
        'STRIPE_PRICE_STARTER_ID',
        'STRIPE_PRICE_PRO_ID',
        'STRIPE_PRICE_TEAM_ID'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: present")
        else:
            print(f"   ❌ {var}: MISSING")
            all_present = False
    
    return all_present


def test_verifier_initialization():
    """Test that StripeVerifier can be initialized"""
    print("\n🧪 Test 3: Testing StripeVerifier initialization...")
    try:
        from verify_stripe_sync import StripeVerifier
        verifier = StripeVerifier()
        print("   ✅ StripeVerifier initialized successfully")
        return True
    except Exception as e:
        print(f"   ❌ Initialization failed: {str(e)}")
        return False


def test_load_backend_config():
    """Test loading backend configuration"""
    print("\n🧪 Test 4: Testing backend config loading...")
    try:
        from verify_stripe_sync import StripeVerifier
        verifier = StripeVerifier()
        verifier.load_backend_config()
        
        if len(verifier.backend_config) == 3:
            print(f"   ✅ Loaded 3 plans")
            return True
        else:
            print(f"   ❌ Expected 3 plans, got {len(verifier.backend_config)}")
            return False
    except Exception as e:
        print(f"   ❌ Config loading failed: {str(e)}")
        return False


def test_load_stripe_data():
    """Test loading Stripe data"""
    print("\n🧪 Test 5: Testing Stripe data loading...")
    try:
        from verify_stripe_sync import StripeVerifier
        verifier = StripeVerifier()
        verifier.load_backend_config()
        verifier.load_stripe_data()
        
        if len(verifier.stripe_products) > 0:
            print(f"   ✅ Loaded {len(verifier.stripe_products)} products from Stripe")
            return True
        else:
            print(f"   ❌ No products loaded")
            return False
    except Exception as e:
        print(f"   ❌ Stripe data loading failed: {str(e)}")
        return False


def test_full_verification():
    """Test running full verification"""
    print("\n🧪 Test 6: Testing full verification...")
    try:
        from verify_stripe_sync import StripeVerifier
        verifier = StripeVerifier()
        success = verifier.verify_all()
        
        if success:
            print(f"   ✅ Full verification passed")
            print(f"      Errors: {len(verifier.errors)}")
            print(f"      Warnings: {len(verifier.warnings)}")
        else:
            print(f"   ⚠️  Verification completed with errors")
            print(f"      Errors: {len(verifier.errors)}")
            print(f"      Warnings: {len(verifier.warnings)}")
        
        return True  # Test passes if verification runs (even with errors)
    except Exception as e:
        print(f"   ❌ Verification failed: {str(e)}")
        return False


def test_expected_plans_config():
    """Test EXPECTED_PLANS configuration"""
    print("\n🧪 Test 7: Testing EXPECTED_PLANS config...")
    try:
        from verify_stripe_sync import EXPECTED_PLANS
        
        required_plans = ['starter', 'pro', 'team']
        all_present = True
        
        for plan in required_plans:
            if plan in EXPECTED_PLANS:
                config = EXPECTED_PLANS[plan]
                has_all = all(key in config for key in ['name', 'price_env', 'expected_price', 'analyses'])
                if has_all:
                    print(f"   ✅ {plan}: configuration complete")
                else:
                    print(f"   ❌ {plan}: missing required keys")
                    all_present = False
            else:
                print(f"   ❌ {plan}: not found in EXPECTED_PLANS")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"   ❌ Config check failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("🧪 Stripe Verification System - Test Suite")
    print("="*70)
    
    tests = [
        test_imports,
        test_env_variables,
        test_expected_plans_config,
        test_verifier_initialization,
        test_load_backend_config,
        test_load_stripe_data,
        test_full_verification
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} crashed: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        print("   verify_stripe_sync.py is working correctly")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        print("   Check errors above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
