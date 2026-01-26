# 🔒 Stripe Security & Anti-Fraud Protection

**Fecha de implementación:** 2026-01-26  
**Estado:** ✅ Activo y verificado

---

## 🎯 Objetivo

Implementar protección anti-fraude y anti-errores en el sistema de suscripciones de Stripe para garantizar que:

1. Solo se acepten los 3 planes finales autorizados
2. Se rechacen price_ids no autorizados o antiguos
3. Se valide que el precio pagado coincide con el plan esperado
4. Se evite que usuarios tengan planes inexistentes

---

## 🛡️ Protecciones Implementadas

### 1. Whitelist de Price IDs

Se implementó una lista blanca (whitelist) de price_ids permitidos:

```python
allowed_price_ids = {
    "price_1StrzhPc1lhDefcvp0TJY0rS": "starter",  # $9.00 USD/mes
    "price_1StrziPc1lhDefcvrfIRB0n0": "pro",      # $19.00 USD/mes
    "price_1StrzjPc1lhDefcvgp2rRqh4": "team",     # $49.00 USD/mes
}
```

**Protección:** Solo estos 3 price_ids son aceptados en todo el sistema.

---

### 2. Validación de Price IDs

**Método:** `validate_price_id(price_id: str) -> str`

**Función:**
- Verifica que el price_id esté en la whitelist
- Retorna el plan correspondiente ("starter", "pro", "team")
- Rechaza cualquier price_id no autorizado con `ValueError`

**Ejemplo de uso:**
```python
try:
    plan = stripe_service.validate_price_id("price_1StrzhPc1lhDefcvp0TJY0rS")
    # plan = "starter"
except ValueError as e:
    # Price ID no autorizado
    logger.error(f"SECURITY_VIOLATION: {e}")
```

**Logs de seguridad:**
```
SECURITY_VIOLATION | Attempted to use unauthorized price_id=price_xxx | allowed_ids=[...]
```

---

### 3. Validación en Checkout

**Flujo protegido:**

1. Usuario solicita checkout para un plan
2. Se valida que el plan sea "starter", "pro" o "team"
3. Se obtiene el price_id configurado para ese plan
4. Se valida que el price_id esté en la whitelist
5. Se crea la sesión de checkout con el price_id validado

**Código:**
```python
# SECURITY: Validate plan name
plan = plan.lower().strip()
if plan not in ["starter", "pro", "team"]:
    raise ValueError(f"Invalid plan '{plan}'. Must be: starter, pro, or team")

# SECURITY: Get validated price_id for plan
price_id = self.get_price_id_for_plan(plan)

# SECURITY: Double-check price_id is in whitelist
validated_plan = self.validate_price_id(price_id)
```

**Rechaza:**
- Planes inválidos: "business", "plus", "base", "premium"
- Price IDs no configurados
- Price IDs no autorizados

---

### 4. Validación en Webhooks

**Protección en `checkout.session.completed`:**

Cuando Stripe notifica un pago exitoso:

1. Se obtiene el `subscription_id` del webhook
2. Se consulta la suscripción en Stripe para obtener el `price_id` real pagado
3. Se valida que el `price_id` pagado esté en la whitelist
4. Si no está autorizado, se revierte al plan "free"
5. Se compara el plan del metadata vs el plan real del price_id
6. Se usa siempre el plan validado del price_id real

**Código:**
```python
# SECURITY: Fetch subscription to get actual price_id paid
subscription = stripe.Subscription.retrieve(subscription_id)
actual_price_id = items[0].get("price", {}).get("id")

# SECURITY: Validate price_id is authorized
try:
    validated_plan = self.validate_price_id(actual_price_id)
except ValueError as e:
    logger.error("SECURITY_VIOLATION | unauthorized_price_id=%s", actual_price_id)
    # Revert to free plan if unauthorized price detected
    user.plan = "free"
    return user

# Use validated plan from actual price_id
user.plan = validated_plan
```

**Protección en `customer.subscription.updated`:**

Similar validación al actualizar suscripciones (upgrades/downgrades).

---

## 🚫 Price IDs Rechazados

Los siguientes price_ids antiguos son rechazados automáticamente:

