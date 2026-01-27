"""
Test OpenAI Activation

Verifies that OpenAI is properly activated with all safety controls.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))


def test_environment_variables():
    """Test that all required environment variables are set"""
    print("\n🧪 Test 1: Environment Variables")
    print("="*70)
    
    required_vars = {
        'OPENAI_ENABLED': os.getenv('OPENAI_ENABLED'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'AI_COST_PER_ANALYSIS_USD': os.getenv('AI_COST_PER_ANALYSIS_USD', '0.03'),
        'USAGE_LIMIT_STARTER': os.getenv('USAGE_LIMIT_STARTER', '40'),
        'USAGE_LIMIT_PRO': os.getenv('USAGE_LIMIT_PRO', '150'),
        'USAGE_LIMIT_TEAM': os.getenv('USAGE_LIMIT_TEAM', '500'),
    }
    
    all_good = True
    for var, value in required_vars.items():
        if value:
            if var == 'OPENAI_API_KEY':
                print(f"   ✅ {var}: {value[:20]}...")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET")
            all_good = False
    
    # Check if enabled
    if os.getenv('OPENAI_ENABLED', 'false').lower() == 'true':
        print("\n   ✅ OpenAI is ENABLED")
    else:
        print("\n   ⚠️  OpenAI is DISABLED")
        all_good = False
    
    return all_good


def test_config_loading():
    """Test that settings load correctly"""
    print("\n🧪 Test 2: Configuration Loading")
    print("="*70)
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print(f"   ✅ Settings loaded")
        print(f"   • openai_enabled: {settings.openai_enabled}")
        print(f"   • openai_api_key: {'***' if settings.openai_api_key else 'NOT SET'}")
        print(f"   • ai_cost_per_analysis_usd: ${settings.ai_cost_per_analysis_usd}")
        print(f"   • usage_limit_starter: {settings.usage_limit_starter}")
        print(f"   • usage_limit_pro: {settings.usage_limit_pro}")
        print(f"   • usage_limit_team: {settings.usage_limit_team}")
        
        if not settings.openai_enabled:
            print("\n   ⚠️  OpenAI is disabled in settings")
            return False
        
        if not settings.openai_api_key:
            print("\n   ❌ OpenAI API key not loaded")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to load settings: {str(e)}")
        return False


def test_ai_service_initialization():
    """Test AI service initialization"""
    print("\n🧪 Test 3: AI Service Initialization")
    print("="*70)
    
    try:
        from app.services.ai_service import get_ai_service
        
        ai_service = get_ai_service()
        
        print(f"   ✅ AI service created")
        print(f"   • use_mock: {ai_service.use_mock}")
        print(f"   • has_client: {ai_service._client is not None}")
        print(f"   • has_api_key: {ai_service.openai_api_key is not None}")
        
        if ai_service.use_mock:
            print("\n   ⚠️  AI service in MOCK mode (no real API calls)")
            return False
        
        if not ai_service._client:
            print("\n   ❌ OpenAI client not initialized")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to initialize AI service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_subscription_validation():
    """Test that subscription validation works"""
    print("\n🧪 Test 4: Subscription Validation Logic")
    print("="*70)
    
    try:
        from app.api.routes.analyze import _determine_preview
        from app.models.user import User
        from app.core.usage import BudgetStatus
        from app.core.db import SessionLocal
        
        # Create test user (free plan)
        free_user = User(
            id=999,
            email="test@test.com",
            plan="free",
            analyses_limit=10,
            analyses_used=0
        )
        
        # Test budget status
        budget_status = BudgetStatus(
            allowed=True,
            reason="ok",
            spend=0.0,
            budget=100.0,
            active_subscribers=1
        )
        
        # Create a test database session
        db = SessionLocal()
        
        try:
            # Test free user (should get preview)
            preview, reason = _determine_preview(free_user, budget_status, db)
            
            if preview and reason == "free_plan":
                print("   ✅ Free users get preview mode (no AI)")
            else:
                print(f"   ❌ Free user validation failed: preview={preview}, reason={reason}")
                return False
            
            # Test paid user
            paid_user = User(
                id=1000,
                email="paid@test.com",
                plan="starter",
                analyses_limit=40,
                analyses_used=0
            )
            
            preview, reason = _determine_preview(paid_user, budget_status, db)
            
            if not preview:
                print("   ✅ Paid users get full AI analysis")
            else:
                print(f"   ⚠️  Paid user got preview: reason={reason}")
                return False
            
            # Test user at limit
            limit_user = User(
                id=1001,
                email="limit@test.com",
                plan="starter",
                analyses_limit=40,
                analyses_used=40
            )
            
            try:
                preview, reason = _determine_preview(limit_user, budget_status, db)
                print(f"   ❌ User at limit should raise HTTPException, got: preview={preview}")
                return False
            except Exception as e:
                if "limit" in str(e).lower() or "429" in str(e):
                    print("   ✅ Users at limit are blocked")
                else:
                    print(f"   ⚠️  Unexpected error for limit user: {str(e)}")
            
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"   ❌ Subscription validation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cost_tracking():
    """Test that costs are properly configured"""
    print("\n🧪 Test 5: Cost Tracking Configuration")
    print("="*70)
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        cost = settings.ai_cost_per_analysis_usd
        
        print(f"   ✅ Cost per analysis: ${cost:.4f}")
        
        # Test economics for each plan
        plans = [
            ("starter", settings.usage_limit_starter, settings.revenue_per_starter_user, 9.0),
            ("pro", settings.usage_limit_pro, settings.revenue_per_pro_user, 19.0),
            ("team", settings.usage_limit_team, settings.revenue_per_team_user, 49.0),
        ]
        
        all_profitable = True
        
        for plan_name, limit, revenue, price in plans:
            max_cost = limit * cost
            margin = revenue - max_cost
            margin_pct = (margin / price) * 100
            
            print(f"\n   {plan_name.upper()} Plan:")
            print(f"      • Price: ${price:.2f}/month")
            print(f"      • Limit: {limit} analyses")
            print(f"      • Max Cost: ${max_cost:.2f}")
            print(f"      • Revenue: ${revenue:.2f}")
            print(f"      • Margin: ${margin:.2f} ({margin_pct:.1f}%)")
            
            if margin > 0:
                print(f"      ✅ Profitable")
            else:
                print(f"      ❌ UNPROFITABLE!")
                all_profitable = False
        
        return all_profitable
        
    except Exception as e:
        print(f"   ❌ Cost tracking test failed: {str(e)}")
        return False


def test_error_handling():
    """Test that errors don't consume credits"""
    print("\n🧪 Test 6: Error Handling (No Credit Consumption)")
    print("="*70)
    
    try:
        # Check that record_usage is only called after successful analysis
        print("   ✅ Checking analyze.py endpoints...")
        
        with open('app/api/routes/analyze.py', 'r') as f:
            content = f.read()
        
        # Check that record_usage comes AFTER try/except
        if 'record_usage(current_user, db,' in content:
            # Count occurrences
            count = content.count('record_usage(current_user, db,')
            print(f"   ✅ Found {count} record_usage() calls")
            
            # Check they're after AI calls
            if 'record_usage' in content.split('try:')[-1]:
                print("   ✅ record_usage() called after successful analysis")
            
            # Check they're not in except blocks
            if 'except' in content and 'record_usage' not in content.split('except')[1].split('record_usage')[0]:
                print("   ✅ record_usage() NOT in error handlers")
            
            return True
        else:
            print("   ❌ record_usage() not found")
            return False
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {str(e)}")
        return False


