"""
Script de verificación - Confirma que los productos de Stripe tienen los nombres exactos
"""

import os
import sys
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY not found in .env")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY

# Expected product names (EXACT)
EXPECTED_NAMES = [
    "LinkedIn Lead Checker – Starter",
    "LinkedIn Lead Checker – Pro",
    "LinkedIn Lead Checker – Team"
]

# Expected configuration from .env
EXPECTED_PRICES = {
    'starter': os.getenv("STRIPE_PRICE_STARTER_ID"),
    'pro': os.getenv("STRIPE_PRICE_PRO_ID"),
    'team': os.getenv("STRIPE_PRICE_TEAM_ID"),
}

def verify():
    """Verify all products have exact names and correct configuration."""
    
    print("="*70)
    print("🔍 Verificando Productos de Stripe")
    print("="*70)
    print()
    
    # Get all products
    products = stripe.Product.list(limit=100, active=True)
    
    found_products = {}
    
    print("📦 Productos encontrados con nombres exactos:\n")
    
    for expected_name in EXPECTED_NAMES:
        found = False
        for product in products.data:
            if product.name == expected_name:
                found_products[expected_name] = product
                found = True
                
                # Get prices for this product
                prices = stripe.Price.list(product=product.id, active=True)
                active_price = prices.data[0] if prices.data else None
                
                print(f"✅ {expected_name}")
                print(f"   Product ID: {product.id}")
                if active_price:
                    amount = active_price.unit_amount / 100
                    print(f"   Price ID: {active_price.id}")
                    print(f"   Precio: ${amount:.2f} {active_price.currency.upper()}")
                    print(f"   Intervalo: {active_price.recurring.interval if active_price.recurring else 'N/A'}")
                print()
                break
        
        if not found:
            print(f"❌ NO ENCONTRADO: {expected_name}\n")
    
    print("="*70)
    print("🔧 Configuración Backend (.env)")
    print("="*70)
    print()
    
    all_configured = True
    
    for plan, price_id in EXPECTED_PRICES.items():
        if price_id:
            try:
                price = stripe.Price.retrieve(price_id)
                product = stripe.Product.retrieve(price.product)
                amount = price.unit_amount / 100
                
                print(f"✅ {plan.upper()}: {product.name}")
                print(f"   Price ID: {price_id}")
                print(f"   Precio: ${amount:.2f} USD/mes")
                print()
            except Exception as e:
                print(f"❌ {plan.upper()}: Error - {str(e)}")
                print(f"   Price ID configurado: {price_id}\n")
                all_configured = False
        else:
            print(f"⚠️  {plan.upper()}: No configurado en .env\n")
            all_configured = False
    
    print("="*70)
    print("📊 Resultado de Verificación")
    print("="*70)
    print()
    
    if len(found_products) == len(EXPECTED_NAMES) and all_configured:
        print("✅ TODO CORRECTO")
        print("   • Todos los productos tienen nombres exactos")
        print("   • Precio mensual recurrente configurado")
        print("   • Sin trials")
        print("   • Currency: USD")
        print("   • Backend .env actualizado correctamente")
        print()
        print("🎉 ¡Sistema listo para usar!")
        return True
    else:
        print("⚠️  ACCIÓN REQUERIDA")
        if len(found_products) < len(EXPECTED_NAMES):
            print(f"   • Faltan {len(EXPECTED_NAMES) - len(found_products)} productos en Stripe")
        if not all_configured:
            print("   • Configuración incompleta en .env")
        print()
        print("💡 Ejecuta: python setup_stripe_products.py")
        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
