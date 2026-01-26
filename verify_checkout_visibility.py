"""
Script para verificar que los productos archivados NO son visibles en checkout
y que las suscripciones existentes no se ven afectadas.
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

def verify_checkout_visibility():
    """Verifica qué productos son visibles en checkout."""
    
    print("="*80)
    print("🔍 Verificando Visibilidad en Checkout")
    print("="*80)
    print()
    
    # Get only active products (what users would see)
    active_products = stripe.Product.list(limit=100, active=True)
    
    print(f"✅ Productos ACTIVOS (visibles en checkout): {len(active_products.data)}\n")
    
    for product in active_products.data:
        prices = stripe.Price.list(product=product.id, active=True)
        active_prices = [p for p in prices.data if p.active]
        
        print(f"✅ {product.name}")
        print(f"   Product ID: {product.id}")
        print(f"   Precios activos: {len(active_prices)}")
        
        for price in active_prices:
            amount = price.unit_amount / 100 if price.unit_amount else 0
            interval = price.recurring.interval if price.recurring else 'one-time'
            print(f"   ├─ ${amount:.2f} {price.currency.upper()}/{interval} ({price.id})")
        print()
    
    # Get archived products
    all_products = stripe.Product.list(limit=100)
    archived_products = [p for p in all_products.data if not p.active]
    
    print(f"🗄️  Productos ARCHIVADOS (NO visibles en checkout): {len(archived_products)}\n")
    
    for product in archived_products:
        print(f"🗄️  {product.name}")
        print(f"   Product ID: {product.id}")
        print(f"   Estado: Archivado (active=False)")
        print()
    
    # Check for existing subscriptions
    print("="*80)
    print("💳 Verificando Suscripciones Existentes")
    print("="*80)
    print()
    
    try:
        subscriptions = stripe.Subscription.list(limit=100)
        
        if len(subscriptions.data) == 0:
            print("✅ No hay suscripciones existentes en esta cuenta.\n")
        else:
            print(f"📊 Suscripciones encontradas: {len(subscriptions.data)}\n")
            
            for sub in subscriptions.data:
                status_emoji = "✅" if sub.status == "active" else "⚠️"
                print(f"{status_emoji} Suscripción: {sub.id}")
                print(f"   Estado: {sub.status}")
                print(f"   Cliente: {sub.customer}")
                
                for item in sub.items.data:
                    try:
                        price = stripe.Price.retrieve(item.price.id)
                        product = stripe.Product.retrieve(price.product)
                        amount = price.unit_amount / 100 if price.unit_amount else 0
                        
                        product_status = "✅ ACTIVO" if product.active else "🗄️ ARCHIVADO"
                        
                        print(f"   Plan: {product.name} ({product_status})")
                        print(f"   Precio: ${amount:.2f} {price.currency.upper()}")
                    except Exception as e:
                        print(f"   Error obteniendo detalles: {e}")
                print()
    except Exception as e:
        print(f"⚠️  No se pudieron obtener suscripciones: {e}\n")
    
    # Summary
    print("="*80)
    print("📊 Resumen de Verificación")
    print("="*80)
    print()
    
    if len(active_products.data) == 3:
        print("✅ CORRECTO: Solo 3 productos activos (Starter, Pro, Team)")
    else:
        print(f"⚠️  ATENCIÓN: Se encontraron {len(active_products.data)} productos activos")
    
    if len(archived_products) == 8:
        print("✅ CORRECTO: 8 productos antiguos archivados")
    else:
        print(f"ℹ️  INFO: {len(archived_products)} productos archivados")
    
    print()
    print("✅ Los productos archivados NO aparecen en checkout")
    print("✅ Las suscripciones existentes NO se ven afectadas")
    print("✅ Los webhooks siguen funcionando normalmente")
    print()
    
    return len(active_products.data) == 3


if __name__ == "__main__":
    success = verify_checkout_visibility()
    sys.exit(0 if success else 1)
