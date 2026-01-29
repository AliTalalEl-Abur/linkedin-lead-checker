"""
Quick test - verifica que el servidor responde
"""
import os
import requests
import time

print("Esperando a que el servidor inicie...")
time.sleep(2)

# Test 1: Health check
try:
    base_url = os.getenv("BACKEND_URL", "")
    response = requests.get(f"{base_url}/health")
    print(f"✅ Health check: {response.status_code}")
    print(f"   {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    exit(1)

# Test 2: Checkout sin auth (debe fallar con 401)
try:
    response = requests.post(
        f"{base_url}/billing/checkout",
        json={"return_url": f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/return", "plan": "pro"}
    )
    if response.status_code == 401:
        print(f"✅ Checkout sin auth: 401 (correcto)")
    else:
        print(f"⚠️  Checkout sin auth: {response.status_code} (esperaba 401)")
except Exception as e:
    print(f"❌ Checkout test failed: {e}")

print("\n✅ Tests básicos completados")
