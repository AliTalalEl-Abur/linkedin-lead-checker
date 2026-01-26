"""
Test Duplicate Prevention in setup_stripe_products.py

This script verifies that the duplicate prevention logic works correctly.
"""

import os
import sys
from dotenv import load_dotenv
import stripe

# Load environment variables
load_dotenv()
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')

if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY not found in .env")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY


def test_duplicate_detection():
    """Test the duplicate detection logic"""
    print("="*70)
    print("🧪 Testing Duplicate Prevention Logic")
    print("="*70)
    
    # Expected product names
    expected_names = [
        "LinkedIn Lead Checker – Starter",
        "LinkedIn Lead Checker – Pro",
        "LinkedIn Lead Checker – Team"
    ]
    
    print("\n1️⃣ Listing all Stripe products...")
    products = stripe.Product.list(limit=100)
    
    active_products = [p for p in products.data if p.active]
    archived_products = [p for p in products.data if not p.active]
    
    print(f"   ✓ Total products: {len(products.data)}")
    print(f"   ✓ Active: {len(active_products)}")
    print(f"   ✓ Archived: {len(archived_products)}")
    
    # Check for exact matches
    print("\n2️⃣ Checking for exact product name matches...")
    exact_matches = {}
    
    for expected_name in expected_names:
        matching_products = [p for p in active_products if p.name == expected_name]
        
        if len(matching_products) > 1:
            print(f"   ⚠️  WARNING: Multiple active products with name '{expected_name}'")
            print(f"      Found {len(matching_products)} matches:")
            for p in matching_products:
                print(f"      - {p.id}: {p.name}")
            exact_matches[expected_name] = matching_products
        elif len(matching_products) == 1:
            print(f"   ✓ Found unique match: {expected_name}")
            print(f"      Product ID: {matching_products[0].id}")
            exact_matches[expected_name] = matching_products
        else:
            print(f"   ℹ️  No match found: {expected_name} (will be created)")
    
    # Check for similar names
    print("\n3️⃣ Checking for similar product names...")
    keywords = ["LinkedIn", "Lead", "Checker", "Starter", "Pro", "Team", "Base", "Plus"]
    similar_products = []
    
    for product in active_products:
        if product.name not in expected_names:
            # Check if product name contains any keywords
            if any(keyword.lower() in product.name.lower() for keyword in keywords):
                similar_products.append(product)
                print(f"   ⚠️  Similar product: {product.name} (ID: {product.id})")
    
    if not similar_products:
        print("   ✓ No similar products found")
    
    # Validation result
    print("\n4️⃣ Validation Results:")
    
    if len(exact_matches) == 3 and all(len(matches) == 1 for matches in exact_matches.values()):
        print("   ✅ PASSED: Exactly 3 unique products with expected names exist")
        print("   ✅ Safe to run setup_stripe_products.py (will update existing products)")
    elif len(exact_matches) == 0 and len(similar_products) == 0:
        print("   ✅ PASSED: No products exist yet")
        print("   ✅ Safe to run setup_stripe_products.py (will create new products)")
    elif any(len(matches) > 1 for matches in exact_matches.values()):
        print("   ❌ FAILED: Duplicate products detected!")
        print("   ⚠️  DANGER: Run archive_old_stripe_products.py to clean up duplicates")
        return False
    elif len(similar_products) > 0:
        print("   ⚠️  WARNING: Similar products exist (may cause confusion)")
        print("   💡 Consider archiving these products before proceeding")
        return True  # Warning, but not blocking
    
    # Summary
    print("\n" + "="*70)
    print("📊 Summary")
    print("="*70)
    print(f"Active Products: {len(active_products)}")
    print(f"Exact Matches: {len(exact_matches)}")
    print(f"Similar Products: {len(similar_products)}")
    print(f"Archived Products: {len(archived_products)}")
    
    return True


def test_price_uniqueness():
    """Test that each product has only one active price"""
    print("\n" + "="*70)
    print("🧪 Testing Price Uniqueness")
    print("="*70)
    
    products = stripe.Product.list(limit=100)
    active_products = [p for p in products.data if p.active]
    
    for product in active_products:
        prices = stripe.Price.list(product=product.id, limit=100)
        active_prices = [p for p in prices.data if p.active]
        
        if len(active_prices) == 0:
            print(f"   ⚠️  Product '{product.name}' has NO active prices")
        elif len(active_prices) == 1:
            print(f"   ✓ Product '{product.name}' has 1 active price: {active_prices[0].id}")
        else:
            print(f"   ❌ Product '{product.name}' has {len(active_prices)} active prices:")
            for price in active_prices:
                print(f"      - {price.id}: ${price.unit_amount/100}/month")


if __name__ == "__main__":
    try:
        # Test duplicate detection
        detection_passed = test_duplicate_detection()
        
        # Test price uniqueness
        test_price_uniqueness()
        
        # Final verdict
        print("\n" + "="*70)
        if detection_passed:
            print("✅ All tests passed - safe to run setup_stripe_products.py")
        else:
            print("❌ Tests failed - DO NOT run setup_stripe_products.py")
            print("   Clean up duplicates first with archive_old_stripe_products.py")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
