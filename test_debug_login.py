"""Debug login endpoint."""
import requests
import traceback

BASE_URL = "http://127.0.0.1:8001"

try:
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Health: {response.status_code} - {response.json()}")
    
    print("\nTesting login endpoint...")
    data = {
        "email": "test_debug@example.com",
        "password": "TestPass123!",
        "full_name": "Debug User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data, timeout=30)
    print(f"Login status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        print(f"Success! Token: {response.json()}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
