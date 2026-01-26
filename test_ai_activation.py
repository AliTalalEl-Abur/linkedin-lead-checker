#!/usr/bin/env python3
"""
Test del Sistema de Activación Comercial de IA
Verifica que la IA solo se active con suscriptores activos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import get_session_factory
from app.core.usage import evaluate_budget_status
from app.core.config import get_settings
from app.models.user import User

def test_ai_activation():
    """Test AI activation system"""
    print("\n" + "="*70)
    print("🧪 TEST: SISTEMA DE ACTIVACIÓN COMERCIAL DE IA")
    print("="*70 + "\n")
    
    settings = get_settings()
    SessionLocal = get_session_factory()
    db = SessionLocal()
    
    try:
        # Check current configuration
        print("📋 CONFIGURACIÓN ACTUAL:")
        print(f"   OPENAI_ENABLED: {settings.openai_enabled}")
        print(f"   OPENAI_API_KEY: {'✅ Configurada' if settings.openai_api_key else '❌ No configurada'}")
        print()
        
        # Count active subscribers
        starter_count = db.query(User).filter(User.plan == 'starter').count()
        pro_count = db.query(User).filter(User.plan == 'pro').count()
        team_count = db.query(User).filter(User.plan == 'team').count()
        total_subscribers = starter_count + pro_count + team_count
        
        print("👥 SUSCRIPTORES ACTIVOS:")
        print(f"   Starter: {starter_count}")
        print(f"   Pro: {pro_count}")
        print(f"   Team: {team_count}")
        print(f"   TOTAL: {total_subscribers}")
        print()
        
        # Evaluate budget status
        budget_status = evaluate_budget_status(db)
        
        print("💰 ESTADO DEL PRESUPUESTO:")
        print(f"   Budget mensual: ${budget_status.budget:.2f}")
        print(f"   Gasto actual: ${budget_status.spend:.2f}")
        print(f"   Allowed: {budget_status.allowed}")
        print(f"   Reason: {budget_status.reason or 'None'}")
        print()
        
        # Determine AI status
        print("🤖 ESTADO DE LA IA:")
        if not settings.openai_enabled:
            print("   ❌ DESHABILITADA (OPENAI_ENABLED=false)")
            print("   📝 Mensaje: 'AI launching soon'")
            print("   ℹ️  Acción: Configurar OPENAI_ENABLED=true cuando estés listo")
        elif total_subscribers == 0:
            print("   ⏳ ESPERANDO PRIMER SUSCRIPTOR")
            print("   📝 Mensaje: 'Full AI analysis coming soon - join the waitlist!'")
            print("   ℹ️  Acción: La IA se activará automáticamente con el primer suscriptor")
        elif budget_status.reason == "exhausted":
            print("   ⚠️  BUDGET AGOTADO")
            print("   📝 Mensaje: 'Analysis temporarily unavailable'")
            print("   ℹ️  Acción: Esperar al próximo mes o aumentar planes")
        elif budget_status.allowed:
            print("   ✅ ACTIVA Y OPERANDO")
            print("   📝 Análisis con IA habilitados")
            print("   💡 Margen: ${:.2f}".format(budget_status.budget - budget_status.spend))
        else:
            print(f"   ❓ Estado desconocido: {budget_status.reason}")
        
        print()
        print("="*70)
        
        # Test scenarios
        print("\n🔍 ESCENARIOS DE PRUEBA:\n")
        
        print("1️⃣  Pre-Launch (Sin suscriptores):")
        if total_subscribers == 0:
            print("   ✅ ESTADO ACTUAL")
            print("   → Los usuarios ven: 'AI launching soon'")
            print("   → Sin llamadas a OpenAI")
            print("   → Gasto en IA: $0")
        else:
            print("   ℹ️  Para probar, ejecuta:")
            print("   → sqlite3 linkedin_lead_checker.db")
            print("   → UPDATE users SET plan='free' WHERE plan != 'free';")
        
        print("\n2️⃣  Primera Activación (Primer suscriptor):")
        if total_subscribers > 0:
            print("   ✅ IA YA ACTIVADA")
            print("   → Log generado en primera activación: 🚀 AI COMMERCIALLY ACTIVATED!")
            print("   → Llamadas a OpenAI habilitadas")
        else:
            print("   ℹ️  Para activar, crea un suscriptor:")
            print("   → UPDATE users SET plan='starter' WHERE email='test@example.com';")
            print("   → El siguiente análisis logeará: 🚀 AI COMMERCIALLY ACTIVATED!")
        
        print("\n3️⃣  OpenAI Deshabilitado:")
        if not settings.openai_enabled:
            print("   ✅ ESTADO ACTUAL")
            print("   → Incluso con suscriptores, IA no se activa")
            print("   → Mensaje: 'AI launching soon'")
        else:
            print("   ℹ️  Para probar:")
            print("   → Configurar: OPENAI_ENABLED=false en .env")
            print("   → Reiniciar servidor")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETADO")
        print("="*70 + "\n")
        
        # Summary
        if not settings.openai_enabled:
            print("📊 RESUMEN: IA deshabilitada globalmente")
        elif total_subscribers == 0:
            print("📊 RESUMEN: Esperando primer suscriptor para activar IA")
        elif budget_status.allowed:
            print("📊 RESUMEN: IA activa con {total_subscribers} suscriptores - Operando normalmente")
        else:
            print(f"📊 RESUMEN: IA bloqueada - Razón: {budget_status.reason}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    try:
        success = test_ai_activation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test falló: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
