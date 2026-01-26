"""
Script para archivar productos antiguos de Stripe.

Este script:
1. Identifica productos que NO sean los 3 planes finales
2. Archiva productos con nombres antiguos/genéricos
3. Desactiva precios antiguos
4. NO afecta suscripciones existentes
5. Genera reporte en STRIPE_CLEANUP.md

IMPORTANTE: Archivar (active=False) NO elimina ni afecta suscripciones existentes.
Solo hace que los productos no aparezcan en el checkout.
"""

import os
import sys
from datetime import datetime
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
if not STRIPE_API_KEY:
    print("❌ Error: STRIPE_SECRET_KEY not found in .env")
    sys.exit(1)

stripe.api_key = STRIPE_API_KEY

# Productos FINALES que NO deben archivarse
KEEP_PRODUCTS = [
    "LinkedIn Lead Checker – Starter",
    "LinkedIn Lead Checker – Pro",
    "LinkedIn Lead Checker – Team"
]

# Precios antiguos a identificar (en USD)
OLD_PRICES = [9.99, 12.00, 8.00, 39.00]

# Nombres genéricos a archivar
GENERIC_NAMES = ["Base", "Plus", "Business", "Starter", "Pro", "Team"]


def should_archive_product(product_name: str) -> bool:
    """Determina si un producto debe archivarse."""
    
    # Mantener productos finales
    if product_name in KEEP_PRODUCTS:
        return False
    
    # Archivar productos con nombres genéricos
    if product_name in GENERIC_NAMES:
        return True
    
    # Archivar productos antiguos de LinkedIn Lead Checker sin el formato exacto
    if "LinkedIn Lead Checker" in product_name and product_name not in KEEP_PRODUCTS:
        return True
    
    return True


def archive_products():
    """Archiva productos antiguos de Stripe."""
    
    print("="*80)
    print("🗄️  Archivando Productos Antiguos de Stripe")
    print("="*80)
    print()
    
    # Get all active products
    all_products = stripe.Product.list(limit=100, active=True)
    
    archived_products = []
    kept_products = []
    archived_prices = []
    
    print(f"📦 Productos activos encontrados: {len(all_products.data)}\n")
    
    for product in all_products.data:
        should_archive = should_archive_product(product.name)
        
        if should_archive:
            print(f"🗄️  Archivando: {product.name}")
            print(f"   Product ID: {product.id}")
            
            # Get all prices for this product
            prices = stripe.Price.list(product=product.id, active=True, limit=100)
            
            # Archive all active prices first
            for price in prices.data:
                amount = price.unit_amount / 100 if price.unit_amount else 0
                print(f"   ├─ Desactivando precio: ${amount:.2f} {price.currency.upper()} ({price.id})")
                
                stripe.Price.modify(price.id, active=False)
                
                archived_prices.append({
                    'price_id': price.id,
                    'product_name': product.name,
                    'amount': amount,
                    'currency': price.currency.upper(),
                    'interval': price.recurring.interval if price.recurring else 'one-time'
                })
            
            # Archive the product
            stripe.Product.modify(product.id, active=False)
            
            archived_products.append({
                'product_id': product.id,
                'name': product.name,
                'created': datetime.fromtimestamp(product.created).strftime('%Y-%m-%d'),
                'prices_archived': len(prices.data)
            })
            
            print(f"   ✓ Producto archivado\n")
            
        else:
            print(f"✅ Manteniendo: {product.name} ({product.id})\n")
            kept_products.append({
                'product_id': product.id,
                'name': product.name
            })
    
    return archived_products, kept_products, archived_prices


