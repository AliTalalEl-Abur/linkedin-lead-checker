import os
import requests
import time

print("✅ Test rápido de pago\n")

# 1. Usuario nuevo
base_url = os.getenv("BACKEND_URL", "")
resp = requests.post(f"{base_url}/auth/login", json={'email': f'final-{int(time.time())}@test.com'})
token = resp.json()['access_token']

# 2. Plan inicial
resp = requests.get(f"{base_url}/user", headers={'Authorization': f'Bearer {token}'})
print(f"ANTES: {resp.json()['plan']} ({resp.json()['usage']['limit']} análisis)")

# 3. Crear checkout y abrir navegador
import webbrowser
resp = requests.post(
    f"{base_url}/billing/checkout",
    headers={'Authorization': f'Bearer {token}'},
    json={'return_url': f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing/return?session_id={CHECKOUT_SESSION_ID}"}
)
url = resp.json()['url']
print(f"\n🌐 URL: {url}")
print("💳 Tarjeta: 4242 4242 4242 4242 | 12/25 | 123\n")
webbrowser.open(url)

input("Presiona Enter después de pagar...")

# 4. Esperar y verificar
time.sleep(2)
resp = requests.get(f"{base_url}/user", headers={'Authorization': f'Bearer {token}'})
plan = resp.json()['plan']
limit = resp.json()['usage']['limit']
print(f"\nDESPUÉS: {plan} ({limit} análisis)")

if plan == 'pro':
    print("✅ ¡ÉXITO! Plan actualizado a PRO")
else:
    print("❌ Plan no se actualizó. Verifica que Stripe Listen esté activo.")
