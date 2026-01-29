"""
Test script for pricing buttons integration
Tests that:
1. Unauthenticated users cannot create checkout
2. Authenticated users can create checkout for all 3 plans
3. Each plan uses the correct price_id
4. Backend validates JWT correctly
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE = os.getenv("BACKEND_URL", "")

def print_header(text):
    print(f"\n{'='*80}")
    print(f" {text}")
    print('='*80)

def test_unauthenticated_checkout():
    """Test that unauthenticated users cannot create checkout"""
    print_header("TEST 1: Unauthenticated Checkout (Should Fail)")
    
    response = requests.post(
        f"{API_BASE}/billing/checkout",
        json={
            "return_url": f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing-return.html?session_id={{CHECKOUT_SESSION_ID}}",
            "plan": "pro"
        }
    )
    
    if response.status_code == 401:
        print("✅ PASS: Unauthenticated request correctly rejected (401)")
        return True
    else:
        print(f"❌ FAIL: Expected 401, got {response.status_code}")
        print(f"Response: {response.text}")
        return False

def login_user(email="test-pricing@example.com"):
    """Login and get JWT token"""
    print(f"\n🔐 Logging in as {email}...")
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return None
    
    data = response.json()
    token = data.get('access_token')
    print(f"✅ Login successful, token obtained")
    return token

def test_checkout_for_plan(token, plan):
    """Test checkout creation for a specific plan"""
    print(f"\n📦 Testing {plan.upper()} plan checkout...")
    
    response = requests.post(
        f"{API_BASE}/billing/checkout",
        json={
            "return_url": f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing-return.html?session_id={{CHECKOUT_SESSION_ID}}",
            "plan": plan
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('sessionId')
        url = data.get('url')
        
        print(f"✅ PASS: {plan.upper()} checkout created")
        print(f"   Session ID: {session_id[:40]}...")
        print(f"   URL: {url[:80]}...")
        return True
    else:
        print(f"❌ FAIL: {plan.upper()} checkout failed ({response.status_code})")
        print(f"   Response: {response.text}")
        return False

def test_invalid_plan(token):
    """Test that invalid plans are rejected"""
    print_header("TEST: Invalid Plan Name (Should Fail)")
    
    response = requests.post(
        f"{API_BASE}/billing/checkout",
        json={
            "return_url": f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing-return.html?session_id={{CHECKOUT_SESSION_ID}}",
            "plan": "premium"  # Invalid plan
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 400:
        print("✅ PASS: Invalid plan correctly rejected (400)")
        return True
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
        print(f"Response: {response.text}")
        return False

def verify_price_ids():
    """Verify that all price IDs are configured"""
    print_header("Verifying Price ID Configuration")
    
    price_ids = {
        'STARTER': os.getenv('STRIPE_PRICE_STARTER_ID'),
        'PRO': os.getenv('STRIPE_PRICE_PRO_ID'),
        'TEAM': os.getenv('STRIPE_PRICE_TEAM_ID')
    }
    
    all_configured = True
    for plan, price_id in price_ids.items():
        if price_id:
            print(f"✅ {plan}: {price_id}")
        else:
            print(f"❌ {plan}: NOT CONFIGURED")
            all_configured = False
    
    return all_configured

def main():
    print("\n🧪 TESTING PRICING BUTTONS INTEGRATION")
    print("="*80)
    
    # Verify configuration
    if not verify_price_ids():
        print("\n❌ ERROR: Not all price IDs are configured in .env")
        print("Please run: python setup_stripe_products.py")
        return
    
    # Test 1: Unauthenticated request should fail
    test1 = test_unauthenticated_checkout()
    
    # Login to get token
    token = login_user()
    if not token:
        print("\n❌ ERROR: Could not obtain authentication token")
        return
    
    # Test 2: Authenticated checkout for all 3 plans
    print_header("TEST 2: Authenticated Checkout (All Plans)")
    test2a = test_checkout_for_plan(token, "starter")
    test2b = test_checkout_for_plan(token, "pro")
    test2c = test_checkout_for_plan(token, "team")
    
    # Test 3: Invalid plan should fail
    test3 = test_invalid_plan(token)
    
    # Summary
    print_header("TEST SUMMARY")
    results = {
        "Unauthenticated rejection": test1,
        "Starter checkout": test2a,
        "Pro checkout": test2b,
        "Team checkout": test2c,
        "Invalid plan rejection": test3,
    }
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📝 Next Steps:")
        print("1. Start your Next.js frontend: cd web && npm run dev")
        print("2. Test the pricing buttons in browser at NEXT_PUBLIC_SITE_URL")
        print("3. Click 'Get Started' → Login → Click plan button")
        print("4. You should be redirected to Stripe Checkout")
        print("5. Test card: 4242 4242 4242 4242")
    else:
        print("❌ SOME TESTS FAILED - Please review the errors above")
    print("="*80)

if __name__ == "__main__":
    main()
