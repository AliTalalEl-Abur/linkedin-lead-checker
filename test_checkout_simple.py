#!/usr/bin/env python
"""
Script simplificado para probar Stripe Checkout
Ejecuta: python test_checkout_simple.py
"""
import os
import requests
import time
import webbrowser

BASE_URL = os.getenv("BACKEND_URL", "")

print("\n🧪 TEST: Flujo de Stripe Checkout\n")

# 1. Crear usuario
print("1️⃣  Creando usuario de prueba...")
try:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "test-stripe@example.com"}
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print("   ✅ Token obtenido")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 2. Ver plan inicial
print("\n2️⃣  Verificando plan inicial...")
try:
    resp = requests.get(
        f"{BASE_URL}/user",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    user = resp.json()
    print(f"   📊 Plan: {user['plan']}")
    print(f"   📊 Email: {user['email']}")
    print(f"   📊 Uso: {user['usage']['used']}/{user['usage']['limit']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 3. Crear checkout
print("\n3️⃣  Creando sesión de Checkout...")
try:
    resp = requests.post(
        f"{BASE_URL}/billing/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"return_url": f"{os.getenv('NEXT_PUBLIC_SITE_URL', '')}/billing/return?session_id={CHECKOUT_SESSION_ID}"}
    )
    resp.raise_for_status()
    checkout = resp.json()
    print(f"   ✅ Sesión creada: {checkout['sessionId']}")
    print(f"   🌐 URL: {checkout['url']}")
    print("\n   👉 Abriendo navegador...")
    print("   💳 Usa tarjeta de prueba: 4242 4242 4242 4242")
    print("      (cualquier fecha futura y CVC)\n")
    
    webbrowser.open(checkout['url'])
    
    input("   ⏸️  Presiona Enter después de completar el pago...")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 4. Verificar plan actualizado
print("\n4️⃣  Verificando actualización de plan...")
time.sleep(2)
try:
    resp = requests.get(
        f"{BASE_URL}/user",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    user = resp.json()
    print(f"   📊 Plan: {user['plan']}")
    print(f"   📊 Uso: {user['usage']['used']}/{user['usage']['limit']}")
    
    if user['plan'] == 'pro':
        print("\n   ✅ ¡ÉXITO! Plan actualizado a PRO")
        print("   🎉 Límite aumentado de 5 a 500 análisis/semana")
    else:
        print(f"\n   ⚠️  Plan sigue siendo '{user['plan']}'")
        print("   💡 Verifica que Stripe Listen esté activo")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n✅ Test completado\n")
