"""E2E Testing del nuevo sistema de precios y límites."""
import subprocess
import time
import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
TEST_EMAIL_PREFIX = f"test_{int(time.time())}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(msg):
    print(f"\n{Colors.BLUE}🧪 TEST:{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")

def wait_for_server():
    """Espera a que el servidor esté listo."""
    print_info("Esperando que el servidor esté listo...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print_success("Servidor listo")
                return True
        except:
            time.sleep(1)
    print_error("Servidor no responde después de 30 segundos")
    return False

def create_user(email_suffix):
    """Crea un nuevo usuario FREE."""
    email = f"{TEST_EMAIL_PREFIX}_{email_suffix}@example.com"
    data = {"email": email, "password": "TestPass123!", "full_name": f"Test User {email_suffix}"}
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data, timeout=30)
    
    if response.status_code != 200:
        print_error(f"Error creando usuario: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None, None
    
    data = response.json()
    token = data.get("access_token")
    return email, token

def get_usage(token):
    """Obtiene estadísticas de uso."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/me/usage", headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

def analyze_profile(token, profile_data):
    """Realiza un análisis de perfil."""
    headers = {"Authorization": f"Bearer {token}"}
    # Wrap profile data in the required structure
    payload = {"profile_extract": profile_data}
    response = requests.post(
        f"{BASE_URL}/analyze/linkedin",
        headers=headers,
        json=payload,
        timeout=30
    )
    return response

def test_free_plan_limits():
    """Test 1: FREE plan - 3 análisis lifetime."""
    print_test("FREE Plan - 3 análisis lifetime")
    
    # Crear usuario FREE
    email, token = create_user("free1")
    if not token:
        print_error("No se pudo crear usuario FREE")
        return False
    
    print_success(f"Usuario FREE creado: {email}")
    
    # Verificar uso inicial
    usage = get_usage(token)
    print_info(f"Uso inicial: {usage}")
    
    # Datos de perfil de prueba
    profile = {
        "name": "John Doe",
        "headline": "Software Engineer at Tech Corp",
        "about": "Experienced developer",
        "current_company": "Tech Corp",
        "current_position": "Software Engineer",
        "location": "San Francisco, CA"
    }
    
    # Realizar 3 análisis
    for i in range(1, 4):
        print_info(f"Análisis {i}/3...")
        response = analyze_profile(token, profile)
        
        if response.status_code == 200:
            print_success(f"Análisis {i} exitoso")
            # Esperar 31 segundos para evitar rate limit
            if i < 3:
                print_info("Esperando 31 segundos (rate limit)...")
                time.sleep(31)
        else:
            print_error(f"Análisis {i} falló: {response.status_code} - {response.text}")
            return False
    
    # Intentar 4to análisis (debe fallar con 402)
    print_info("Intentando 4to análisis (debe fallar)...")
    time.sleep(31)  # Rate limit
    response = analyze_profile(token, profile)
    
    if response.status_code == 402:
        print_success("4to análisis bloqueado correctamente (402 Payment Required)")
        error_data = response.json()
        print_info(f"Mensaje: {error_data.get('detail')}")
        return True
    else:
        print_error(f"4to análisis no fue bloqueado! Status: {response.status_code}")
        return False

def test_rate_limiting():
    """Test 2: Rate limiting - 30 segundos."""
    print_test("Rate Limiting - 30 segundos entre análisis")
    
    # Crear usuario
    email, token = create_user("ratelimit")
    if not token:
        return False
    
    print_success(f"Usuario creado: {email}")
    
    profile = {
        "name": "Jane Smith",
        "headline": "Product Manager",
        "about": "PM with 5 years experience",
        "current_company": "StartupXYZ",
        "current_position": "Product Manager",
        "location": "New York, NY"
    }
    
    # Primer análisis
    print_info("Primer análisis...")
    response = analyze_profile(token, profile)
    if response.status_code != 200:
        print_error(f"Primer análisis falló: {response.status_code}")
        return False
    print_success("Primer análisis exitoso")
    
    # Intentar inmediatamente (debe fallar)
    print_info("Intentando segundo análisis inmediatamente (debe fallar)...")
    response = analyze_profile(token, profile)
    
    if response.status_code == 429:
        print_success("Rate limit funcionando correctamente (429 Too Many Requests)")
        error_data = response.json()
        print_info(f"Mensaje: {error_data.get('detail')}")
    else:
        print_error(f"Rate limit no funcionó! Status: {response.status_code}")
        return False
    
    # Esperar 31 segundos y reintentar
    print_info("Esperando 31 segundos...")
    time.sleep(31)
    
    print_info("Intentando segundo análisis después de 31s...")
    response = analyze_profile(token, profile)
    
    if response.status_code == 200:
        print_success("Segundo análisis exitoso después de esperar")
        return True
    else:
        print_error(f"Segundo análisis falló: {response.status_code}")
        return False

def test_usage_tracking():
    """Test 3: Verificar tracking de uso."""
    print_test("Tracking de Uso - Verificar estadísticas")
    
    # Crear usuario
    email, token = create_user("tracking")
    if not token:
        return False
    
    print_success(f"Usuario creado: {email}")
    
    # Verificar uso inicial (0/3)
    usage = get_usage(token)
    if not usage:
        print_error("No se pudo obtener uso")
        return False
    
    print_info(f"Uso inicial: {usage}")
    
    if usage.get("used") != 0 or usage.get("limit") != 3:
        print_error(f"Uso inicial incorrecto: {usage}")
        return False
    
    print_success("Uso inicial correcto: 0/3")
    
    # Realizar 1 análisis
    profile = {"name": "Test", "headline": "Test", "about": "Test", 
               "current_company": "Test", "current_position": "Test", "location": "Test"}
    
    response = analyze_profile(token, profile)
    if response.status_code != 200:
        print_error(f"Análisis falló: {response.status_code}")
        return False
    
    print_success("Análisis realizado")
    
    # Verificar uso actualizado (1/3)
    time.sleep(2)  # Dar tiempo para que se actualice
    usage = get_usage(token)
    print_info(f"Uso después de 1 análisis: {usage}")
    
    if usage.get("used") != 1:
        print_error(f"Uso no se actualizó correctamente: {usage}")
        return False
    
    print_success("Tracking de uso funcionando correctamente: 1/3")
    return True

def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print(f"{Colors.BLUE}🚀 LinkedIn Lead Checker - E2E Testing{Colors.RESET}")
    print(f"{Colors.BLUE}   Nuevo Sistema de Precios y Límites{Colors.RESET}")
    print("="*70)
    
    # Verificar servidor
    if not wait_for_server():
        print_error("El servidor no está corriendo en http://127.0.0.1:8001")
        print_info("Inicia el servidor con: python -m uvicorn app.main:application --host 127.0.0.1 --port 8001")
        return
    
    results = {}
    
    # Test 1: Usage Tracking
    try:
        results["usage_tracking"] = test_usage_tracking()
    except Exception as e:
        print_error(f"Test de tracking falló con excepción: {e}")
        results["usage_tracking"] = False
    
    # Test 2: Rate Limiting
    try:
        results["rate_limiting"] = test_rate_limiting()
    except Exception as e:
        print_error(f"Test de rate limiting falló con excepción: {e}")
        results["rate_limiting"] = False
    
    # Test 3: FREE Plan Limits (este es largo, ~100 segundos)
    print_info("⚠️  El siguiente test tomará ~100 segundos (3 análisis + rate limits)")
    user_wants_to_continue = input(f"{Colors.YELLOW}¿Continuar con test de FREE plan limits? (s/n): {Colors.RESET}").lower()
    
    if user_wants_to_continue == 's':
        try:
            results["free_plan_limits"] = test_free_plan_limits()
        except Exception as e:
            print_error(f"Test de FREE plan falló con excepción: {e}")
            results["free_plan_limits"] = False
    else:
        print_info("Test de FREE plan omitido")
        results["free_plan_limits"] = None
    
    # Resumen
    print("\n" + "="*70)
    print(f"{Colors.BLUE}📊 RESUMEN DE TESTS{Colors.RESET}")
    print("="*70)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASÓ")
        elif result is False:
            print_error(f"{test_name}: FALLÓ")
        else:
            print_info(f"{test_name}: OMITIDO")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print("\n" + "="*70)
    print(f"Total: {passed} pasaron, {failed} fallaron, {skipped} omitidos")
    print("="*70 + "\n")
    
    if failed == 0 and passed > 0:
        print(f"{Colors.GREEN}🎉 ¡TODOS LOS TESTS PASARON!{Colors.RESET}\n")
    elif failed > 0:
        print(f"{Colors.RED}⚠️  Algunos tests fallaron. Revisa los logs arriba.{Colors.RESET}\n")

if __name__ == "__main__":
    run_all_tests()
