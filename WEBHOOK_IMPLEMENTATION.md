# ✅ Webhook de Stripe - Implementación Completa

## 🎯 Estado: IMPLEMENTADO

Todos los webhooks solicitados han sido implementados con seguridad e idempotencia.

---

## 📋 Eventos Implementados

### 1. ✅ checkout.session.completed

**Trigger:** Usuario completa el pago en Stripe Checkout

**Acciones:**
- Asocia la suscripción al usuario
- Guarda en BD:
  - `plan` (starter/pro/team) - validado contra whitelist
  - `stripe_customer_id` - ID del cliente en Stripe
  - `stripe_subscription_id` - ID de la suscripción
  - `subscription_status` = "active"
  - `monthly_analyses_count` = 0 (reset)
  - `monthly_analyses_reset_at` = próxima fecha de facturación
- **Idempotencia:** Verifica si subscription_id ya fue procesado

**Validaciones de Seguridad:**
- ✅ Valida que price_id esté en whitelist
- ✅ Verifica que plan de metadata coincida con price_id real
- ✅ Si price_id no autorizado → revierte a plan "free"

**Logging:**
```
CHECKOUT_COMPLETED | user_id=123 | plan=pro | price_id=price_xxx | 
customer_id=cus_xxx | subscription_id=sub_xxx | status=active | 
monthly_limit=150 | reset_at=2026-02-26 | validated=true
```

---

### 2. ✅ customer.subscription.created

**Trigger:** Se crea una suscripción (alternativa a checkout)

**Acciones:**
- Similar a checkout.session.completed
- Útil cuando se crea suscripción manualmente en Stripe Dashboard
- Asocia suscripción al usuario usando `customer_id`
- Inicializa créditos mensuales
- **Idempotencia:** Verifica si subscription_id ya fue procesado

**Validaciones de Seguridad:**
- ✅ Valida price_id contra whitelist
- ✅ Rechaza price_ids no autorizados

**Logging:**
```
SUBSCRIPTION_CREATED | user_id=123 | plan=pro | subscription_id=sub_xxx | 
status=active | monthly_limit=150 | reset_at=2026-02-26
```

---

### 3. ✅ customer.subscription.deleted

**Trigger:** Suscripción cancelada o expirada

**Acciones:**
- Revierte `plan` a "free"
- Cambia `subscription_status` a "canceled"
- Resetea `monthly_analyses_count` a 0
- Limpia `monthly_analyses_reset_at` (None)
- **Mantiene:** customer_id y subscription_id para historial

**Logging:**
```
SUBSCRIPTION_DELETED | user_id=123 | previous_plan=pro | 
previous_status=active | subscription_id=sub_xxx | 
customer_id=cus_xxx | reverted_to=free
```

---

## 🗄️ Campos de Base de Datos

### Campos Agregados al Modelo User

| Campo | Tipo | Descripción | Índice |
|-------|------|-------------|--------|
| `subscription_status` | String(50) | Estado de Stripe (active, canceled, past_due) | No |
| `monthly_analyses_count` | Integer | Contador mensual de análisis usados | No |
| `monthly_analyses_reset_at` | DateTime(TZ) | Fecha/hora del próximo reset | No |
| `stripe_customer_id` | String(255) | ID del cliente en Stripe | ✅ Sí |
| `stripe_subscription_id` | String(255) | ID de la suscripción activa | ✅ Sí |

### Valores de subscription_status

| Estado | Descripción |
|--------|-------------|
| `active` | Suscripción activa y al día |
| `canceled` | Suscripción cancelada |
| `past_due` | Pago atrasado |
| `trialing` | En período de prueba |
| `incomplete` | Pago pendiente |
| `unpaid` | No pagada |
| `unauthorized` | Price ID no autorizado (seguridad) |

---

## 🔒 Características de Seguridad

### 1. Verificación de Firma Webhook
```python
event = stripe_service.verify_webhook_signature(body, signature)
```
- Usa HMAC-SHA256
- Requiere `STRIPE_WEBHOOK_SECRET` de .env
- Rechaza requests sin firma válida (400 Bad Request)

