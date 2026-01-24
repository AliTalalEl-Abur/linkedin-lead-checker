"""
Script to create/configure Stripe products and prices for LinkedIn Lead Checker.

This script creates:
1. Three products (Starter, Pro, Business)
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

# Load environment variables
load_dotenv()

# Get Stripe API key (try both names for compatibility)
STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY or STRIPE_API_KEY not found in environment variables")
    print("   Please set STRIPE_SECRET_KEY in your .env file")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY

# Product configurations
PRODUCTS = {
    "starter": {
        "name": "Starter",
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
        "name": "Pro",
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
    "business": {
        "name": "Business",
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


def create_or_update_product(product_key: str, config: dict) -> str:
    """
    Create or update a Stripe product.
    
    Returns:
        Product ID
    """
    print(f"\n📦 Processing {config['name']} product...")
    
    # Search for existing product by name
    existing_products = stripe.Product.list(limit=100)
    existing_product = None
    
    for product in existing_products.data:
        if product.name == config['name']:
            existing_product = product
            break
    
    if existing_product:
        print(f"   ✓ Found existing product: {existing_product.id}")
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
    
    # Store price IDs
    price_ids = {}
    
    # Create/update each product and price
    for product_key, config in PRODUCTS.items():
        try:
            product_id = create_or_update_product(product_key, config)
            price_id = create_or_update_price(product_id, product_key, config)
            price_ids[product_key] = price_id
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
    print(f"STRIPE_PRICE_BUSINESS_ID={price_ids['business']}")
    
    print("\n📊 Price Summary:")
    print(f"   • Starter:  ${PRODUCTS['starter']['price_usd']}/month → {PRODUCTS['starter']['analyses_per_month']} analyses")
    print(f"   • Pro:      ${PRODUCTS['pro']['price_usd']}/month → {PRODUCTS['pro']['analyses_per_month']} analyses")
    print(f"   • Business: ${PRODUCTS['business']['price_usd']}/month → {PRODUCTS['business']['analyses_per_month']} analyses")
    
    print("\n⚙️  Configuration:")
    print("   ✓ Monthly billing")
    print("   ✓ Cancel anytime (Stripe default)")
    print("   ✓ No trial period")
    print("   ✓ Recurring subscription")
    
    print("\n🔗 Next Steps:")
    print("   1. Copy the price IDs above to your .env file")
    print("   2. Restart your backend server")
    print("   3. Test checkout flow: http://localhost:8000/billing/checkout?plan=pro")
    print("   4. Configure webhook endpoint in Stripe Dashboard:")
    print("      https://dashboard.stripe.com/webhooks")
    print("      Endpoint: https://your-domain.com/billing/webhook/stripe")
    print("      Events: checkout.session.completed, customer.subscription.deleted, customer.subscription.updated")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
