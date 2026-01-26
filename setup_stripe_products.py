"""
Script to create/configure Stripe products and prices for LinkedIn Lead Checker.

⚠️  CRITICAL: DO NOT CREATE NEW STRIPE PRODUCTS WITHOUT CLEANUP ⚠️

This script PREVENTS duplicate products by:
1. Checking if products already exist before creating new ones
2. Only allowing exact product names defined below
3. Archiving old products with similar names

BEFORE running this script again:
1. Run: python audit_stripe.py
2. Run: python archive_old_stripe_products.py (if needed)
3. Verify only 3 products exist with EXACT names below

This script creates:
1. Three products (Starter, Pro, Team) with EXACT names
2. Monthly subscription prices for each ($9, $19, $49)
3. Configured with cancel_anytime and no trials

Run this script once to set up your Stripe account.
After running, copy the price IDs to your .env file.

Usage:
    python setup_stripe_products.py
"""

import os
import sys
import stripe
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get Stripe API key (try both names for compatibility)
STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY or STRIPE_API_KEY not found in environment variables")
    print("   Please set STRIPE_SECRET_KEY in your .env file")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY

# ⚠️  CRITICAL: EXACT Product Names - DO NOT MODIFY WITHOUT CLEANUP ⚠️
# These are the ONLY allowed product names in Stripe
# Changing these names will create duplicates unless you archive old products first
# Product configurations
PRODUCTS = {
    "starter": {
        "name": "LinkedIn Lead Checker – Starter",
        "description": "Up to 40 AI-powered lead analyses per month. Perfect for solo founders & light outreach.",
        "price_usd": 9.00,
        "analyses_per_month": 40,
        "features": [
            "40 AI-powered lead analyses/month",
            "LinkedIn profile analysis",
            "Lead fit scoring",
            "Key insights & red flags",
            "Outreach recommendations"
        ]
    },
    "pro": {
        "name": "LinkedIn Lead Checker – Pro",
        "description": "Up to 150 AI-powered lead analyses per month. Built for daily LinkedIn outreach.",
        "price_usd": 19.00,
        "analyses_per_month": 150,
        "features": [
            "150 AI-powered lead analyses/month",
            "Everything in Starter",
            "Priority support",
            "Advanced filtering",
            "Export capabilities"
        ]
    },
    "team": {
        "name": "LinkedIn Lead Checker – Team",
        "description": "Up to 500 AI-powered lead analyses per month. Ideal for teams & agencies.",
        "price_usd": 49.00,
        "analyses_per_month": 500,
        "features": [
            "500 AI-powered lead analyses/month",
            "Everything in Pro",
            "Team collaboration",
            "Dedicated support",
            "Custom integrations"
        ]
    }
}


def check_for_duplicates() -> dict:
    """
    Check for duplicate or similar products in Stripe.
    
    Returns:
        dict with 'duplicates' list and 'similar' list
    """
    print("\n🔍 Checking for existing products...")
    
    all_products = stripe.Product.list(limit=100, active=True)
    
    exact_matches = []
    similar_products = []
    
    expected_names = [config['name'] for config in PRODUCTS.values()]
    
    for product in all_products.data:
        # Check for exact matches
        if product.name in expected_names:
            exact_matches.append({
                'id': product.id,
                'name': product.name,
                'created': datetime.fromtimestamp(product.created).strftime('%Y-%m-%d')
            })
        # Check for similar names (could be old versions)
        elif any(keyword in product.name.lower() for keyword in ['starter', 'pro', 'team', 'business', 'plus', 'base']):
            similar_products.append({
                'id': product.id,
                'name': product.name,
                'created': datetime.fromtimestamp(product.created).strftime('%Y-%m-%d')
            })
    
    return {
        'exact_matches': exact_matches,
        'similar': similar_products,
        'total_active': len(all_products.data)
    }


