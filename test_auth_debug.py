import os
import requests
import json
from jose import jwt
from app.core.config import get_settings

print("🔍 Diagnóstico de Autenticación\n")

# 1. Login
print("1. Realizando login...")
base_url = os.getenv("BACKEND_URL", "")
resp = requests.post(f"{base_url}/auth/login", json={'email': 'test_complete@example.com'})
print(f"   Status: {resp.status_code}")
token_data = resp.json()
token = token_data['access_token']
print(f"   Token: {token[:50]}...")

# 2. Decodificar token
print("\n2. Decodificando token...")
settings = get_settings()
try:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    print(f"   ✅ Payload: {payload}")
    user_id = payload.get('sub')
    print(f"   ✅ User ID: {user_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar usuario en BD
print("\n3. Buscando usuario en BD...")
from app.core.db import get_session_factory
from app.models.user import User
SessionLocal = get_session_factory()
db = SessionLocal()
user = db.query(User).filter(User.id == user_id).first()
if user:
    print(f"   ✅ Usuario encontrado: {user.email}")
else:
    print(f"   ❌ Usuario NO encontrado con ID {user_id}")

# 4. Llamar a /user
print("\n4. Llamando a GET /user...")
headers = {'Authorization': f'Bearer {token}'}
resp_user = requests.get(f"{base_url}/user", headers=headers)
print(f"   Status: {resp_user.status_code}")
if resp_user.status_code == 200:
    print(f"   ✅ Response: {resp_user.json()}")
else:
    print(f"   ❌ Response: {resp_user.text}")

db.close()
