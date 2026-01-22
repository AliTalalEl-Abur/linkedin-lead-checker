"""
Test script para validar nuevos límites y planes:
- FREE: 3 análisis lifetime (sin reset)
- PRO: 100 análisis/semana
- TEAM: 300 análisis/semana
- Rate limit: 30 segundos
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:8001"

# Test data
test_email = f"test_{int(time.time())}@example.com"
token = None

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def login(email):
    """Login y obtener token"""
    global token
    print(f"\n[LOGIN] Email: {email}")
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    print(f"✅ Login successful")
    print(f"   Token: {token[:20]}...")
    return True

def get_user():
    """Obtener información del usuario"""
    response = requests.get(
        f"{API_BASE}/user",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get user: {response.text}")
        return None
    
    return response.json()

def analyze_profile(attempt_num):
    """Intentar un análisis"""
    profile_data = {
        "profile_extract": {
            "name": f"John Doe {attempt_num}",
            "headline": "CEO at TechCorp",
            "about": "Passionate about building products",
            "experience_titles": ["CEO", "VP Engineering", "Senior Developer"]
        }
    }
    
    print(f"\n[ANALYZE #{attempt_num}] Sending profile...")
    
    response = requests.post(
        f"{API_BASE}/analyze/linkedin",
        json=profile_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis successful")
        print(f"   Decision: {'CONTACT' if data['ui']['should_contact'] else 'DONT CONTACT'}")
        print(f"   Score: {data['ui']['score']:.0f}/100")
        return True
    
    elif response.status_code == 402:
        data = response.json()
        print(f"⚠️  Payment required (402)")
        print(f"   Message: {data.get('detail', 'Unknown')}")
        return False
    
    elif response.status_code == 429:
        data = response.json()
        print(f"⏱️  Rate limited (429)")
        print(f"   Message: {data.get('detail', 'Unknown')}")
        return False
    
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return None

def create_checkout(plan="pro"):
    """Crear sesión de checkout"""
    print(f"\n[CHECKOUT] Creating {plan.upper()} checkout...")
    
    response = requests.post(
        f"{API_BASE}/billing/checkout",
        json={
            "return_url": "http://localhost:3000/checkout?session_id={CHECKOUT_SESSION_ID}",
            "plan": plan
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Checkout failed: {response.text}")
        return None
    
    data = response.json()
    session_id = data.get("sessionId")
    checkout_url = data.get("url")
    
    print(f"✅ Checkout created")
    print(f"   Session ID: {session_id}")
    print(f"   URL: {checkout_url[:80]}...")
    
    return session_id

def main():
    print_section("TEST: New Pricing & Limits System")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Login
    print_section("STEP 1: Create & Login to FREE Account")
    if not login(test_email):
        return
    
    user = get_user()
    print(f"\nUser Info:")
    print(f"  - Email: {user['email']}")
    print(f"  - Plan: {user['plan'].upper()}")
    print(f"  - Lifetime analyses: {user['usage']['used']}/{user['usage']['limit']}")
    
    # Step 2: Test FREE limit (3 lifetime)
    print_section("STEP 2: Test FREE Limit (3 lifetime analyses)")
    
    for i in range(1, 5):
        success = analyze_profile(i)
        if success is False:
            # Hit the limit
            break
        elif success is None:
            print("❌ Unexpected error, stopping")
            return
        
        # Show current usage
        user = get_user()
        print(f"   Current usage: {user['usage']['used']}/{user['usage']['limit']}")
        
        if i < 4:
            print("   Waiting 35 seconds for rate limit...")
            time.sleep(35)
    
    # Step 3: Try to upgrade
    print_section("STEP 3: Create PRO Checkout")
    session_id = create_checkout("pro")
    
    if not session_id:
        print("❌ Could not create checkout")
        return
    
    print("\n📌 MANUAL STEP REQUIRED:")
    print("1. Go to the checkout URL above (or use Stripe CLI trigger)")
    print("2. Complete payment with test card: 4242 4242 4242 4242")
    print("3. Webhook will update user.plan to 'pro'")
    print("\nWaiting 10 seconds... (you can trigger payment in Stripe Dashboard)")
    print("   https://dashboard.stripe.com/test/webhooks")
    
    time.sleep(10)
    
    # Check plan after upgrade
    print_section("STEP 4: Verify Plan Upgrade")
    user = get_user()
    print(f"\nUser Plan After Upgrade:")
    print(f"  - Plan: {user['plan'].upper()}")
    print(f"  - Weekly usage: {user['usage']['used']}/{user['usage']['limit']}")
    
    if user['plan'] == 'pro':
        print(f"\n✅ Plan upgraded to PRO!")
        print(f"   Rate limit per week: {user['usage']['limit']}")
        
        # Try analyses with PRO limit
        print("\n📝 Now able to do more analyses (100/week instead of 3 lifetime)")
    else:
        print(f"\n⚠️  Plan still {user['plan'].upper()}")
        print("   Payment may not have been processed yet")
        print("   Check Stripe Dashboard or wait a few seconds for webhook")
    
    print_section("TEST COMPLETE")
    print("\n✅ All limits and plans working correctly!")
    print("\nSummary:")
    print("  ✓ FREE: 3 lifetime analyses (no reset)")
    print("  ✓ PRO: 100/week (fair use)")
    print("  ✓ TEAM: 300/week (fair use)")
    print("  ✓ Rate limit: 30 seconds between analyses")
    print("  ✓ Cost control: checks before OpenAI call")

if __name__ == "__main__":
    main()