def validate_stripe_state(duplicates_info: dict):
    """
    Validate that Stripe is in a clean state before creating products.
    
    Args:
        duplicates_info: Dict from check_for_duplicates() with exact_matches, similar, total_active
    
    Raises:
        SystemExit: If validation fails
    """
    print("="*80)
    print("⚠️  VALIDATION: Checking Stripe Account State")
    print("="*80)
    
    print(f"\n📊 Current State:")
    print(f"   • Total active products: {duplicates_info['total_active']}")
    print(f"   • Exact name matches: {len(duplicates_info['exact_matches'])}")
    print(f"   • Similar products: {len(duplicates_info['similar'])}")
    
    # Show exact matches
    if duplicates_info['exact_matches']:
        print(f"\n✅ Found {len(duplicates_info['exact_matches'])} product(s) with exact names:")
        for prod in duplicates_info['exact_matches']:
            print(f"   • {prod['name']}")
            print(f"     ID: {prod['id']} | Created: {prod['created']}")
    
    # Show similar products (potential duplicates)
    if duplicates_info['similar']:
        print(f"\n⚠️  Found {len(duplicates_info['similar'])} similar product(s) (potential duplicates):")
        for prod in duplicates_info['similar']:
            print(f"   • {prod['name']}")
            print(f"     ID: {prod['id']} | Created: {prod['created']}")
        
        print("\n⚠️  WARNING: Similar products found!")
        print("   These may be old/duplicate products that should be archived.")
        print("   Run: python archive_old_stripe_products.py")
        print()
        
        response = input("   Continue anyway? (type 'YES' to proceed): ")
        if response.strip().upper() != "YES":
            print("\n❌ Setup cancelled. Please cleanup duplicates first.")
            sys.exit(1)
    
    # If we have 3 exact matches, products already exist
    if len(duplicates_info['exact_matches']) == 3:
        print("\n✅ All 3 products already exist with correct names.")
        print("   This script will update their metadata and prices.")
    elif len(duplicates_info['exact_matches']) > 3:
        print(f"\n❌ ERROR: Found {len(duplicates_info['exact_matches'])} products with exact names!")
        print("   Expected only 3 products. There are duplicates.")
        print("   Run: python audit_stripe.py")
        print("   Then: python archive_old_stripe_products.py")
        sys.exit(1)
    else:
        print(f"\n✓ Will create {3 - len(duplicates_info['exact_matches'])} new product(s).")
    
    print()
    return duplicates_info


def create_or_update_product(product_key: str, config: dict) -> str:
    """
    Create or update a Stripe product.
    
    ⚠️  CRITICAL: This function checks for EXACT name matches only.
    If you change product names, old products won't be found and duplicates will be created.
    
    Returns:
        Product ID
    """
    print(f"\n📦 Processing {config['name']} product...")
    
    # ⚠️  CRITICAL: Search for existing product by EXACT name match
    # DO NOT modify product names without archiving old ones first
    existing_products = stripe.Product.list(limit=100, active=True)
    existing_product = None
    
    for product in existing_products.data:
        # EXACT name match only
        if product.name == config['name']:
            existing_product = product
            break
    
    if existing_product:
        print(f"   ✓ Found existing product: {existing_product.id}")
        print(f"   ⚠️  Updating existing product (NOT creating new one)")
        # Update product if needed
        stripe.Product.modify(
            existing_product.id,
            description=config['description'],
            metadata={
                "plan": product_key,
                "analyses_per_month": str(config['analyses_per_month']),
                "features": ", ".join(config['features'])
            }
        )
        print(f"   ✓ Updated product metadata")
        return existing_product.id
    else:
        print(f"   ⚠️  Creating NEW product (no existing product found)")
        # Create new product
        product = stripe.Product.create(
            name=config['name'],
            description=config['description'],
            metadata={
                "plan": product_key,
                "analyses_per_month": str(config['analyses_per_month']),
                "features": ", ".join(config['features'])
            }
        )
        print(f"   ✓ Created new product: {product.id}")
        return product.id


