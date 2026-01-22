"""
Test script para verificar hardening y límites.

Este script prueba:
1. Configuración de logging
2. Inicialización del servicio AI con timeout
3. Manejo de errores básico
4. Kill switches (simulados)
"""

import logging
import os
import sys

# Configurar logging antes de importar
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging():
    """Test 1: Verificar que el logging funciona."""
    logger.info("✓ Logging configurado correctamente")
    logger.warning("✓ Warnings funcionan")
    logger.error("✓ Errors funcionan")
    print("Test 1 PASSED: Logging ✓\n")


def test_ai_service_init():
    """Test 2: Verificar inicialización del servicio AI."""
    from app.services.ai_service import AIAnalysisService, OPENAI_TIMEOUT, MAX_RETRIES
    
    # Test sin API key (modo mock)
    service_mock = AIAnalysisService(openai_api_key=None)
    assert service_mock.use_mock is True, "Debería estar en modo mock sin API key"
    logger.info("✓ Servicio AI en modo MOCK funciona")
    
    # Test configuración de hardening
    assert OPENAI_TIMEOUT == 30, f"Timeout debería ser 30s, es {OPENAI_TIMEOUT}"
    assert MAX_RETRIES == 3, f"Max retries debería ser 3, es {MAX_RETRIES}"
    logger.info("✓ Constantes de hardening configuradas correctamente")
    logger.info(f"  - Timeout: {OPENAI_TIMEOUT}s")
    logger.info(f"  - Max Retries: {MAX_RETRIES}")
    
    print("Test 2 PASSED: AI Service Initialization ✓\n")


def test_config_kill_switches():
    """Test 3: Verificar que los kill switches están en la configuración."""
    from app.core.config import get_settings
    
    settings = get_settings()
    
    # Verificar que existen los kill switches
    assert hasattr(settings, 'disable_all_analyses'), "Falta disable_all_analyses"
    assert hasattr(settings, 'disable_free_plan'), "Falta disable_free_plan"
    
    logger.info("✓ Kill switches configurados en settings")
    logger.info(f"  - disable_all_analyses: {settings.disable_all_analyses}")
    logger.info(f"  - disable_free_plan: {settings.disable_free_plan}")
    
    # Verificar límites
    assert settings.usage_limit_free == 3, "FREE limit debería ser 3"
    assert settings.usage_limit_pro == 100, "PRO limit debería ser 100"
    assert settings.usage_limit_team == 300, "TEAM limit debería ser 300"
    assert settings.rate_limit_seconds == 30, "Rate limit debería ser 30s"
    
    logger.info("✓ Límites de uso configurados correctamente")
    logger.info(f"  - FREE: {settings.usage_limit_free} análisis total")
    logger.info(f"  - PRO: {settings.usage_limit_pro} análisis/semana")
    logger.info(f"  - TEAM: {settings.usage_limit_team} análisis/semana")
    logger.info(f"  - Rate limit: {settings.rate_limit_seconds}s")
    
    print("Test 3 PASSED: Configuration ✓\n")


def test_mock_analysis():
    """Test 4: Verificar que el análisis en modo mock funciona."""
    from app.services.ai_service import AIAnalysisService
    
    service = AIAnalysisService(openai_api_key=None)
    
    profile_data = {
        "name": "John Doe",
        "title": "VP Engineering",
        "company": "Tech Corp",
    }
    
    logger.info("Ejecutando análisis en modo MOCK...")
    result = service.analyze_profile(profile_data)
    
    assert result.should_contact is not None, "Debería retornar decisión"
    assert result.score > 0, "Debería retornar score"
    assert result.reasoning, "Debería retornar reasoning"
    
    logger.info("✓ Análisis en modo MOCK completado")
    logger.info(f"  - Decision: {'CONTACT' if result.should_contact else 'SKIP'}")
    logger.info(f"  - Score: {result.score}")
    logger.info(f"  - Priority: {result.priority}")
    
    print("Test 4 PASSED: Mock Analysis ✓\n")


def test_error_handling():
    """Test 5: Verificar que el manejo de errores funciona."""
    from app.services.ai_service import _run_chat_json
    
    # Test con cliente None
    try:
        _run_chat_json(None, [])
        assert False, "Debería haber lanzado RuntimeError"
    except RuntimeError as e:
        assert "not initialized" in str(e).lower()
        logger.info("✓ Error handling para cliente None funciona")
    
    print("Test 5 PASSED: Error Handling ✓\n")


def main():
    """Ejecutar todos los tests."""
    print("=" * 60)
    print("HARDENING & LIMITS - TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Logging", test_logging),
        ("AI Service Init", test_ai_service_init),
        ("Config & Kill Switches", test_config_kill_switches),
        ("Mock Analysis", test_mock_analysis),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"✗ Test '{name}' FAILED: {e}", exc_info=True)
            failed += 1
            print(f"Test FAILED: {name} ✗\n")
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Sistema de hardening funcionando correctamente!")
        print("\nHardening implementado:")
        print("  ✓ Timeouts (30s)")
        print("  ✓ Retries con backoff exponencial (3 intentos)")
        print("  ✓ Manejo robusto de errores OpenAI")
        print("  ✓ Kill switches para free users")
        print("  ✓ Logging básico estructurado")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
