# 🔍 Stripe Verification System

## 📋 Overview

Sistema de verificación que valida la sincronización entre la configuración del backend y Stripe, garantizando que:
- ✅ Hay exactamente 3 planes activos
- ✅ Los precios coinciden con los esperados
- ✅ No existen productos duplicados
- ✅ Los price_ids del backend están activos en Stripe
- ✅ Backend y Stripe están sincronizados

---

## 🚀 Uso Rápido

### Opción 1: Script de Línea de Comandos
```powershell
python verify_stripe_sync.py
```

### Opción 2: API Endpoint (Opcional)
```bash
# Verificación completa
curl BACKEND_URL/admin/verify-stripe

# Health check rápido
curl BACKEND_URL/admin/stripe-health
```

**Ver:** [stripe_verification_endpoint.py](./stripe_verification_endpoint.py) para implementar el endpoint.

### Resultado Esperado (Estado Saludable):
```
✅ VERIFICATION PASSED - All checks successful!
🎉 System is ready for production!
```

### Si Hay Errores:
```
❌ VERIFICATION FAILED
🚨 Fix errors before deploying to production!

Recommended actions:
   1. Run: python archive_old_stripe_products.py
   2. Run: python setup_stripe_products.py
   3. Update .env with correct price_ids
   4. Run this script again
```

---

## 🔍 Qué Verifica el Script

### 1️⃣ Configuración del Backend
**Verifica que .env contenga:**
- `STRIPE_PRICE_STARTER_ID`
- `STRIPE_PRICE_PRO_ID`
- `STRIPE_PRICE_TEAM_ID`

**Resultado esperado:**
```
✓ Loaded starter: price_1StrzhPc1lhDefcvp0TJY0rS
✓ Loaded pro: price_1StrziPc1lhDefcvrfIRB0n0
✓ Loaded team: price_1StrzjPc1lhDefcvgp2rRqh4
```

### 2️⃣ Estado de Stripe
**Carga productos y precios desde Stripe API:**
- Total de productos
- Productos activos vs archivados
- Precios activos por producto

**Resultado esperado:**
```
✓ Loaded 11 products
  • Active: 3
  • Archived: 8
✓ Product 'LinkedIn Lead Checker – Starter': 1 active price(s)
✓ Product 'LinkedIn Lead Checker – Pro': 1 active price(s)
✓ Product 'LinkedIn Lead Checker – Team': 1 active price(s)
```

### 3️⃣ Cantidad de Productos
**Valida que haya exactamente 3 productos activos.**

**✅ Pasa si:**
- Hay exactamente 3 productos activos

**❌ Falla si:**
- Hay más o menos de 3 productos activos
- Error: `Expected exactly 3 active products, found X`

### 4️⃣ Nombres de Productos
**Verifica que los nombres sean exactos:**
- `LinkedIn Lead Checker – Starter`
- `LinkedIn Lead Checker – Pro`
- `LinkedIn Lead Checker – Team`

**✅ Pasa si:**
- Los 3 productos tienen los nombres exactos esperados

**❌ Falla si:**
- Falta algún producto esperado
- Hay productos con nombres diferentes

**⚠️ Advierte si:**
- Hay productos con nombres similares (ej: "LinkedIn Lead Checker Pro" sin guion)

### 5️⃣ Precios Correctos
**Verifica que los precios mensuales sean:**
- Starter: $9.00/mes
- Pro: $19.00/mes
- Team: $49.00/mes

**✅ Pasa si:**
- Todos los precios coinciden con los esperados

**❌ Falla si:**
- Algún precio no coincide
- Error: `Price mismatch - expected $19.00, got $29.00`

**⚠️ Advierte si:**
- Un producto tiene múltiples precios activos

### 6️⃣ Duplicados
**Busca productos duplicados:**
- Nombres exactamente iguales
- Nombres similares (potenciales duplicados)

**✅ Pasa si:**
- No hay productos con nombres duplicados
- No hay productos similares activos

**❌ Falla si:**
- Hay productos con el mismo nombre
- Error: `Duplicate product: LinkedIn Lead Checker – Pro (2 instances)`

**⚠️ Advierte si:**
- Hay productos similares (ej: "Lead Checker Pro", "LinkedIn Checker")

### 7️⃣ Price IDs Activos
**Verifica que los price_ids del .env estén activos en Stripe:**

**✅ Pasa si:**
- Todos los price_ids existen en Stripe
- Todos los price_ids están marcados como `active=True`