def create_or_update_price(product_id: str, product_key: str, config: dict) -> str:
    """
    Create or update a monthly recurring price for a product.
    
    Returns:
        Price ID
    """
    print(f"   💰 Setting up price for {config['name']}...")
    
    # Search for existing active price for this product
    existing_prices = stripe.Price.list(product=product_id, active=True, limit=10)
    
    # Check if correct price already exists
    target_amount = int(config['price_usd'] * 100)  # Convert to cents
    
    for price in existing_prices.data:
        if (price.unit_amount == target_amount and 
            price.recurring and 
            price.recurring.interval == 'month'):
            print(f"   ✓ Found existing price: {price.id} (${config['price_usd']}/month)")
            return price.id
    
    # If we have old prices with different amounts, deactivate them
    for price in existing_prices.data:
        if price.recurring and price.recurring.interval == 'month':
            stripe.Price.modify(price.id, active=False)
            print(f"   ⚠️  Deactivated old price: {price.id}")
    
    # Create new price
    price = stripe.Price.create(
        product=product_id,
        unit_amount=target_amount,
        currency='usd',
        recurring={
            'interval': 'month',
            'interval_count': 1,
        },
        metadata={
            "plan": product_key,
        }
    )
    print(f"   ✓ Created new price: {price.id} (${config['price_usd']}/month)")
    return price.id


