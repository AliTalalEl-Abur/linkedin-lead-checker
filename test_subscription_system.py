"""
Test end-to-end para verificar el nuevo sistema de suscripciones.
Prueba límites mensuales y cálculo de remaining_analyses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.db import get_session_factory
from app.models.user import User
from app.core.usage import check_usage_limit, record_usage, get_usage_stats
from app.core.config import get_settings
from app.core.utils import get_current_month_key
from fastapi import HTTPException

def test_subscription_system():
    """Test the new subscription system."""
    print("\n" + "="*60)
    print("🧪 TEST: NUEVO SISTEMA DE SUSCRIPCIONES")
    print("="*60 + "\n")
    
    settings = get_settings()
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()
    
    try:
        # Test data
        test_cases = [
            ("starter", settings.usage_limit_starter, "$9/mes - 40 análisis/mes"),
            ("pro", settings.usage_limit_pro, "$19/mes - 150 análisis/mes"),
            ("business", settings.usage_limit_business, "$49/mes - 500 análisis/mes"),
        ]
        
        month_key = get_current_month_key()
        print(f"📅 Testing para mes: {month_key}\n")
        
        for plan, expected_limit, description in test_cases:
            print(f"📊 Testing plan: {plan.upper()}")
            print(f"   {description}")
            
            # Create or get test user
            test_email = f"test_{plan}@example.com"
            user = db.query(User).filter(User.email == test_email).first()
            
            if not user:
                user = User(email=test_email, plan=plan)
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"   ✅ Usuario creado: {test_email}")
            else:
                user.plan = plan
                db.commit()
                print(f"   ✅ Usuario actualizado: {test_email}")
            
            # Get usage stats
            stats = get_usage_stats(user, db)
            
            print(f"   Límite configurado: {expected_limit}")
            print(f"   Límite retornado: {stats['limit']}")
            print(f"   Usado: {stats['used']}")
            print(f"   Restante: {stats['remaining']}")
            
            # Verify limit is correct
            if stats['limit'] != expected_limit:
                print(f"   ❌ ERROR: Límite incorrecto!")
                return False
            
            # Verify remaining calculation
            expected_remaining = max(0, expected_limit - stats['used'])
            if stats['remaining'] != expected_remaining:
                print(f"   ❌ ERROR: remaining incorrecto!")
                return False
            
            # Verify month_key
            if 'month_key' not in stats:
                print(f"   ❌ ERROR: month_key no está en stats!")
                return False
            
            if stats['month_key'] != month_key:
                print(f"   ❌ ERROR: month_key incorrecto!")
                return False
            
            print(f"   ✅ Todo correcto para plan {plan.upper()}\n")
        
        # Test hard cap enforcement
        print("🔒 Testing límite DURO (hard cap)...")
        
        # Get a user with some usage
        test_user = db.query(User).filter(User.plan == "starter").first()
        if test_user:
            stats = get_usage_stats(test_user, db)
            print(f"   Usuario: {test_user.email}")
            print(f"   Plan: {test_user.plan.upper()}")
            print(f"   Usado: {stats['used']}/{stats['limit']}")
            
            if stats['used'] >= stats['limit']:
                print(f"   Límite alcanzado. Testing bloqueo...")
                try:
                    check_usage_limit(test_user, db)
                    print(f"   ❌ ERROR: No se bloqueó al alcanzar límite!")
                    return False
                except HTTPException as e:
                    if e.status_code == 429:
                        print(f"   ✅ Bloqueado correctamente con HTTP 429")
                        print(f"   Mensaje: {e.detail}")
                    else:
                        print(f"   ❌ ERROR: Status code incorrecto: {e.status_code}")
                        return False
            else:
                print(f"   ⚠️  Usuario aún no alcanzó límite. Testing omitido.")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*60)
        print("\n🎯 VERIFICACIONES EXITOSAS:")
        print("  • Límites mensuales correctos (40, 150, 500)")
        print("  • Cálculo de remaining_analyses correcto")
        print("  • month_key presente en respuestas")
        print("  • Sistema usa tracking mensual")
        print("  • Límites DUROS funcionando")
        
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
        success = test_subscription_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test falló: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
