"""Script para ejecutar tests E2E completos con servidor incluido."""
import subprocess
import sys
import time
import os

# Remove DATABASE_URL from environment
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']
    print("✓ DATABASE_URL eliminada del entorno")

print("="*70)
print("LinkedIn Lead Checker - Testing E2E Automatizado")
print("="*70)

# Kill any existing Python processes
print("\n1. Limpiando procesos anteriores...")
subprocess.run(
    ["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"],
    capture_output=True
)
time.sleep(2)
print("   ✓ Procesos limpiados")

# Start server in background
print("\n2. Iniciando servidor backend...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:application", 
     "--host", "0.0.0.0", "--port", "8001"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print(f"   ✓ Servidor iniciado (PID: {server_process.pid})")

# Wait for server
print("\n3. Esperando que el servidor esté listo...")
time.sleep(5)
print("   ✓ Servidor listo")

# Run tests
print("\n4. Ejecutando tests E2E...")
print("="*70 + "\n")

try:
    result = subprocess.run(
        [sys.executable, "test_e2e_pricing.py"],
        env={**os.environ, 'PYTHONUNBUFFERED': '1'}
    )
    exit_code = result.returncode
except KeyboardInterrupt:
    print("\n\n⚠️  Tests interrumpidos por el usuario")
    exit_code = 1
finally:
    print("\n" + "="*70)
    print("5. Limpiando...")
    print("="*70)
    server_process.terminate()
    server_process.wait()
    print("   ✓ Servidor detenido")
    print("\n" + "="*70)
    print("Testing completado")
    print("="*70 + "\n")
    
    sys.exit(exit_code)