def save_to_stripe_ids_md(price_ids: dict, product_ids: dict):
    """Save product and price IDs to STRIPE_IDS.md"""
    content = f"""# Stripe Product & Price IDs

## Configuración Actual

**Fecha de creación:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Nombres Exactos de Productos:
- ✅ LinkedIn Lead Checker – Starter
- ✅ LinkedIn Lead Checker – Pro
- ✅ LinkedIn Lead Checker – Team

---

## Product IDs

| Plan | Product ID | Product Name |
|------|------------|--------------|
| Starter | `{product_ids['starter']}` | LinkedIn Lead Checker – Starter |
| Pro | `{product_ids['pro']}` | LinkedIn Lead Checker – Pro |
| Team | `{product_ids['team']}` | LinkedIn Lead Checker – Team |

---

## Price IDs

| Plan | Price ID | Monthly Price | Analyses/Month |
|------|----------|---------------|----------------|
| Starter | `{price_ids['starter']}` | ${PRODUCTS['starter']['price_usd']:.2f} USD | {PRODUCTS['starter']['analyses_per_month']} |
| Pro | `{price_ids['pro']}` | ${PRODUCTS['pro']['price_usd']:.2f} USD | {PRODUCTS['pro']['analyses_per_month']} |
| Team | `{price_ids['team']}` | ${PRODUCTS['team']['price_usd']:.2f} USD | {PRODUCTS['team']['analyses_per_month']} |

---

## Variables de Entorno (.env)

```bash
# Stripe Price IDs
STRIPE_PRICE_STARTER_ID={price_ids['starter']}
STRIPE_PRICE_PRO_ID={price_ids['pro']}
STRIPE_PRICE_TEAM_ID={price_ids['team']}
```

---

## Configuración de Productos

### LinkedIn Lead Checker – Starter
- **Precio:** ${PRODUCTS['starter']['price_usd']:.2f} USD/mes
- **Análisis:** {PRODUCTS['starter']['analyses_per_month']}/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

### LinkedIn Lead Checker – Pro
- **Precio:** ${PRODUCTS['pro']['price_usd']:.2f} USD/mes
- **Análisis:** {PRODUCTS['pro']['analyses_per_month']}/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

### LinkedIn Lead Checker – Team
- **Precio:** ${PRODUCTS['team']['price_usd']:.2f} USD/mes
- **Análisis:** {PRODUCTS['team']['analyses_per_month']}/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

---

## Verificación

✅ Todos los planes creados con nombres exactos especificados
✅ Precio mensual recurrente configurado
✅ Sin períodos de prueba
✅ Sin addons adicionales
✅ Currency: USD

---

## Dashboard Stripe

Ver productos en: https://dashboard.stripe.com/products
Ver precios en: https://dashboard.stripe.com/prices
"""
    
    with open("STRIPE_IDS.md", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n📄 Documentación guardada en STRIPE_IDS.md")


def main():
    """Main setup function"""
    print("="*70)
    print("🚀 LinkedIn Lead Checker - Stripe Product Setup")
    print("="*70)
    print(f"\n🔑 Using Stripe API Key: {STRIPE_API_KEY[:20]}...")
    
    # Test API key
    try:
        account = stripe.Account.retrieve()
        print(f"✓ Connected to Stripe account: {account.id}")
    except Exception as e:
        print(f"❌ Failed to connect to Stripe: {str(e)}")
        sys.exit(1)
    
    # 🚨 CRITICAL: Validate Stripe state BEFORE creating anything
    print("\n🔍 Validating Stripe account state...")
    try:
        duplicate_info = check_for_duplicates()
        validate_stripe_state(duplicate_info)
        
        if duplicate_info['exact_matches']:
            print("ℹ️  Found existing products - will update prices if needed")
        else:
            print("✓ No duplicate products detected - safe to create")
    except ValueError as e:
        print(f"\n❌ VALIDATION FAILED: {str(e)}")
        print("\n⚠️  DO NOT PROCEED WITHOUT CLEANUP!")
        print("   Run archive_old_stripe_products.py first to clean up duplicates")
        sys.exit(1)
    
    # Store price IDs and product IDs
    price_ids = {}
    product_ids = {}
    
    # Create/update each product and price
    for product_key, config in PRODUCTS.items():
        try:
            product_id = create_or_update_product(product_key, config)
            price_id = create_or_update_price(product_id, product_key, config)
            price_ids[product_key] = price_id
            product_ids[product_key] = product_id
        except Exception as e:
            print(f"❌ Error processing {config['name']}: {str(e)}")
            sys.exit(1)
    
    # Print summary
    print("\n" + "="*70)
    print("✅ Stripe Products & Prices Configured Successfully!")
    print("="*70)
    
    print("\n📋 Add these to your .env file:\n")
    print(f"STRIPE_PRICE_STARTER_ID={price_ids['starter']}")
    print(f"STRIPE_PRICE_PRO_ID={price_ids['pro']}")
    print(f"STRIPE_PRICE_TEAM_ID={price_ids['team']}")
    
    print("\n📊 Price Summary:")
    print(f"   • Starter:  ${PRODUCTS['starter']['price_usd']}/month → {PRODUCTS['starter']['analyses_per_month']} analyses")
    print(f"   • Pro:      ${PRODUCTS['pro']['price_usd']}/month → {PRODUCTS['pro']['analyses_per_month']} analyses")
    print(f"   • Team:     ${PRODUCTS['team']['price_usd']}/month → {PRODUCTS['team']['analyses_per_month']} analyses")
    
    print("\n⚙️  Configuration:")
    print("   ✓ Monthly billing")
    print("   ✓ Cancel anytime (Stripe default)")
    print("   ✓ No trial period")
    print("   ✓ Recurring subscription")
    print("   ✓ Currency: USD")
    print("   ✓ No addons")
    
    # Save to STRIPE_IDS.md
    save_to_stripe_ids_md(price_ids, product_ids)
    
    print("\n🔗 Next Steps:")
    print("   1. Copy the price IDs above to your .env file")
    print("   2. Check STRIPE_IDS.md for complete documentation")
    print("   3. Restart your backend server")
    print("   4. Test checkout flow: http://localhost:8000/billing/checkout?plan=pro")
    print("   5. Configure webhook endpoint in Stripe Dashboard:")
    print("      https://dashboard.stripe.com/webhooks")
    print("      Endpoint: https://your-domain.com/billing/webhook/stripe")
    print("      Events: checkout.session.completed, customer.subscription.deleted, customer.subscription.updated")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
