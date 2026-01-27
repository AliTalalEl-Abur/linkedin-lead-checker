"""
Test del endpoint GET /billing/status
Verifica que devuelve toda la información requerida
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import create_app
from app.core.db import get_session_factory
from app.models.user import User
from datetime import datetime, timezone, timedelta

def test_billing_status():
    """Test GET /billing/status endpoint"""
    print("\n" + "="*70)
    print("🧪 TEST: GET /billing/status endpoint")
    print("="*70 + "\n")
    
    app = create_app()
    client = TestClient(app)
    
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()
    
    try:
        # Test scenarios
        test_cases = [
            {
                "email": "free_test@example.com",
                "plan": "free",
                "lifetime_count": 2,
                "monthly_count": 0,
                "expected_limit": 3,
                "expected_current": 2,
                "expected_can_analyze": True,
                "reset_date": None
            },
            {
                "email": "starter_test@example.com",
                "plan": "starter",
                "lifetime_count": 0,
                "monthly_count": 25,
                "expected_limit": 40,
                "expected_current": 25,
                "expected_can_analyze": True,
                "reset_date": datetime.now(timezone.utc) + timedelta(days=15)
            },
            {
                "email": "pro_test@example.com",
                "plan": "pro",
                "lifetime_count": 0,
                "monthly_count": 150,
                "expected_limit": 150,
                "expected_current": 150,
                "expected_can_analyze": False,
                "reset_date": datetime.now(timezone.utc) + timedelta(days=7)
            },
            {
                "email": "team_test@example.com",
                "plan": "team",
                "lifetime_count": 0,
                "monthly_count": 200,
                "expected_limit": 500,
                "expected_current": 200,
                "expected_can_analyze": True,
                "reset_date": datetime.now(timezone.utc) + timedelta(days=20)
            }
        ]
        
        for case in test_cases:
            print(f"📋 Testing {case['plan'].upper()} plan...")
            
            # Create or update user
            user = db.query(User).filter(User.email == case["email"]).first()
            if not user:
                user = User(
                    email=case["email"],
                    plan=case["plan"],
                    lifetime_analyses_count=case["lifetime_count"],
                    monthly_analyses_count=case["monthly_count"]
                )
                if case["reset_date"]:
                    user.monthly_analyses_reset_at = case["reset_date"]
                db.add(user)
            else:
                user.plan = case["plan"]
                user.lifetime_analyses_count = case["lifetime_count"]
                user.monthly_analyses_count = case["monthly_count"]
                if case["reset_date"]:
                    user.monthly_analyses_reset_at = case["reset_date"]
            
            db.commit()
            db.refresh(user)
            
            # Generate JWT token
            from app.core.security import create_access_token
            token = create_access_token({"sub": str(user.id)})
            
            # Call endpoint
            response = client.get(
                "/billing/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ ERROR: Expected 200, got {response.status_code}")
                print(f"   Response: {response.json()}")
                return False
            
            data = response.json()
            print(f"   Response: {data}")
            
            # Validate response structure
            required_fields = ["plan", "usage_current", "usage_limit", "reset_date", "can_analyze", "subscription_status"]
            for field in required_fields:
                if field not in data:
                    print(f"   ❌ ERROR: Campo '{field}' no encontrado en la respuesta")
                    return False
            
            # Validate plan
            if data["plan"] != case["plan"]:
                print(f"   ❌ ERROR: Plan esperado '{case['plan']}', recibido '{data['plan']}'")
                return False
            
            # Validate usage_limit
            if data["usage_limit"] != case["expected_limit"]:
                print(f"   ❌ ERROR: Límite esperado {case['expected_limit']}, recibido {data['usage_limit']}")
                return False
            
            # Validate usage_current
            if data["usage_current"] != case["expected_current"]:
                print(f"   ❌ ERROR: Uso esperado {case['expected_current']}, recibido {data['usage_current']}")
                return False
            
            # Validate can_analyze
            if data["can_analyze"] != case["expected_can_analyze"]:
                print(f"   ❌ ERROR: can_analyze esperado {case['expected_can_analyze']}, recibido {data['can_analyze']}")
                return False
            
            # Validate reset_date
            if case["reset_date"] is None:
                if data["reset_date"] is not None:
                    print(f"   ❌ ERROR: reset_date debería ser None para plan free")
                    return False
            else:
                if data["reset_date"] is None:
                    print(f"   ❌ ERROR: reset_date no debería ser None para plan {case['plan']}")
                    return False
            
            print(f"   ✅ Todas las validaciones pasaron para {case['plan'].upper()}")
            print()
        
        print("="*70)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*70)
        return True
        
    finally:
        db.close()


if __name__ == "__main__":
    try:
        success = test_billing_status()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test falló: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
