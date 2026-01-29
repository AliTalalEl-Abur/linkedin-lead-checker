#!/usr/bin/env python3
"""Simple test script to verify auth endpoints"""
import sys
import time
import os
import requests

BASE_URL = os.getenv("BACKEND_URL", "")

def wait_for_server():
    """Wait for server to be ready"""
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            return True
        except:
            time.sleep(1)
    return False

def test_login():
    """Test login endpoint"""
    print("🔐 Testing POST /auth/login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "test@example.com"},
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Token received: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"  ❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return None

def test_protected(token):
    """Test protected endpoint"""
    print("\n🔒 Testing GET /me (protected)...")
    try:
        response = requests.get(
            f"{BASE_URL}/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ User data: {data}")
            return True
        else:
            print(f"  ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for server...")
    if not wait_for_server():
        print("❌ Server not responding")
        sys.exit(1)
    
    print("✅ Server ready\n")
    
    token = test_login()
    if token:
        test_protected(token)
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