**❌ Falla si:**
- Algún price_id no existe en Stripe
- Algún price_id está marcado como `active=False`

### 8️⃣ Sincronización Backend ↔ Stripe
**Verifica que el backend use los price_ids correctos:**

**Para cada plan:**
1. Busca el producto correspondiente en Stripe
2. Obtiene sus precios activos
3. Verifica que el price_id del backend coincida

**✅ Pasa si:**
- Los price_ids del backend coinciden con los de Stripe
- Cada producto tiene exactamente 1 precio activo
- El precio activo es el que está en .env

**❌ Falla si:**
- Los price_ids no coinciden
- El producto no existe en Stripe
- Hay múltiples productos con el mismo nombre

---

## 📊 Ejemplo de Salida Completa

### Verificación Exitosa:
```
================================================================================
🔍 Stripe Synchronization Verification
================================================================================

1️⃣ Loading backend configuration...
   ✓ Loaded starter: price_1StrzhPc1lhDefcvp0TJY0rS
   ✓ Loaded pro: price_1StrziPc1lhDefcvrfIRB0n0
   ✓ Loaded team: price_1StrzjPc1lhDefcvgp2rRqh4

2️⃣ Loading Stripe data...
   ✓ Loaded 11 products
     • Active: 3
     • Archived: 8
   ✓ Product 'LinkedIn Lead Checker – Team': 1 active price(s)
   ✓ Product 'LinkedIn Lead Checker – Pro': 1 active price(s)
   ✓ Product 'LinkedIn Lead Checker – Starter': 1 active price(s)

3️⃣ Verifying product count...
   ✅ Exactly 3 active products

4️⃣ Verifying product names...
   ✅ Found: LinkedIn Lead Checker – Team
   ✅ Found: LinkedIn Lead Checker – Pro
   ✅ Found: LinkedIn Lead Checker – Starter

5️⃣ Verifying prices...
   ✅ LinkedIn Lead Checker – Team: $49.00/month (correct)
   ✅ LinkedIn Lead Checker – Pro: $19.00/month (correct)
   ✅ LinkedIn Lead Checker – Starter: $9.00/month (correct)

6️⃣ Checking for duplicates...
   ✅ No duplicate products

7️⃣ Verifying price_ids are active...
   ✅ starter: price_id is active
   ✅ pro: price_id is active
   ✅ team: price_id is active

8️⃣ Verifying backend/Stripe synchronization...
   ✅ starter: Backend ↔ Stripe synchronized
   ✅ pro: Backend ↔ Stripe synchronized
   ✅ team: Backend ↔ Stripe synchronized

================================================================================
📊 Verification Report
================================================================================

📋 Summary:
   • Active Products: 3
   • Backend Plans: 3
   • Errors: 0
   • Warnings: 0

================================================================================
✅ VERIFICATION PASSED - All checks successful!
================================================================================

🎉 System is ready for production!
```

