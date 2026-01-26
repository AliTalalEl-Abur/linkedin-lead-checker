"""
Stripe Audit Script - Analiza todos los productos y precios en Stripe
Genera un reporte detallado en STRIPE_AUDIT.md
"""

import os
import sys
from datetime import datetime
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Stripe API key
STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY not found in .env")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY

# Get configured price IDs from .env
CONFIGURED_PRICES = {
    'starter': os.getenv("STRIPE_PRICE_STARTER_ID"),
    'pro': os.getenv("STRIPE_PRICE_PRO_ID"),
    'team': os.getenv("STRIPE_PRICE_TEAM_ID"),
}

def audit_stripe():
    """Audit all Stripe products and prices."""
    
    print("🔍 Auditing Stripe configuration...")
    print(f"API Key: {STRIPE_API_KEY[:20]}...")
    print()
    
    # Get all products
    products = stripe.Product.list(limit=100)
    
    audit_data = []
    
    for product in products.data:
        # Get all prices for this product
        prices = stripe.Price.list(product=product.id, limit=100)
        
        product_info = {
            'product_id': product.id,
            'product_name': product.name,
            'product_active': product.active,
            'created': datetime.fromtimestamp(product.created).strftime('%Y-%m-%d'),
            'prices': []
        }
        
        for price in prices.data:
            # Check if this price is configured in backend
            used_as = None
            for plan, price_id in CONFIGURED_PRICES.items():
                if price.id == price_id:
                    used_as = plan
                    break
            
            price_info = {
                'price_id': price.id,
                'active': price.active,
                'amount': price.unit_amount / 100 if price.unit_amount else 0,
                'currency': price.currency.upper(),
                'interval': price.recurring.interval if price.recurring else 'one-time',
                'created': datetime.fromtimestamp(price.created).strftime('%Y-%m-%d'),
                'used_as': used_as
            }
            product_info['prices'].append(price_info)
        
        audit_data.append(product_info)
    
    return audit_data, products

