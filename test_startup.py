#!/usr/bin/env python
"""Test rápido de startup de la app"""
import sys
import traceback

print("1. Importando FastAPI...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n2. Importando create_app...")
try:
    from app.main import create_app
    print("   ✅ create_app importado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n3. Creando app...")
try:
    application = create_app()
    print(f"   ✅ App creada: {type(application)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n4. Verificando rutas...")
try:
    routes = [route.path for route in application.routes]
    print(f"   ✅ Rutas ({len(routes)} total):")
    for route in sorted(set(routes)):
        print(f"      - {route}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ App OK, lista para uvicorn")
