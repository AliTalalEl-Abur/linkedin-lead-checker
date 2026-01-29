"""
Quick script to test API endpoints after deployment
"""
import os
import requests
import json

BASE_URL = os.getenv("BACKEND_URL", "")

def test_endpoint(method, path, description):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=10)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} {method} {path}")
        print(f"   Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"   Error: {response.text[:200]}")
        else:
            print(f"   Response: {response.text[:200]}")
        print()
        return response.status_code < 400
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {path}")
        print(f"   Error: {str(e)}")
        print()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Testing API Endpoints")
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    print()
    
    # Test endpoints
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/v1/health", "Health check (versioned)"),
        ("POST", "/auth/login", "Login (without credentials)"),
        ("POST", "/api/v1/auth/login", "Login (versioned)"),
        ("GET", "/billing/status", "Billing status (should 401)"),
        ("GET", "/api/v1/billing/status", "Billing status versioned (should 401)"),
    ]
    
    results = []
    for method, path, desc in endpoints:
        success = test_endpoint(method, path, desc)
        results.append((desc, success))
    
    print("="*60)
    print("Summary:")
    print("="*60)
    for desc, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {desc}")