def generate_markdown_report(audit_data):
    """Generate markdown audit report."""
    
    report = []
    report.append("# 🔍 Stripe Configuration Audit Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**API Key**: {STRIPE_API_KEY[:20]}...")
    report.append(f"**Mode**: {'Test' if 'test' in STRIPE_API_KEY else 'Live'}")
    
    # Backend Configuration
    report.append("\n## 📋 Backend Configuration (.env)")
    report.append("\n| Plan | Price ID | Status |")
    report.append("|------|----------|--------|")
    
    for plan, price_id in CONFIGURED_PRICES.items():
        status = "✅ Set" if price_id else "❌ Missing"
        report.append(f"| **{plan.capitalize()}** | `{price_id or 'NOT SET'}` | {status} |")
    
    # All Products & Prices
    report.append("\n## 📦 All Products in Stripe")
    
    total_products = len(audit_data)
    active_products = sum(1 for p in audit_data if p['product_active'])
    total_prices = sum(len(p['prices']) for p in audit_data)
    active_prices = sum(len([pr for pr in p['prices'] if pr['active']]) for p in audit_data)
    
    report.append(f"\n**Summary**:")
    report.append(f"- Total Products: {total_products} ({active_products} active, {total_products - active_products} archived)")
    report.append(f"- Total Prices: {total_prices} ({active_prices} active, {total_prices - active_prices} inactive)")
    
    for product in audit_data:
        report.append(f"\n### {product['product_name']}")
        report.append(f"\n- **Product ID**: `{product['product_id']}`")
        report.append(f"- **Status**: {'✅ Active' if product['product_active'] else '⚠️ Archived'}")
        report.append(f"- **Created**: {product['created']}")
        report.append(f"- **Prices**: {len(product['prices'])}")
        
        if product['prices']:
            report.append("\n| Price ID | Amount | Interval | Status | Backend | Created |")
            report.append("|----------|--------|----------|--------|---------|---------|")
            
            for price in product['prices']:
                status_emoji = "✅" if price['active'] else "❌"
                backend_usage = f"**{price['used_as'].upper()}**" if price['used_as'] else "-"
                report.append(
                    f"| `{price['price_id']}` | "
                    f"${price['amount']:.2f} {price['currency']} | "
                    f"{price['interval']} | "
                    f"{status_emoji} {'Active' if price['active'] else 'Inactive'} | "
                    f"{backend_usage} | "
                    f"{price['created']} |"
                )
    
    # Analysis
    report.append("\n## 🔎 Analysis")
    
    # Unused prices
    unused_prices = []
    for product in audit_data:
        for price in product['prices']:
            if not price['used_as'] and price['active']:
                unused_prices.append({
                    'product': product['product_name'],
                    'price_id': price['price_id'],
                    'amount': price['amount']
                })
    
    if unused_prices:
        report.append("\n### ⚠️ Active Prices NOT Used in Backend")
        report.append("\n| Product | Price ID | Amount |")
        report.append("|---------|----------|--------|")
        for up in unused_prices:
            report.append(f"| {up['product']} | `{up['price_id']}` | ${up['amount']:.2f} |")
        report.append("\n**Recommendation**: Review if these should be deactivated or added to backend config.")
    else:
        report.append("\n### ✅ All Active Prices are Configured")
        report.append("\nNo unused active prices found.")
    
    # Duplicates
    report.append("\n### 🔍 Duplicate Products (Same Name)")
    
    product_names = {}
    for product in audit_data:
        name = product['product_name']
        if name not in product_names:
            product_names[name] = []
        product_names[name].append(product)
    
    duplicates = {name: products for name, products in product_names.items() if len(products) > 1}
    
    if duplicates:
        for name, products in duplicates.items():
            report.append(f"\n**{name}**: {len(products)} products found")
            for p in products:
                status = "✅ Active" if p['product_active'] else "⚠️ Archived"
                report.append(f"- `{p['product_id']}` - {status} - {len(p['prices'])} prices - Created: {p['created']}")
    else:
        report.append("\n✅ No duplicate product names found.")
    
    # Missing configuration
    report.append("\n### 🚨 Configuration Issues")
    
    issues = []
    
    # Check if configured prices exist and are active
    for plan, price_id in CONFIGURED_PRICES.items():
        if not price_id:
            issues.append(f"❌ **{plan.capitalize()}**: Price ID not set in .env")
            continue
        
        found = False
        for product in audit_data:
            for price in product['prices']:
                if price['price_id'] == price_id:
                    found = True
                    if not price['active']:
                        issues.append(f"⚠️ **{plan.capitalize()}**: Price `{price_id}` is INACTIVE in Stripe")
                    break
            if found:
                break
        
        if not found:
            issues.append(f"❌ **{plan.capitalize()}**: Price `{price_id}` NOT FOUND in Stripe")
    
    if issues:
        for issue in issues:
            report.append(f"\n{issue}")
    else:
        report.append("\n✅ All configured prices are active and valid.")
    
    # Recommendations
    report.append("\n## 💡 Recommendations")
    report.append("\n1. **Keep**: Products/prices that are configured in backend and active")
    report.append("2. **Archive**: Old products/prices that are no longer used")
    report.append("3. **Review**: Active prices not configured in backend")
    report.append("4. **Clean**: Inactive prices can be safely ignored (Stripe keeps them for history)")
    
    report.append("\n## 🛠️ Next Steps")
    report.append("\n- [ ] Review unused active prices")
    report.append("- [ ] Archive duplicate products if not needed")
    report.append("- [ ] Verify all backend price IDs are correct")
    report.append("- [ ] Update .env if any price IDs need to change")
    
    report.append("\n---")
    report.append("\n*Audit completed successfully* ✅")
    
    return "\n".join(report)

def main():
    """Main audit function."""
    
    try:
        print("Starting Stripe audit...\n")
        
        # Audit
        audit_data, products_response = audit_stripe()
        
        print(f"✅ Found {len(audit_data)} products")
        print(f"✅ Analyzed {sum(len(p['prices']) for p in audit_data)} prices\n")
        
        # Generate report
        report = generate_markdown_report(audit_data)
        
        # Save to file
        output_file = "STRIPE_AUDIT.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Audit report saved to: {output_file}")
        print("\nRun: code {output_file}")
        print("Or: cat {output_file}")
        
    except Exception as e:
        print(f"❌ Error during audit: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