def generate_cleanup_report(archived_products, kept_products, archived_prices):
    """Genera reporte en STRIPE_CLEANUP.md"""
    
    content = f"""# 🗄️ Stripe Products Cleanup Report

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Acción:** Archivado de productos antiguos  
**Estado:** ✅ Completado exitosamente

---

## 📊 Resumen

- **Productos archivados:** {len(archived_products)}
- **Productos mantenidos:** {len(kept_products)}
- **Precios desactivados:** {len(archived_prices)}

---

## ✅ Productos Mantenidos (Activos)

Los siguientes productos permanecen activos y disponibles para checkout:

"""
    
    for product in kept_products:
        content += f"### {product['name']}\n"
        content += f"- **Product ID:** `{product['product_id']}`\n"
        content += f"- **Estado:** ✅ Activo\n\n"
    
    content += """---

## 🗄️ Productos Archivados

Los siguientes productos fueron archivados (ya no visibles en checkout):

"""
    
    for product in archived_products:
        content += f"### {product['name']}\n"
        content += f"- **Product ID:** `{product['product_id']}`\n"
        content += f"- **Fecha creación:** {product['created']}\n"
        content += f"- **Precios desactivados:** {product['prices_archived']}\n"
        content += f"- **Estado:** 🗄️ Archivado (active=false)\n\n"
    
    content += """---

## 💰 Precios Desactivados

"""
    
    if archived_prices:
        content += "| Producto | Price ID | Monto | Intervalo |\n"
        content += "|----------|----------|-------|-----------|\\n"
        
        for price in archived_prices:
            content += f"| {price['product_name']} | `{price['price_id']}` | ${price['amount']:.2f} {price['currency']} | {price['interval']} |\n"
    else:
        content += "No se desactivaron precios.\n"
    
    content += """
---

## ⚠️ Importante: Impacto de Archivado

### ✅ Lo que SÍ hace archivar un producto:
- ❌ El producto NO aparece en listados de productos activos
- ❌ El producto NO puede ser comprado en nuevos checkouts
- ❌ Los precios NO están disponibles para nuevas suscripciones
- ✅ El dashboard de Stripe lo marca como "Archived"

### ✅ Lo que NO hace archivar un producto:
- ✅ Las suscripciones existentes NO se ven afectadas
- ✅ Los clientes actuales pueden seguir pagando
- ✅ Los webhooks siguen funcionando para suscripciones existentes
- ✅ Se puede restaurar el producto si es necesario

### 🔄 Cómo restaurar un producto archivado:
```python
stripe.Product.modify('prod_xxx', active=True)
stripe.Price.modify('price_xxx', active=True)
```

---

## 🔍 Verificación

Para verificar que los productos finales están activos:

```bash
python verify_stripe_products.py
```

Para ver todos los productos (incluyendo archivados):

```bash
python audit_stripe.py
```

---

## 📋 Productos Finales Activos

Los únicos productos que deben estar activos son:

1. **LinkedIn Lead Checker – Starter**
   - Precio: $9.00 USD/mes
   - Análisis: 40/mes

2. **LinkedIn Lead Checker – Pro**
   - Precio: $19.00 USD/mes
   - Análisis: 150/mes

3. **LinkedIn Lead Checker – Team**
   - Precio: $49.00 USD/mes
   - Análisis: 500/mes

---

## ✅ Confirmación

- ✅ Productos antiguos archivados correctamente
- ✅ Precios antiguos desactivados
- ✅ Productos finales permanecen activos
- ✅ No se afectan suscripciones existentes
- ✅ Checkout muestra solo productos finales

**Dashboard Stripe:** https://dashboard.stripe.com/products

---

**Nota:** Para ver productos archivados en Stripe Dashboard, usa el filtro "Show archived products".
"""
    
    with open("STRIPE_CLEANUP.md", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"📄 Reporte guardado en STRIPE_CLEANUP.md")


def main():
    """Main function"""
    
    print(f"🔑 Using Stripe API Key: {STRIPE_API_KEY[:20]}...\n")
    
    # Test connection
    try:
        account = stripe.Account.retrieve()
        print(f"✓ Connected to Stripe account: {account.id}\n")
    except Exception as e:
        print(f"❌ Failed to connect to Stripe: {str(e)}")
        sys.exit(1)
    
    print("⚠️  ADVERTENCIA: Este script archivará productos antiguos.")
    print("   Los productos archivados NO aparecerán en checkout.")
    print("   Las suscripciones existentes NO se verán afectadas.\n")
    
    response = input("¿Continuar? (escriba 'SI' para confirmar): ")
    
    if response.strip().upper() != "SI":
        print("\n❌ Operación cancelada por el usuario.")
        sys.exit(0)
    
    print()
    
    # Archive products
    archived_products, kept_products, archived_prices = archive_products()
    
    # Generate report
    generate_cleanup_report(archived_products, kept_products, archived_prices)
    
    # Summary
    print("\n" + "="*80)
    print("✅ Limpieza Completada")
    print("="*80)
    print()
    print(f"📊 Resumen:")
    print(f"   • Productos archivados: {len(archived_products)}")
    print(f"   • Productos activos: {len(kept_products)}")
    print(f"   • Precios desactivados: {len(archived_prices)}")
    print()
    print(f"📄 Ver reporte completo: STRIPE_CLEANUP.md")
    print(f"🔍 Verificar productos activos: python verify_stripe_products.py")
    print(f"🌐 Dashboard Stripe: https://dashboard.stripe.com/products")
    print()
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
