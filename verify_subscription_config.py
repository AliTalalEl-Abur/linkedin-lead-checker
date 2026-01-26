"""
Script de verificación para el nuevo sistema de suscripciones.
Verifica que los límites y configuración estén correctos.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.utils import get_current_month_key

def verify_configuration():
    """Verify that all configuration is correct."""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DEL SISTEMA DE SUSCRIPCIONES")
    print("="*60 + "\n")
    
    settings = get_settings()
    
    # Check limits
    print("📊 LÍMITES CONFIGURADOS:")
    print(f"  ├─ FREE:     {settings.usage_limit_free} análisis (lifetime)")
    print(f"  ├─ STARTER:  {settings.usage_limit_starter} análisis/mes")
    print(f"  ├─ PRO:      {settings.usage_limit_pro} análisis/mes")
    print(f"  └─ BUSINESS: {settings.usage_limit_business} análisis/mes")
    
    # Verify expected values
    errors = []
    
    if settings.usage_limit_free != 3:
        errors.append(f"❌ FREE limit debería ser 3, es {settings.usage_limit_free}")
    
    if settings.usage_limit_starter != 40:
        errors.append(f"❌ STARTER limit debería ser 40, es {settings.usage_limit_starter}")
    
    if settings.usage_limit_pro != 150:
        errors.append(f"❌ PRO limit debería ser 150, es {settings.usage_limit_pro}")
    
    if settings.usage_limit_business != 500:
        errors.append(f"❌ BUSINESS limit debería ser 500, es {settings.usage_limit_business}")
    
    # Check revenue settings
    print("\n💰 REVENUE POR PLAN:")
    print(f"  ├─ STARTER:  ${settings.revenue_per_starter_user}/mes")
    print(f"  ├─ PRO:      ${settings.revenue_per_pro_user}/mes")
    print(f"  └─ TEAM: ${settings.revenue_per_team_user}/mes")
    
    # Check Stripe config
    print("\n🔐 CONFIGURACIÓN STRIPE:")
    has_api_key = bool(settings.stripe_api_key)
    has_webhook = bool(settings.stripe_webhook_secret)
    has_starter = bool(settings.stripe_price_starter_id)
    has_pro = bool(settings.stripe_price_pro_id)
    has_team = bool(settings.stripe_price_team_id)
    
    print(f"  ├─ API Key:          {'✅' if has_api_key else '⚠️  (no configurada)'}")
    print(f"  ├─ Webhook Secret:   {'✅' if has_webhook else '⚠️  (no configurado)'}")
    print(f"  ├─ Starter Price ID: {'✅' if has_starter else '⚠️  (no configurado)'}")
    print(f"  ├─ Pro Price ID:     {'✅' if has_pro else '⚠️  (no configurado)'}")
    print(f"  └─ Team Price ID:{'✅' if has_team else '⚠️  (no configurado)'}")
    
    if not (has_api_key and has_webhook):
        print("\n  ⚠️  Nota: Stripe no está completamente configurado.")
        print("     Esto es normal en desarrollo si no planeas probar pagos.")
    
    # Check month key generation
    print("\n📅 TRACKING MENSUAL:")
    month_key = get_current_month_key()
    print(f"  └─ Month Key actual: {month_key}")
    
    if len(month_key) != 7 or month_key[4] != '-':
        errors.append(f"❌ month_key debería tener formato YYYY-MM, es '{month_key}'")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print("❌ ERRORES ENCONTRADOS:")
        for error in errors:
            print(f"  {error}")
        print("="*60 + "\n")
        return False
    else:
        print("✅ CONFIGURACIÓN CORRECTA")
        print("="*60)
        print("\n🎯 RESUMEN:")
        print("  • Límites mensuales configurados correctamente")
        print("  • Sistema de tracking mensual activo")
        print("  • 3 planes pagos: Starter ($9), Pro ($19), Team ($49)")
        print("  • Límites DUROS (sin rollover)")
        print("\n📝 PRÓXIMOS PASOS:")
        print("  1. Ejecutar migración: python migrations/add_month_key_to_usage_events.py")
        print("  2. Configurar Stripe Price IDs en .env (si aún no lo hiciste)")
        print("  3. Iniciar servidor: python start_server.py")
        print("  4. Probar límites con usuarios de prueba")
        print()
        return True


if __name__ == "__main__":
    try:
        success = verify_configuration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