### Verificación con Errores:
```
================================================================================
🔍 Stripe Synchronization Verification
================================================================================

1️⃣ Loading backend configuration...
   ✓ Loaded starter: price_1StrzhPc1lhDefcvp0TJY0rS
   ✓ Loaded pro: price_OLD123456789
   ✓ Loaded team: price_1StrzjPc1lhDefcvgp2rRqh4

2️⃣ Loading Stripe data...
   ✓ Loaded 11 products
     • Active: 5
     • Archived: 6
   ✓ Product 'LinkedIn Lead Checker – Team': 1 active price(s)
   ✓ Product 'LinkedIn Lead Checker – Pro': 1 active price(s)
   ✓ Product 'LinkedIn Lead Checker – Starter': 1 active price(s)
   ✓ Product 'LinkedIn Lead Checker Pro': 1 active price(s)
   ✓ Product 'Lead Checker Business': 1 active price(s)

3️⃣ Verifying product count...
   ❌ Found 5 active products (expected 3)

4️⃣ Verifying product names...
   ✅ Found: LinkedIn Lead Checker – Team
   ✅ Found: LinkedIn Lead Checker – Pro
   ✅ Found: LinkedIn Lead Checker – Starter
   ⚠️  Unexpected: LinkedIn Lead Checker Pro
   ⚠️  Unexpected: Lead Checker Business

5️⃣ Verifying prices...
   ✅ LinkedIn Lead Checker – Team: $49.00/month (correct)
   ✅ LinkedIn Lead Checker – Pro: $19.00/month (correct)
   ✅ LinkedIn Lead Checker – Starter: $9.00/month (correct)

6️⃣ Checking for duplicates...
   ✅ No duplicate products
   ⚠️  Similar: LinkedIn Lead Checker Pro (may need archiving)
   ⚠️  Similar: Lead Checker Business (may need archiving)

7️⃣ Verifying price_ids are active...
   ✅ starter: price_id is active
   ❌ pro: price_id NOT FOUND in Stripe
   ✅ team: price_id is active

8️⃣ Verifying backend/Stripe synchronization...
   ✅ starter: Backend ↔ Stripe synchronized
   ❌ pro: Backend price_id price_OLD123456789 doesn't match Stripe prices ['price_1StrziPc1lhDefcvrfIRB0n0']
   ✅ team: Backend ↔ Stripe synchronized

================================================================================
📊 Verification Report
================================================================================

❌ ERRORS (3):
   1. Expected exactly 3 active products, found 5
   2. pro: price_id price_OLD123456789 not found in Stripe
   3. pro: Backend price_id price_OLD123456789 doesn't match Stripe prices ['price_1StrziPc1lhDefcvrfIRB0n0']

⚠️  WARNINGS (4):
   1. Unexpected product name: LinkedIn Lead Checker Pro
   2. Unexpected product name: Lead Checker Business
   3. Similar product name: LinkedIn Lead Checker Pro
   4. Similar product name: Lead Checker Business

📋 Summary:
   • Active Products: 5
   • Backend Plans: 3
   • Errors: 3
   • Warnings: 4

================================================================================
❌ VERIFICATION FAILED
   Action required before production deployment
================================================================================

🚨 Fix errors before deploying to production!

Recommended actions:
   1. Run: python archive_old_stripe_products.py
   2. Run: python setup_stripe_products.py
   3. Update .env with correct price_ids
   4. Run this script again
```

---

## 🔧 Solución de Errores Comunes

### Error: "Expected exactly 3 active products, found X"

**Causa:** Hay productos duplicados o productos viejos activos

**Solución:**
```powershell
# 1. Ver qué productos están activos
python test_duplicate_prevention.py

# 2. Archivar productos viejos/duplicados
python archive_old_stripe_products.py

# 3. Verificar de nuevo
python verify_stripe_sync.py
```

### Error: "price_id not found in Stripe"

**Causa:** El price_id en .env es incorrecto o fue eliminado

**Solución:**
```powershell
# 1. Regenerar productos y precios
python setup_stripe_products.py

# 2. Copiar los nuevos price_ids al .env
# (El script los mostrará al final)

# 3. Verificar de nuevo
python verify_stripe_sync.py
```

### Error: "Backend price_id doesn't match Stripe prices"

**Causa:** El .env tiene un price_id viejo, pero Stripe tiene uno nuevo

**Solución:**
```powershell
# 1. Ver los price_ids actuales en Stripe
python setup_stripe_products.py

# 2. Actualizar .env con los price_ids correctos
# (Copiar desde la salida del script o desde STRIPE_IDS.md)

# 3. Verificar de nuevo
python verify_stripe_sync.py
```

### Warning: "Similar product name"

**Causa:** Hay productos con nombres parecidos pero no exactos

**Solución:**
```powershell
# 1. Identificar productos similares
python test_duplicate_prevention.py

# 2. Archivarlos (no eliminar)
python archive_old_stripe_products.py

# 3. Verificar de nuevo
python verify_stripe_sync.py
```

### Warning: "Multiple active prices for product"

**Causa:** Un producto tiene más de un precio activo

**Solución:**
```powershell
# En Stripe Dashboard:
# 1. Ir a: https://dashboard.stripe.com/products
# 2. Abrir el producto afectado
# 3. Desactivar precios viejos (marcar como inactive)
# 4. Dejar solo 1 precio activo

# Verificar de nuevo
python verify_stripe_sync.py
```

---

## 📅 Cuándo Ejecutar la Verificación

### ✅ Antes de Deployment:
```powershell
# En el workflow de CI/CD
python verify_stripe_sync.py || exit 1
```

### ✅ Después de Cambios en Stripe:
- Después de crear/actualizar productos
- Después de cambiar precios
- Después de archivar productos
- Después de modificar .env

### ✅ Mantenimiento Regular:
- **Diario:** En entornos de producción
- **Antes de cada deploy:** En CI/CD
- **Después de incidentes:** Para verificar estado

### ✅ Troubleshooting:
- Cuando hay problemas con checkouts
- Cuando webhooks fallan
- Cuando los usuarios reportan precios incorrectos

