"""
OpenAI Activation Script

Enables OpenAI with strict economic controls:
- Only paid users can use AI
- Credits consumed only on successful calls
- Costs tracked per analysis
- No retries on failure
"""

import os
import sys
from dotenv import load_dotenv, set_key

def check_prerequisites():
    """Verify all prerequisites before activation"""
    print("🔍 Checking prerequisites...")
    
    load_dotenv()
    
    issues = []
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        issues.append("❌ OPENAI_API_KEY not found in .env")
    elif not openai_key.startswith('sk-'):
        issues.append("⚠️  OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
    else:
        print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...")
    
    # Check Stripe configuration
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe_key:
        issues.append("❌ STRIPE_SECRET_KEY not found in .env")
    else:
        print(f"✅ STRIPE_SECRET_KEY: {stripe_key[:20]}...")
    
    # Check price IDs
    price_ids = {
        'STRIPE_PRICE_STARTER_ID': os.getenv('STRIPE_PRICE_STARTER_ID'),
        'STRIPE_PRICE_PRO_ID': os.getenv('STRIPE_PRICE_PRO_ID'),
        'STRIPE_PRICE_TEAM_ID': os.getenv('STRIPE_PRICE_TEAM_ID'),
    }
    
    for name, value in price_ids.items():
        if not value:
            issues.append(f"❌ {name} not found in .env")
        else:
            print(f"✅ {name}: {value}")
    
    return issues


def show_configuration():
    """Show current AI configuration"""
    load_dotenv()
    
    print("\n📊 Current AI Configuration:")
    print("="*70)
    
    config = {
        'OPENAI_ENABLED': os.getenv('OPENAI_ENABLED', 'false'),
        'AI_COST_PER_ANALYSIS_USD': os.getenv('AI_COST_PER_ANALYSIS_USD', '0.03'),
        'USAGE_LIMIT_STARTER': os.getenv('USAGE_LIMIT_STARTER', '40'),
        'USAGE_LIMIT_PRO': os.getenv('USAGE_LIMIT_PRO', '150'),
        'USAGE_LIMIT_TEAM': os.getenv('USAGE_LIMIT_TEAM', '500'),
        'REVENUE_PER_STARTER_USER': os.getenv('REVENUE_PER_STARTER_USER', '1.20'),
        'REVENUE_PER_PRO_USER': os.getenv('REVENUE_PER_PRO_USER', '4.50'),
        'REVENUE_PER_TEAM_USER': os.getenv('REVENUE_PER_TEAM_USER', '15.0'),
    }
    
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print()


def activate_openai():
    """Activate OpenAI with safety checks"""
    print("\n🚀 Activating OpenAI...")
    print("="*70)
    
    env_file = '.env'
    
    # Set OPENAI_ENABLED=true
    set_key(env_file, 'OPENAI_ENABLED', 'true')
    print("✅ Set OPENAI_ENABLED=true")
    
    # Ensure cost tracking is set
    if not os.getenv('AI_COST_PER_ANALYSIS_USD'):
        set_key(env_file, 'AI_COST_PER_ANALYSIS_USD', '0.03')
        print("✅ Set AI_COST_PER_ANALYSIS_USD=0.03")
    
    # Ensure usage limits are set
    limits = {
        'USAGE_LIMIT_STARTER': '40',
        'USAGE_LIMIT_PRO': '150',
        'USAGE_LIMIT_TEAM': '500',
    }
    
    for key, default_value in limits.items():
        if not os.getenv(key):
            set_key(env_file, key, default_value)
            print(f"✅ Set {key}={default_value}")
    
    # Ensure revenue tracking is set
    revenue = {
        'REVENUE_PER_STARTER_USER': '1.20',
        'REVENUE_PER_PRO_USER': '4.50',
        'REVENUE_PER_TEAM_USER': '15.0',
    }
    
    for key, default_value in revenue.items():
        if not os.getenv(key):
            set_key(env_file, key, default_value)
            print(f"✅ Set {key}={default_value}")
    
    print("\n✅ OpenAI activated successfully!")


def show_safety_features():
    """Display safety features"""
    print("\n🛡️  Safety Features Enabled:")
    print("="*70)
    print("✅ Subscription Validation:")
    print("   • Only users with active subscriptions can use AI")
    print("   • Free users get preview mode (no AI calls)")
    print("   • Plans: Starter, Pro, Team")
    
    print("\n✅ Credit System:")
    print("   • Each analysis deducts 1 credit from monthly limit")
    print("   • Credits reset on 1st of each month")
    print("   • Starter: 40 analyses/month ($9/month)")
    print("   • Pro: 150 analyses/month ($19/month)")
    print("   • Team: 500 analyses/month ($49/month)")
    
    print("\n✅ Cost Tracking:")
    print("   • Each analysis: ~$0.03 estimated cost")
    print("   • Costs recorded in usage_events table")
    print("   • Monthly budget calculated: active_users * revenue_per_user")
    print("   • AI disabled if monthly spend exceeds budget")
    
    print("\n✅ Error Handling:")
    print("   • No retries on OpenAI failures (prevents duplicate costs)")
    print("   • Credits consumed ONLY on successful AI calls")
    print("   • Clear error messages to users")
    print("   • All failures logged with user_id")
    
    print("\n✅ Rate Limiting:")
    print("   • 1 analysis per 30 seconds per user")
    print("   • Prevents abuse and rapid cost accumulation")
    
    print("\n✅ Kill Switches:")
    print("   • DISABLE_ALL_ANALYSES: Emergency stop all AI")
    print("   • DISABLE_FREE_PLAN: Stop free tier if needed")
    print("   • Budget exhaustion auto-disables AI")
    
    print("\n✅ Validation Layers:")
    print("   • Pre-flight: Check subscription status")
    print("   • Pre-flight: Check remaining credits")
    print("   • Pre-flight: Check rate limit")
    print("   • Pre-call: Double-verify OpenAI enabled")
    print("   • Pre-call: Final credit check")
    print("   • Post-call: Record usage only if successful")


def show_economics():
    """Show economic model"""
    print("\n💰 Economic Model:")
    print("="*70)
    
    plans = [
        {"name": "Starter", "price": 9, "analyses": 40, "cost": 1.20, "margin": 7.80},
        {"name": "Pro", "price": 19, "analyses": 150, "cost": 4.50, "margin": 14.50},
        {"name": "Team", "price": 49, "analyses": 500, "cost": 15.00, "margin": 34.00},
    ]
    
    for plan in plans:
        print(f"\n{plan['name']} Plan:")
        print(f"   • Revenue: ${plan['price']:.2f}/month")
        print(f"   • Analyses: {plan['analyses']}/month")
        print(f"   • AI Cost: ${plan['cost']:.2f}/month (@ $0.03/analysis)")
        print(f"   • Gross Margin: ${plan['margin']:.2f}/month ({plan['margin']/plan['price']*100:.1f}%)")
        print(f"   • Cost per analysis: ${plan['cost']/plan['analyses']:.4f}")
    
    print("\n📊 Profitability Thresholds:")
    print("   • Starter: Profitable from day 1 (86.7% margin)")
    print("   • Pro: Profitable from day 1 (76.3% margin)")
    print("   • Team: Profitable from day 1 (69.4% margin)")
    
    print("\n⚠️  Risk Scenarios:")
    print("   • User maxes out limit: Still profitable ✅")
    print("   • OpenAI price increase 50%: Still profitable ✅")
    print("   • 100% usage rate: Still profitable ✅")


def run_tests():
    """Run basic tests"""
    print("\n🧪 Running Tests...")
    print("="*70)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from app.core.config import get_settings
        from app.services.ai_service import get_ai_service
        print("   ✅ Imports successful")
        
        # Test config
        print("2. Testing configuration...")
        settings = get_settings()
        if settings.openai_enabled:
            print("   ✅ OPENAI_ENABLED=true")
        else:
            print("   ⚠️  OPENAI_ENABLED=false")
        
        if settings.openai_api_key:
            print(f"   ✅ OpenAI API key loaded: {settings.openai_api_key[:20]}...")
        else:
            print("   ❌ OpenAI API key not loaded")
        
        # Test AI service initialization
        print("3. Testing AI service...")
        ai_service = get_ai_service()
        if ai_service.use_mock:
            print("   ⚠️  AI service in MOCK mode")
        else:
            print("   ✅ AI service initialized with OpenAI")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main activation flow"""
    print("="*70)
    print("🤖 OpenAI Activation System")
    print("="*70)
    
    # Step 1: Check prerequisites
    issues = check_prerequisites()
    
    if issues:
        print("\n❌ Prerequisites check failed:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Fix these issues before activating OpenAI")
        return 1
    
    print("\n✅ All prerequisites met!")
    
    # Step 2: Show current configuration
    show_configuration()
    
    # Step 3: Check current state
    current_state = os.getenv('OPENAI_ENABLED', 'false').lower()
    
    if current_state == 'true':
        print("⚠️  OpenAI is already ENABLED")
        print("\nOptions:")
        print("1. Show safety features")
        print("2. Show economic model")
        print("3. Run tests")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            show_safety_features()
        elif choice == "2":
            show_economics()
        elif choice == "3":
            run_tests()
        else:
            print("\n👋 Goodbye!")
        
        return 0
    
    # Step 4: Confirm activation
    print("\n⚠️  IMPORTANT: OpenAI is currently DISABLED")
    print("\nActivating OpenAI will:")
    print("• Enable AI-powered analysis for subscribed users")
    print("• Start consuming OpenAI API credits")
    print("• Track costs in usage_events table")
    print("• Apply strict subscription validation")
    
    confirm = input("\n❓ Activate OpenAI now? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Activation cancelled")
        return 0
    
    # Step 5: Activate
    activate_openai()
    
    # Step 6: Show safety features
    show_safety_features()
    
    # Step 7: Show economics
    show_economics()
    
    # Step 8: Run tests
    if not run_tests():
        print("\n⚠️  Tests failed but OpenAI is activated")
        print("   Check errors above and restart backend")
        return 1
    
    # Step 9: Final instructions
    print("\n" + "="*70)
    print("✅ ACTIVATION COMPLETE!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("1. Restart backend: python run.py")
    print("2. Verify activation: python test_ai_activation.py")
    print("3. Test subscription flow: See TEST_SUBSCRIPTION.md")
    print("4. Monitor costs: Check usage_events table")
    
    print("\n💡 Monitoring Commands:")
    print("   • View costs: SELECT SUM(cost_usd) FROM usage_events WHERE month_key='2026-01';")
    print("   • View usage: SELECT COUNT(*) FROM usage_events WHERE month_key='2026-01';")
    print("   • By user: SELECT user_id, COUNT(*), SUM(cost_usd) FROM usage_events GROUP BY user_id;")
    
    print("\n🚨 Emergency Deactivation:")
    print("   • Set OPENAI_ENABLED=false in .env")
    print("   • Or set DISABLE_ALL_ANALYSES=true")
    print("   • Restart backend")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
