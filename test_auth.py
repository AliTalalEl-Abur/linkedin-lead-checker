import requests

# Test login endpoint
print("🔐 Testing POST /auth/login...")
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "test@example.com"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

if response.status_code == 200:
    token = response.json()["access_token"]
    
    # Test protected endpoint
    print("🔒 Testing GET /me (protected endpoint)...")
    me_response = requests.get(
        "http://localhost:8000/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {me_response.status_code}")
    print(f"Response: {me_response.json()}\n")
    
    print("✅ Authentication working!")
else:
    print("❌ Login failed")