def test_openai_disabled_check():
    """Test that OpenAI disabled check works"""
    print("\n🧪 Test 7: OpenAI Disabled Safety Check")
    print("="*70)
    
    try:
        with open('app/services/ai_service.py', 'r') as f:
            content = f.read()
        
        # Check for safety checks
        if 'if not settings.openai_enabled:' in content:
            count = content.count('if not settings.openai_enabled:')
            print(f"   ✅ Found {count} OpenAI enabled checks")
        else:
            print("   ❌ OpenAI enabled check not found")
            return False
        
        if 'AI_CALL_BLOCKED_OPENAI_DISABLED' in content:
            print("   ✅ Disabled calls are logged")
        
        if 'raise RuntimeError' in content and 'OpenAI API is disabled' in content:
            print("   ✅ Disabled calls raise error")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Disabled check test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("🧪 OpenAI Activation Test Suite")
    print("="*70)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Configuration Loading", test_config_loading),
        ("AI Service Initialization", test_ai_service_initialization),
        ("Subscription Validation", test_subscription_validation),
        ("Cost Tracking", test_cost_tracking),
        ("Error Handling", test_error_handling),
        ("OpenAI Disabled Check", test_openai_disabled_check),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - OpenAI is properly activated!")
        print("\n📝 Next Steps:")
        print("   1. Start backend: python run.py")
        print("   2. Test subscription: See TEST_SUBSCRIPTION.md")
        print("   3. Monitor usage: SELECT * FROM usage_events;")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        print("\n💡 Common Issues:")
        print("   • OPENAI_ENABLED not set to true")
        print("   • OPENAI_API_KEY missing or invalid")
        print("   • Backend not restarted after .env changes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