| Price ID | Precio | Producto | Estado |
|----------|--------|----------|--------|
| `price_1SrkwsPc1lhDefcv1sbYqMeG` | $9.99 | LinkedIn Lead Checker Pro (antiguo) | 🚫 Rechazado |
| `price_1SRzEpPc1lhDefcvbT1byOEA` | $12.00 | Plus | 🚫 Rechazado |
| `price_1SRzEoPc1lhDefcvXD8Swmh1` | $8.00 | Base | 🚫 Rechazado |
| `price_1SrmCwPc1lhDefcvdBqLWlbL` | $39.00 | LinkedIn Lead Checker Team (antiguo) | 🚫 Rechazado |
| `price_1Ssu7IPc1lhDefcvGhmgzOoZ` | $9.00 | Starter (antiguo) | 🚫 Rechazado |
| `price_1Ssu7KPc1lhDefcvgbL0z62T` | $19.00 | Pro (antiguo) | 🚫 Rechazado |
| `price_1Ssu7LPc1lhDefcv6NzhAtgz` | $49.00 | Business (antiguo) | 🚫 Rechazado |
| `price_1SrmCdPc1lhDefcvkdws7hwi` | $19.00 | LinkedIn Lead Checker Pro (antiguo) | 🚫 Rechazado |

---

## ✅ Price IDs Aceptados

Solo estos 3 price_ids son aceptados:

| Price ID | Precio | Producto | Plan |
|----------|--------|----------|------|
| `price_1StrzhPc1lhDefcvp0TJY0rS` | $9.00 | LinkedIn Lead Checker – Starter | ✅ starter |
| `price_1StrziPc1lhDefcvrfIRB0n0` | $19.00 | LinkedIn Lead Checker – Pro | ✅ pro |
| `price_1StrzjPc1lhDefcvgp2rRqh4` | $49.00 | LinkedIn Lead Checker – Team | ✅ team |

---

## 🔍 Testing

**Script de prueba:** `test_stripe_security.py`

**Tests ejecutados:**
1. ✅ Validación de price_ids permitidos
2. ✅ Rechazo de price_ids no autorizados (8 antiguos)
3. ✅ Mapeo de plan a price_id
4. ✅ Validación de price_id a plan
5. ✅ Rechazo de planes inválidos
6. ✅ Integridad de whitelist

**Ejecutar tests:**
```bash
python test_stripe_security.py
```

**Resultado esperado:**
```
✅ All security validations passed!

🔒 Security Features Verified:
   ✅ Only 3 price_ids accepted (Starter, Pro, Team)
   ✅ Old price_ids rejected ($9.99, $12, $8, $39)
   ✅ Fake price_ids rejected
   ✅ Invalid plans rejected
   ✅ Plan-to-price mapping works correctly
   ✅ Price-to-plan validation works correctly

🛡️  Anti-fraud protection: ACTIVE
```

---

## 🎯 Escenarios Protegidos

### Escenario 1: Intento de usar price_id antiguo

**Ataque:**
```bash
curl -X POST /api/billing/checkout \
  -H "Authorization: Bearer xxx" \
  -d '{"plan": "pro", "return_url": "..."}'
```

Si alguien manipula Stripe para usar `price_1SrkwsPc1lhDefcv1sbYqMeG` (antiguo $9.99):

**Protección:**
1. El webhook recibe el evento
2. Se obtiene el price_id real de la suscripción
3. Se valida contra la whitelist → RECHAZADO
4. Se registra `SECURITY_VIOLATION` en logs
5. Usuario queda en plan "free"

**Log:**
```
SECURITY_VIOLATION | user_id=xxx | unauthorized_price_id=price_1SrkwsPc1lhDefcv1sbYqMeG
```

---

### Escenario 2: Mismatch entre metadata y price real

**Situación:**
- Metadata del checkout dice: `plan: "pro"`
- Price ID real pagado: `price_1StrzhPc1lhDefcvp0TJY0rS` (starter)

**Protección:**
1. Se ignora el metadata
2. Se valida el price_id real → "starter"
3. Usuario obtiene plan "starter" (el que realmente pagó)
4. Se registra warning de mismatch

**Log:**
```
PLAN_MISMATCH | metadata_plan=pro | actual_plan=starter | using_actual
```

---

### Escenario 3: Price ID completamente falso

**Ataque:**
Alguien intenta manipular el webhook con:
```json
{
  "subscription": {
    "items": {
      "data": [{
        "price": {"id": "price_fake123456789"}
      }]
    }
  }
}
```

**Protección:**
1. Se intenta validar `price_fake123456789`
2. No está en whitelist → RECHAZADO
3. Se registra `SECURITY_VIOLATION`
4. Usuario queda en plan "free"

---

