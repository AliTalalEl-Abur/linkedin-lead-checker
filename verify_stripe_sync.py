"""
Stripe Synchronization Verification Script

Verifies that:
1. Backend configuration matches Stripe
2. Exactly 3 active plans exist
3. Prices match between backend and Stripe
4. No duplicate products exist
5. All price_ids are valid and active

Usage:
    python verify_stripe_sync.py
"""

import os
import sys
from dotenv import load_dotenv
import stripe
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

# Configuration
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
EXPECTED_PLANS = {
    'starter': {
        'name': 'LinkedIn Lead Checker – Starter',
        'price_env': 'STRIPE_PRICE_STARTER_ID',
        'expected_price': 9.00,
        'analyses': 40
    },
    'pro': {
        'name': 'LinkedIn Lead Checker – Pro',
        'price_env': 'STRIPE_PRICE_PRO_ID',
        'expected_price': 19.00,
        'analyses': 150
    },
    'team': {
        'name': 'LinkedIn Lead Checker – Team',
        'price_env': 'STRIPE_PRICE_TEAM_ID',
        'expected_price': 49.00,
        'analyses': 500
    }
}


class StripeVerificationError(Exception):
    """Custom exception for verification failures"""
    pass


class StripeVerifier:
    """Verifies Stripe configuration and synchronization"""
    
    def __init__(self):
        if not STRIPE_API_KEY:
            raise ValueError("STRIPE_SECRET_KEY not found in .env")
        stripe.api_key = STRIPE_API_KEY
        self.errors = []
        self.warnings = []
        self.backend_config = {}
        self.stripe_products = []
        self.stripe_prices = {}
    
    def verify_all(self) -> bool:
        """
        Run all verification checks.
        
        Returns:
            True if all checks pass, False otherwise
        """
        print("="*80)
        print("🔍 Stripe Synchronization Verification")
        print("="*80)
        
        try:
            # Step 1: Load backend configuration
            print("\n1️⃣ Loading backend configuration...")
            self.load_backend_config()
            
            # Step 2: Load Stripe state
            print("\n2️⃣ Loading Stripe data...")
            self.load_stripe_data()
            
            # Step 3: Verify product count
            print("\n3️⃣ Verifying product count...")
            self.verify_product_count()
            
            # Step 4: Verify product names
            print("\n4️⃣ Verifying product names...")
            self.verify_product_names()
            
            # Step 5: Verify prices match
            print("\n5️⃣ Verifying prices...")
            self.verify_prices()
            
            # Step 6: Check for duplicates
            print("\n6️⃣ Checking for duplicates...")
            self.check_duplicates()
            
            # Step 7: Verify price_ids are active
            print("\n7️⃣ Verifying price_ids are active...")
            self.verify_price_ids_active()
            
            # Step 8: Verify backend/Stripe sync
            print("\n8️⃣ Verifying backend/Stripe synchronization...")
            self.verify_backend_stripe_sync()
            
            # Generate report
            self.print_report()
            
            return len(self.errors) == 0
            
        except Exception as e:
            print(f"\n❌ Verification failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_backend_config(self):
        """Load configuration from .env"""
        for plan_key, plan_info in EXPECTED_PLANS.items():
            price_id = os.getenv(plan_info['price_env'])
            if price_id:
                self.backend_config[plan_key] = {
                    'price_id': price_id,
                    'expected_name': plan_info['name'],
                    'expected_price': plan_info['expected_price'],
                    'analyses': plan_info['analyses']
                }
                print(f"   ✓ Loaded {plan_key}: {price_id}")
            else:
                self.errors.append(f"Missing env var: {plan_info['price_env']}")
                print(f"   ❌ Missing: {plan_info['price_env']}")
        
        if len(self.backend_config) != 3:
            raise StripeVerificationError(
                f"Expected 3 plans in .env, found {len(self.backend_config)}"
            )
    
    def load_stripe_data(self):
        """Load products and prices from Stripe"""
        # Load all products
        products = stripe.Product.list(limit=100)
        self.stripe_products = products.data
        
        active_count = sum(1 for p in self.stripe_products if p.active)
        archived_count = sum(1 for p in self.stripe_products if not p.active)
        
        print(f"   ✓ Loaded {len(self.stripe_products)} products")
        print(f"     • Active: {active_count}")
        print(f"     • Archived: {archived_count}")
        
        # Load prices for active products
        for product in self.stripe_products:
            if product.active:
                prices = stripe.Price.list(product=product.id, limit=100)
                self.stripe_prices[product.id] = prices.data
                active_prices = [p for p in prices.data if p.active]
                print(f"   ✓ Product '{product.name}': {len(active_prices)} active price(s)")
    
    def verify_product_count(self):
        """Verify exactly 3 active products exist"""
        active_products = [p for p in self.stripe_products if p.active]
        
        if len(active_products) != 3:
            self.errors.append(
                f"Expected exactly 3 active products, found {len(active_products)}"
            )
            print(f"   ❌ Found {len(active_products)} active products (expected 3)")
        else:
            print(f"   ✅ Exactly 3 active products")
    
    def verify_product_names(self):
        """Verify product names match expected names"""
        active_products = [p for p in self.stripe_products if p.active]
        expected_names = [info['expected_name'] for info in self.backend_config.values()]
        
        for product in active_products:
            if product.name in expected_names:
                print(f"   ✅ Found: {product.name}")
            else:
                self.warnings.append(
                    f"Unexpected product name: {product.name}"
                )
                print(f"   ⚠️  Unexpected: {product.name}")
        
        # Check if all expected names are present
        found_names = [p.name for p in active_products]
        for expected_name in expected_names:
            if expected_name not in found_names:
                self.errors.append(f"Missing product: {expected_name}")
                print(f"   ❌ Missing: {expected_name}")
    
    def verify_prices(self):
        """Verify prices match expected values"""
        active_products = [p for p in self.stripe_products if p.active]
        
        for product in active_products:
            # Find matching plan in backend config
            matching_plan = None
            for plan_key, config in self.backend_config.items():
                if config['expected_name'] == product.name:
                    matching_plan = (plan_key, config)
                    break
            
            if not matching_plan:
                continue
            
            plan_key, plan_config = matching_plan
            
            # Get active prices for this product
            prices = self.stripe_prices.get(product.id, [])
            active_prices = [p for p in prices if p.active]
            
            if len(active_prices) == 0:
                self.errors.append(f"No active price for {product.name}")
                print(f"   ❌ {product.name}: No active price")
            elif len(active_prices) > 1:
                self.warnings.append(f"Multiple active prices for {product.name}")
                print(f"   ⚠️  {product.name}: {len(active_prices)} active prices")
            else:
                price = active_prices[0]
                actual_price = price.unit_amount / 100
                expected_price = plan_config['expected_price']
                
                if actual_price == expected_price:
                    print(f"   ✅ {product.name}: ${actual_price:.2f}/month (correct)")
                else:
                    self.errors.append(
                        f"{product.name}: Price mismatch - "
                        f"expected ${expected_price:.2f}, got ${actual_price:.2f}"
                    )
                    print(f"   ❌ {product.name}: Expected ${expected_price:.2f}, got ${actual_price:.2f}")
    
    def check_duplicates(self):
        """Check for duplicate products"""
        active_products = [p for p in self.stripe_products if p.active]
        names = [p.name for p in active_products]
        
        # Check for exact duplicates
        duplicate_names = [name for name in names if names.count(name) > 1]
        unique_duplicates = list(set(duplicate_names))
        
        if unique_duplicates:
            for dup_name in unique_duplicates:
                count = names.count(dup_name)
                self.errors.append(f"Duplicate product: {dup_name} ({count} instances)")
                print(f"   ❌ Duplicate: {dup_name} ({count} instances)")
        else:
            print(f"   ✅ No duplicate products")
        
        # Check for similar names (potential duplicates)
        keywords = ['starter', 'pro', 'team', 'business', 'plus', 'base']
        similar_products = []
        
        for product in active_products:
            # Check if product name is NOT in expected names
            expected_names = [info['expected_name'] for info in self.backend_config.values()]
            if product.name not in expected_names:
                # But contains plan keywords
                if any(keyword in product.name.lower() for keyword in keywords):
                    similar_products.append(product.name)
        
        if similar_products:
            for similar in similar_products:
                self.warnings.append(f"Similar product name: {similar}")
                print(f"   ⚠️  Similar: {similar} (may need archiving)")
    
    def verify_price_ids_active(self):
        """Verify all price_ids in backend config are active in Stripe"""
        for plan_key, config in self.backend_config.items():
            price_id = config['price_id']
            
            try:
                price = stripe.Price.retrieve(price_id)
                
                if not price.active:
                    self.errors.append(f"{plan_key}: price_id {price_id} is not active")
                    print(f"   ❌ {plan_key}: price_id is INACTIVE")
                else:
                    print(f"   ✅ {plan_key}: price_id is active")
                    
            except stripe.error.InvalidRequestError:
                self.errors.append(f"{plan_key}: price_id {price_id} not found in Stripe")
                print(f"   ❌ {plan_key}: price_id NOT FOUND in Stripe")
    
    def verify_backend_stripe_sync(self):
        """Verify backend price_ids match Stripe products"""
        for plan_key, config in self.backend_config.items():
            backend_price_id = config['price_id']
            expected_name = config['expected_name']
            
            # Find product in Stripe
            matching_products = [
                p for p in self.stripe_products 
                if p.active and p.name == expected_name
            ]
            
            if not matching_products:
                self.errors.append(f"{plan_key}: Product '{expected_name}' not found in Stripe")
                print(f"   ❌ {plan_key}: Product not found in Stripe")
                continue
            
            if len(matching_products) > 1:
                self.errors.append(f"{plan_key}: Multiple products with name '{expected_name}'")
                print(f"   ❌ {plan_key}: Multiple products found")
                continue
            
            product = matching_products[0]
            
            # Get active prices for this product
            prices = self.stripe_prices.get(product.id, [])
            active_prices = [p for p in prices if p.active]
            
            if not active_prices:
                self.errors.append(f"{plan_key}: No active prices in Stripe")
                print(f"   ❌ {plan_key}: No active prices")
                continue
            
            # Check if backend price_id matches Stripe
            stripe_price_ids = [p.id for p in active_prices]
            
            if backend_price_id in stripe_price_ids:
                print(f"   ✅ {plan_key}: Backend ↔ Stripe synchronized")
            else:
                self.errors.append(
                    f"{plan_key}: Backend price_id {backend_price_id} "
                    f"doesn't match Stripe prices {stripe_price_ids}"
                )
                print(f"   ❌ {plan_key}: Backend/Stripe MISMATCH")
    
    def print_report(self):
        """Print verification report"""
        print("\n" + "="*80)
        print("📊 Verification Report")
        print("="*80)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"   • Active Products: {len([p for p in self.stripe_products if p.active])}")
        print(f"   • Backend Plans: {len(self.backend_config)}")
        print(f"   • Errors: {len(self.errors)}")
        print(f"   • Warnings: {len(self.warnings)}")
        
        print("\n" + "="*80)
        
        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("✅ VERIFICATION PASSED - All checks successful!")
            print("="*80)
            return True
        elif len(self.errors) == 0:
            print("⚠️  VERIFICATION PASSED WITH WARNINGS")
            print("   Action recommended but not required")
            print("="*80)
            return True
        else:
            print("❌ VERIFICATION FAILED")
            print("   Action required before production deployment")
            print("="*80)
            return False


def main():
    """Main verification function"""
    try:
        verifier = StripeVerifier()
        success = verifier.verify_all()
        
        if success:
            print("\n🎉 System is ready for production!")
            sys.exit(0)
        else:
            print("\n🚨 Fix errors before deploying to production!")
            print("\nRecommended actions:")
            print("   1. Run: python archive_old_stripe_products.py")
            print("   2. Run: python setup_stripe_products.py")
            print("   3. Update .env with correct price_ids")
            print("   4. Run this script again")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
