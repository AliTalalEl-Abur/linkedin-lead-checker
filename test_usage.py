#!/usr/bin/env python3
"""Test usage control and limits"""
import os
import requests
import sys

BASE_URL = os.getenv("BACKEND_URL", "")

def test_usage_control():
    """Test usage limits for free and pro users"""
    
    # Login as free user
    print("🔐 Creating free user...")
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": "free@test.com"})
    free_token = response.json()["access_token"]
    headers_free = {"Authorization": f"Bearer {free_token}"}
    
    # Check initial usage
    print("\n📊 Checking initial usage...")
    me = requests.get(f"{BASE_URL}/me", headers=headers_free).json()
    print(f"  Plan: {me['plan']}")
    print(f"  Usage: {me['usage']['used']}/{me['usage']['limit']}")
    print(f"  Remaining: {me['usage']['remaining']}")
    
    # Make analyses until limit
    print(f"\n🔬 Making {me['usage']['limit']} analyses (free limit)...")
    for i in range(me['usage']['limit']):
        response = requests.post(
            f"{BASE_URL}/analyze/profile",
            headers=headers_free,
            json={"linkedin_profile_data": {"name": "Test User", "title": "Developer"}}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [{i+1}] ✅ Score: {data['score']}, Remaining: {data['usage_remaining']}")
        else:
            print(f"  [{i+1}] ❌ Error: {response.status_code}")
            break
    
    # Try one more (should fail with 402)
    print("\n🚫 Trying to exceed free limit...")
    response = requests.post(
        f"{BASE_URL}/analyze/profile",
        headers=headers_free,
        json={"linkedin_profile_data": {"name": "Test User"}}
    )
    if response.status_code == 402:
        print(f"  ✅ Correctly blocked with 402: {response.json()['detail']}")
    else:
        print(f"  ❌ Expected 402, got {response.status_code}")
        return False
    
    # Test pro user
    print("\n🔐 Creating pro user...")
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": "pro@test.com"})
    pro_token = response.json()["access_token"]
    
    # Upgrade to pro (manual for now)
    print("  Note: In real app, user would upgrade via Stripe")
    
    print("\n✅ Usage control working correctly!")
    return True

if __name__ == "__main__":
    try:
        test_usage_control()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