### Escenario 4: Plan inexistente

**Ataque:**
```bash
curl -X POST /api/billing/checkout \
  -d '{"plan": "business"}'  # Plan que no existe
```

**Protección:**
1. Validación en endpoint rechaza "business"
2. Se retorna error 400
3. No se crea sesión de checkout

**Respuesta:**
```json
{
  "detail": "Invalid plan. Must be 'starter', 'pro', or 'team'"
}
```

---

## 📊 Logs de Seguridad

### Eventos registrados:

**Inicialización:**
```
StripeService initialized | allowed_price_ids=[...] | plans=['starter', 'pro', 'team']
```

**Validación exitosa:**
```
PRICE_VALIDATED | price_id=price_xxx | plan=starter
```

**Violación de seguridad:**
```
SECURITY_VIOLATION | Attempted to use unauthorized price_id=price_xxx | allowed_ids=[...]
```

**Checkout exitoso:**
```
CHECKOUT_COMPLETED | user_id=xxx | plan=starter | price_id=price_xxx | validated=true
```

**Suscripción activada:**
```
SUBSCRIPTION_ACTIVATED | user_id=xxx | plan=pro | price_id=price_xxx | validated=true
```

---

## 🔧 Configuración

Las validaciones se activan automáticamente al cargar las variables de entorno:

```bash
# .env
STRIPE_PRICE_STARTER_ID=price_1StrzhPc1lhDefcvp0TJY0rS
STRIPE_PRICE_PRO_ID=price_1StrziPc1lhDefcvrfIRB0n0
STRIPE_PRICE_TEAM_ID=price_1StrzjPc1lhDefcvgp2rRqh4
```

**Importante:** Si cambias los price_ids, debes:
1. Actualizar `.env`
2. Actualizar `STRIPE_IDS.md`
3. Reiniciar el backend
4. Ejecutar `python test_stripe_security.py`

---

## ⚡ Rendimiento

Las validaciones son extremadamente rápidas:

- **Validación de price_id:** O(1) - lookup en diccionario
- **Validación de plan:** O(1) - lookup en diccionario
- **Overhead total:** < 1ms por operación

No hay impacto perceptible en el rendimiento.

---

## 🛠️ Archivos Modificados

1. **`app/core/stripe_service.py`**
   - Agregado: `validate_price_id()`
   - Agregado: `get_price_id_for_plan()`
   - Agregado: `allowed_price_ids` whitelist
   - Modificado: `create_checkout_session()` con validaciones
   - Modificado: `handle_checkout_completed()` con validación de price real
   - Modificado: `handle_subscription_updated()` con validación

2. **`app/api/routes/billing.py`**
   - Mejorado: Manejo de errores de validación
   - Mejorado: Mensajes de error más claros

3. **`test_stripe_security.py`** (nuevo)
   - Suite completa de tests de seguridad

4. **`STRIPE_SECURITY_IMPLEMENTATION.md`** (este archivo)
   - Documentación completa de protecciones

---

## ✅ Checklist de Seguridad

- [x] Whitelist de price_ids implementada
- [x] Validación en checkout
- [x] Validación en webhooks (checkout.session.completed)
- [x] Validación en webhooks (customer.subscription.updated)
- [x] Rechazo de price_ids antiguos
- [x] Rechazo de planes inválidos
- [x] Logs de seguridad implementados
- [x] Tests de seguridad creados
- [x] Tests ejecutados exitosamente
- [x] Documentación completa

---

## 🚀 Próximos Pasos Recomendados

### Monitoreo (Opcional):

1. Configurar alertas para `SECURITY_VIOLATION` en logs
2. Dashboard de métricas de seguridad
3. Revisión mensual de intentos de fraude

### Hardening Adicional (Opcional):

1. Rate limiting en endpoint de checkout
2. Validación de IP/geolocalización
3. Verificación adicional de email

---

## 📞 Verificación Rápida

```bash
# Verificar protecciones activas
python test_stripe_security.py

# Verificar productos en Stripe
python verify_stripe_products.py

# Ver logs de seguridad
grep "SECURITY_VIOLATION" logs/*.log
```

---

**✅ Sistema protegido contra:**
- ✅ Uso de price_ids antiguos/archivados
- ✅ Uso de price_ids falsos
- ✅ Manipulación de planes
- ✅ Mismatch precio/plan
- ✅ Planes inexistentes

**🛡️ Protección anti-fraude:** ACTIVA y VERIFICADA
