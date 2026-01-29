import os
import requests
import time
from app.core.config import get_settings

print("🔍 Verificando si el pago se procesó y el plan se actualizó\n")

# Obtener token del último usuario creado
print("1️⃣  Creando nuevo usuario para verificar...")
base_url = os.getenv("BACKEND_URL", "")
resp = requests.post(f"{base_url}/auth/login", json={'email': f'verify-{int(time.time())}@test.com'})
token = resp.json()['access_token']
print("   ✅ Usuario creado")

# 2. Ver plan inicial
print("\n2️⃣  Plan inicial:")
resp = requests.get(f"{base_url}/user", headers={'Authorization': f'Bearer {token}'})
user = resp.json()
print(f"   📊 Plan: {user['plan']}")
print(f"   📊 Uso: {user['usage']['used']}/{user['usage']['limit']}")

# 3. Crear checkout
print("\n3️⃣  Creando sesión de Checkout...")
resp = requests.post(
    f"{base_url}/billing/checkout",
    headers={'Authorization': f'Bearer {token}'},
    json={'return_url': f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing/return?session_id={CHECKOUT_SESSION_ID}"}
)
checkout = resp.json()
print(f"   ✅ Sesión: {checkout['sessionId']}")
print(f"   🌐 URL: {checkout['url']}\n")

print("   👉 COMPLETA EL PAGO EN EL NAVEGADOR:")
print("   💳 Tarjeta: 4242 4242 4242 4242")
print("   📅 Fecha: 12/25 (o cualquiera futura)")
print("   🔐 CVC: 123\n")

input("   ⏸️  Presiona Enter después de pagar...")

# 4. Esperar un poco y verificar plan
print("\n4️⃣  Verificando actualización de plan...")
time.sleep(3)

resp = requests.get(f"{base_url}/user", headers={'Authorization': f'Bearer {token}'})
user = resp.json()
print(f"   📊 Plan: {user['plan']}")
print(f"   📊 Uso: {user['usage']['used']}/{user['usage']['limit']}")

if user['plan'] == 'pro':
    print("\n   ✅ ¡ÉXITO! Plan actualizado a PRO")
    print("   🎉 Límite aumentado a 500 análisis/semana")
else:
    print(f"\n   ❌ Plan sigue siendo '{user['plan']}'")
    print("\n   Posibles causas:")
    print("   1. El webhook no recibió el evento (verifica Stripe CLI)")
    print("   2. El pago fue cancelado o rechazado")
    print("   3. El STRIPE_WEBHOOK_SECRET no es correcto")
