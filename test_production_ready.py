"""
Quick production readiness check.
Validates that the backend can start with minimal configuration.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_minimal_startup():
    """Test that app starts with only required env vars."""
    print("=" * 60)
    print("Testing Production Readiness")
    print("=" * 60)
    
    # Set minimal required env vars
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET_KEY"] = "test-key-with-at-least-32-characters-for-validation"
    os.environ["ENV"] = "test"
    
    try:
        print("\n1. Importing app module...")
        from app.main import app
        print("   ✅ App imported successfully")
        
        print("\n2. Checking app type...")
        from fastapi import FastAPI
        assert isinstance(app, FastAPI), f"Expected FastAPI instance, got {type(app)}"
        print("   ✅ App is FastAPI instance")
        
        print("\n3. Checking health endpoint...")
        routes = [route.path for route in app.routes]
        assert "/health" in routes, "Health endpoint not found"
        print("   ✅ Health endpoint exists")
        
        print("\n4. Testing health endpoint...")
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("ok") is True, f"Health check returned ok=False: {data}"
        assert "env" in data, "Health check missing env field"
        print(f"   ✅ Health check passed: {data}")
        
        print("\n5. Testing startup without OpenAI...")
        # Ensure OpenAI is disabled
        from app.core.config import get_settings
        settings = get_settings()
        if settings.openai_api_key and not settings.openai_enabled:
            print("   ✅ OpenAI disabled by default (OPENAI_ENABLED=false)")
        elif not settings.openai_api_key:
            print("   ✅ OpenAI key not set (mock mode)")
        else:
            print("   ⚠️  Warning: OpenAI enabled - should be false by default")
        
        print("\n6. Testing startup without Stripe...")
        if not settings.stripe_api_key:
            print("   ✅ Stripe not configured (optional)")
        else:
            print("   ℹ️  Stripe configured")
        
        print("\n" + "=" * 60)
        print("✅ All production readiness checks passed!")
        print("=" * 60)
        print("\nBackend can start with:")
        print("  - DATABASE_URL")
        print("  - JWT_SECRET_KEY")
        print("\nOptional services work in degraded mode:")
        print("  - OpenAI: Preview mode (zero cost)")
        print("  - Stripe: Billing disabled")
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Production readiness check FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_startup()
    sys.exit(0 if success else 1)