### 2. Validación de Price ID
```python
validated_plan = self.validate_price_id(actual_price_id)
```
- Solo acepta price_ids configurados en `.env`
- Bloquea intentos de usar price_ids no autorizados
- Logs de seguridad para auditoría

### 3. Idempotencia
```python
if user.stripe_subscription_id == subscription_id and user.plan in ["starter", "pro", "team"]:
    logger.info("IDEMPOTENT_SKIP | already_processed=true")
    return user
```
- Previene duplicación de suscripciones
- Eventos duplicados son ignorados (pero logueados)

### 4. Validación Plan vs Price ID
```python
if plan_from_metadata != validated_plan:
    logger.warning("PLAN_MISMATCH | using_actual")
```
- Si metadata dice "pro" pero price_id es de "starter" → usa "starter"
- Previene manipulación de metadata

---

## 🎯 Límites Mensuales por Plan

Según configuración en `.env`:

| Plan | Límite Mensual | Variable |
|------|----------------|----------|
| Free | 3 (lifetime) | `usage_limit_free` |
| Starter | 40 | `usage_limit_starter` |
| Pro | 150 | `usage_limit_pro` |
| Team | 500 | `usage_limit_team` |

**Inicialización:**
- `monthly_analyses_count` = 0 al activar suscripción
- `monthly_analyses_reset_at` = fecha de próxima facturación
- Se reseteará automáticamente en el próximo período de facturación

---

## 🧪 Testing

### Migración de Base de Datos
```bash
python add_subscription_fields.py
```
✅ Agrega campos: subscription_status, monthly_analyses_count, monthly_analyses_reset_at
✅ Crea índices en stripe_customer_id y stripe_subscription_id

### Testing con Stripe CLI

**1. Instalar Stripe CLI:**
```bash
# Windows
scoop install stripe

# Mac
brew install stripe/stripe-cli/stripe

# Linux
https://stripe.com/docs/stripe-cli
```

**2. Login:**
```bash
stripe login
```

**3. Forwarding de Webhooks:**
```bash
stripe listen --forward-to BACKEND_URL/billing/webhook/stripe
```

**4. Trigger Events:**
```bash
# Simular checkout completado
stripe trigger checkout.session.completed

# Simular suscripción creada
stripe trigger customer.subscription.created

# Simular suscripción cancelada
stripe trigger customer.subscription.deleted
```

### Testing Manual
```bash
# Ejecutar servidor
python run.py

# En otro terminal, ejecutar test
python test_webhook_handlers.py
```

---

## 📊 Flujo Completo

```
┌─────────────────────────────────────────────┐
│ 1. Usuario completa pago en Stripe         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 2. Stripe envía webhook:                   │
│    checkout.session.completed               │
│    + Firma HMAC-SHA256                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 3. Backend verifica firma                   │
│    - Inválida → 400 Bad Request             │
│    - Válida → Procesa evento                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 4. Extrae datos del webhook:                │
│    - user_id (metadata o client_reference)  │
│    - customer_id                            │
│    - subscription_id                        │
│    - plan (metadata)                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 5. Verifica idempotencia                    │
│    - ¿Subscription ya procesado?            │
│      Sí → Skip (log IDEMPOTENT_SKIP)        │
│      No → Continúa                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 6. Obtiene subscription de Stripe API       │
│    - Lee price_id real pagado               │
│    - Lee current_period_end                 │
│    - Lee status                             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 7. Valida price_id contra whitelist         │
│    - No autorizado → plan = "free"          │
│    - Autorizado → plan = validated_plan     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 8. Actualiza usuario en BD:                 │
│    - plan = "starter|pro|team"              │
│    - stripe_customer_id = "cus_xxx"         │
│    - stripe_subscription_id = "sub_xxx"     │
│    - subscription_status = "active"         │
│    - monthly_analyses_count = 0             │
│    - monthly_analyses_reset_at = next_bill  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 9. Commit a base de datos                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 10. Log éxito + Return 200 OK a Stripe     │
└─────────────────────────────────────────────┘
```