---

## 🔄 Integración con CI/CD

### GitHub Actions Example:
```yaml
name: Verify Stripe Configuration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  verify-stripe:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Verify Stripe Sync
        env:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
          STRIPE_PRICE_STARTER_ID: ${{ secrets.STRIPE_PRICE_STARTER_ID }}
          STRIPE_PRICE_PRO_ID: ${{ secrets.STRIPE_PRICE_PRO_ID }}
          STRIPE_PRICE_TEAM_ID: ${{ secrets.STRIPE_PRICE_TEAM_ID }}
        run: |
          python verify_stripe_sync.py
```

### Pre-Commit Hook:
```bash
#!/bin/bash
# .git/hooks/pre-push

echo "🔍 Verifying Stripe configuration..."
python verify_stripe_sync.py

if [ $? -ne 0 ]; then
    echo "❌ Stripe verification failed!"
    echo "Fix errors before pushing to production"
    exit 1
fi

echo "✅ Stripe verification passed"
```

---

## 🎯 Criterios de Éxito

### ✅ Estado Saludable:
- Exactamente 3 productos activos
- Nombres de productos exactos (con guiones `–`)
- Precios correctos: $9, $19, $49
- Sin productos duplicados
- Sin productos similares activos
- Todos los price_ids activos en Stripe
- Backend y Stripe sincronizados
- 0 errores, 0 warnings

### ⚠️ Estado Aceptable (Con Warnings):
- 3 productos activos correctos
- Precios correctos
- Price_ids sincronizados
- 0 errores, algunos warnings
- Warnings no bloquean deployment pero requieren atención

### ❌ Estado Crítico (Con Errores):
- Más o menos de 3 productos activos
- Productos duplicados
- Precios incorrectos
- Price_ids inactivos o no encontrados
- Backend/Stripe desincronizados
- **NO DEPLOYAR A PRODUCCIÓN**

---

## 🔗 Scripts Relacionados

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `verify_stripe_sync.py` | Verificación completa | Antes de deploy, después de cambios |
| `test_duplicate_prevention.py` | Detectar duplicados | Antes de crear productos |
| `setup_stripe_products.py` | Crear/actualizar productos | Setup inicial, cambios de precio |
| `archive_old_stripe_products.py` | Limpiar duplicados | Cuando hay productos viejos |
| `test_stripe_security.py` | Verificar whitelist | Después de cambios en backend |

---

## 📚 Documentación Relacionada

- [STRIPE_IDS.md](./STRIPE_IDS.md) - IDs actuales de productos y precios
- [STRIPE_DUPLICATE_PREVENTION.md](./STRIPE_DUPLICATE_PREVENTION.md) - Sistema de prevención de duplicados
- [STRIPE_SECURITY_IMPLEMENTATION.md](./STRIPE_SECURITY_IMPLEMENTATION.md) - Validación de price_ids
- [STRIPE_CLEANUP.md](./STRIPE_CLEANUP.md) - Historial de archivado
- [STRIPE_QUICKREF.md](./STRIPE_QUICKREF.md) - Referencia rápida

---

## 💡 Tips Avanzados

### Verificación Automática con Cron:
```bash
# Ejecutar cada hora en producción
0 * * * * cd /path/to/project && python verify_stripe_sync.py >> /var/log/stripe-verify.log 2>&1
```

### Alertas por Email:
```python
# Agregar al final de verify_stripe_sync.py
if not success:
    send_email(
        to="admin@example.com",
        subject="🚨 Stripe Verification Failed",
        body=f"Errors: {len(verifier.errors)}\n\n{verifier.errors}"
    )
```

### Slack Notifications:
```python
# Webhook de Slack
if not success:
    requests.post(
        SLACK_WEBHOOK_URL,
        json={
            "text": f"🚨 Stripe verification failed with {len(verifier.errors)} errors"
        }
    )
```

---

## 🆘 Soporte

Si la verificación falla y no sabes cómo arreglar:

1. **Guarda la salida completa del script**
2. **Revisa los errores específicos**
3. **Consulta la sección "Solución de Errores Comunes"**
4. **Si persiste, ejecuta:**
   ```powershell
   python test_duplicate_prevention.py > diagnostic.txt
   python verify_stripe_sync.py >> diagnostic.txt
   ```
5. **Revisa `diagnostic.txt` para análisis completo**

---

**Última Actualización:** 2026-01-26
**Versión:** 1.0.0
**Estado:** ✅ Production Ready
