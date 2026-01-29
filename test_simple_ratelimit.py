"""Simple rate limit test con servidor existente."""
import os
import requests
import time

BASE_URL = os.getenv("BACKEND_URL", "")

print("="*70)
print("Test de Rate Limiting (30 segundos)")
print("="*70)

# Create user
print("\n1. Creando usuario...")
email = f"test_rlimit_{int(time.time())}@example.com"
data = {"email": email, "password": "pass", "full_name": "Test"}
response = requests.post(f"{BASE_URL}/auth/login", json=data, timeout=30)

if response.status_code != 200:
    print(f"❌ Error creando usuario: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"✅ Usuario creado: {email}")

# First analysis
print("\n2. Primer análisis...")
profile = {"profile_extract": {
    "name": "Test Person",
    "headline": "Software Engineer",
    "about": "Experienced developer with 5 years",
    "current_company": "TechCorp",
    "current_position": "Senior Engineer",
    "location": "San Francisco"
}}

headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/analyze/linkedin", headers=headers, json=profile, timeout=30)

if response.status_code != 200:
    print(f"❌ Primer análisis falló: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

print(f"✅ Primer análisis exitoso")

# Second analysis immediately (should fail with 429)
print("\n3. Segundo análisis inmediatamente (debe fallar con 429)...")
response = requests.post(f"{BASE_URL}/analyze/linkedin", headers=headers, json=profile, timeout=30)

if response.status_code == 429:
    print(f"✅ Rate limit funcionó! Status: 429")
    error_data = response.json()
    print(f"   Mensaje: {error_data.get('detail')}")
elif response.status_code == 500:
    print(f"❌ Error 500! Response: {response.text}")
    print("\n   ESTO INDICA UN BUG EN EL CÓDIGO")
else:
    print(f"❌ Rate limit NO funcionó. Status: {response.status_code}")
    print(f"   Response: {response.text}")

print("\n" + "="*70)
print("Test completado")
print("="*70)