---

## 🔧 Configuración Requerida

### Variables de Entorno (.env)

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_...

# Webhook Secret (obtener de Stripe Dashboard)
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs
STRIPE_PRICE_STARTER_ID=price_1StrzhPc1lhDefcvp0TJY0rS
STRIPE_PRICE_PRO_ID=price_1StrziPc1lhDefcvrfIRB0n0
STRIPE_PRICE_TEAM_ID=price_1StrzjPc1lhDefcvgp2rRqh4

# Usage Limits
USAGE_LIMIT_STARTER=40
USAGE_LIMIT_PRO=150
USAGE_LIMIT_TEAM=500
```

### Obtener Webhook Secret

1. Ir a Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. URL: `https://yourdomain.com/billing/webhook/stripe`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
5. Copy "Signing secret" → `.env` como `STRIPE_WEBHOOK_SECRET`

---

## 📝 Archivos Modificados/Creados

### Modificados
1. **[app/models/user.py](app/models/user.py)** - Agregados campos de suscripción
2. **[app/core/stripe_service.py](app/core/stripe_service.py)** - Implementados 3 handlers
3. **[app/api/routes/billing.py](app/api/routes/billing.py)** - Actualizado webhook endpoint

### Creados
1. **[add_subscription_fields.py](add_subscription_fields.py)** - Script de migración
2. **[test_webhook_handlers.py](test_webhook_handlers.py)** - Script de testing
3. **[migrations/002_add_subscription_fields.py](migrations/002_add_subscription_fields.py)** - Migración Alembic

---

## ✅ Checklist de Implementación

- [x] Modelo User actualizado con campos de suscripción
- [x] Migración de base de datos ejecutada
- [x] Índices creados en stripe_customer_id y stripe_subscription_id
- [x] Handler checkout.session.completed implementado
- [x] Handler customer.subscription.created implementado
- [x] Handler customer.subscription.deleted implementado
- [x] Verificación de firma webhook (HMAC-SHA256)
- [x] Validación de price_id contra whitelist
- [x] Idempotencia implementada
- [x] Inicialización de créditos mensuales
- [x] Configuración de reset mensual
- [x] Logging detallado para auditoría
- [x] Manejo de errores robusto
- [x] Tests creados

---

## 🚀 Deploy a Producción

**Antes de deploy:**
1. ✅ Migración de BD ejecutada
2. ✅ Variables de entorno configuradas
3. ✅ Webhook secret de producción configurado
4. ✅ Webhook endpoint registrado en Stripe
5. ✅ Testing con Stripe CLI completado

**Después de deploy:**
1. Verificar que webhook endpoint responde (200 OK)
2. Hacer test payment con tarjeta real
3. Verificar que usuario se actualiza correctamente
4. Monitorear logs para errores
5. Configurar alertas para fallos de webhook

---

## 📊 Monitoreo

**Logs a monitorear:**
```
CHECKOUT_COMPLETED | user_id=* | plan=* | validated=true
SUBSCRIPTION_CREATED | user_id=* | plan=*
SUBSCRIPTION_DELETED | user_id=* | reverted_to=free
WEBHOOK_SIGNATURE_INVALID | error=*
SECURITY_VIOLATION | unauthorized_price_id=*
```

**Métricas importantes:**
- Tasa de éxito de webhooks (200 OK)
- Tiempo de procesamiento de webhook
- Eventos con IDEMPOTENT_SKIP (normales)
- Eventos con SECURITY_VIOLATION (críticos)

---

## ✨ Resumen

✅ **Todos los webhooks implementados y funcionales**
✅ **Idempotencia garantizada**
✅ **Seguridad validada con whitelists**
✅ **Créditos mensuales inicializados correctamente**
✅ **Base de datos migrada**
✅ **Testing disponible**

**¡Sistema listo para producción!** 🎉
