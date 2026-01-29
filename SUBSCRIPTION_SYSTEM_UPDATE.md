# 🎯 Sistema de Suscripciones Actualizado

## ✅ Cambios Implementados

### 📊 Nuevos Planes de Suscripción

| Plan | Precio | Límite Mensual | Costo AI Máx |
|------|--------|----------------|--------------|
| **FREE** | $0 | 3 lifetime | $0.09 |
| **Starter** | $9/mes | 40 análisis/mes | $1.20/mes |
| **Pro** | $19/mes | 150 análisis/mes | $4.50/mes |
| **Business** | $49/mes | 500 análisis/mes | $15/mes |

### 🔒 Características de los Límites

✅ **Límites DUROS (Hard Cap)**
- Al alcanzar el límite → análisis bloqueado inmediatamente
- Error HTTP 429 con mensaje claro
- No hay análisis adicionales hasta el próximo mes

✅ **Sin Rollover Mensual**
- Los análisis no usados NO se acumulan
- Reset automático el día 1 de cada mes a las 00:00 UTC
- Cada mes comienza con el límite completo

✅ **Tracking Mensual**
- Sistema cambió de `week_key` (YYYY-WW) a `month_key` (YYYY-MM)
- Permite límites mensuales en lugar de semanales
- Compatible con datos históricos

### 📁 Archivos Modificados

#### 1. **app/core/config.py**
```python
# Nuevos límites mensuales
usage_limit_free: int = 3           # lifetime
usage_limit_starter: int = 40       # por mes
usage_limit_pro: int = 150          # por mes  
usage_limit_business: int = 500     # por mes

# Nuevos price IDs de Stripe
stripe_price_starter_id: Optional[str]
stripe_price_pro_id: Optional[str]
stripe_price_business_id: Optional[str]
```

#### 2. **app/core/utils.py**
- ✅ Agregada función `get_current_month_key()` → retorna "YYYY-MM"
- ✅ Agregada función `get_month_key_for_date(dt)` → convierte fecha a "YYYY-MM"

#### 3. **app/core/usage.py**
**Cambios principales:**
- ✅ Cambió `get_current_week_key()` por `get_current_month_key()`
- ✅ Consultas usan `month_key` en lugar de `week_key`
- ✅ Soporta 3 planes pagos: starter, pro, business
- ✅ Mensaje de error actualizado: "monthly limit" en lugar de "weekly limit"
- ✅ Error 429 con mensaje claro al alcanzar límite

**Funciones actualizadas:**
- `get_active_subscriber_counts()` → cuenta starter, pro, business
- `evaluate_budget_status()` → calcula budget con los 3 planes
- `check_usage_limit()` → verifica límites mensuales DUROS
- `record_usage()` → registra con month_key
- `get_usage_stats()` → devuelve estadísticas mensuales

#### 4. **app/core/stripe_service.py**
```python
def __init__(
    self, 
    starter_price_id: Optional[str],
    pro_price_id: Optional[str], 
    business_price_id: Optional[str]
):
    # Soporta 3 planes en lugar de 2
```

#### 5. **app/api/routes/billing.py**
- ✅ `CheckoutRequest.plan` acepta "starter", "pro", "business"
- ✅ Validación actualizada para los 3 planes
- ✅ Documentación de endpoint actualizada

#### 6. **app/models/usage_event.py**
```python
class UsageEvent(Base):
    week_key: Mapped[str] = mapped_column(nullable=True)  # Deprecated
    month_key: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)  # NEW
```

#### 7. **migrations/add_month_key_to_usage_events.py**
- ✅ Script de migración para agregar columna `month_key`
- ✅ Popula `month_key` desde `created_at` para registros existentes
- ✅ Crea índice para optimizar consultas

### 🚀 Cómo Usar

#### 1. Ejecutar Migración
```bash
python migrations/add_month_key_to_usage_events.py
```

#### 2. Configurar Variables de Entorno
```bash
# Stripe Price IDs (crear en Stripe Dashboard)
STRIPE_PRICE_STARTER_ID=price_xxx_starter  # $9/mes
STRIPE_PRICE_PRO_ID=price_xxx_pro         # $19/mes
STRIPE_PRICE_BUSINESS_ID=price_xxx_business # $49/mes
```

#### 3. Crear Productos en Stripe

**Starter Plan:**
- Nombre: "Starter Plan"
- Precio: $9.00 USD / mes (recurring)
- Descripción: "40 AI analyses per month"

**Pro Plan:**
- Nombre: "Pro Plan"  
- Precio: $19.00 USD / mes (recurring)
- Descripción: "150 AI analyses per month"

**Business Plan:**
- Nombre: "Business Plan"
- Precio: $49.00 USD / mes (recurring)
- Descripción: "500 AI analyses per month"

### 🔍 Cálculo de `remaining_analyses`

El endpoint `/user` devuelve automáticamente:

```json
{
  "usage": {
    "month_key": "2026-01",
    "used": 25,
    "limit": 150,
    "remaining": 125,
    "plan": "pro"
  }
}
```

**Lógica:**
```python
remaining = max(0, limit - used)
```

- ✅ Siempre >= 0 (nunca negativo)
- ✅ Se calcula en tiempo real en cada request
- ✅ Refleja el límite DURO actual

### 🛡️ Bloqueo al Alcanzar Límite

Cuando `used >= limit`:

```python
# Response
HTTP 429 Too Many Requests
{
  "detail": "You've reached your monthly limit (150 analyses/month). Your limit will reset on the 1st of next month."
}
```

**Comportamiento:**
- ❌ Análisis AI bloqueado completamente
- ✅ Usuario puede ver error claro
- ✅ No hay análisis adicionales hasta próximo mes
- ✅ No hay excepciones ni "bonus credits"

### 📈 Reset Mensual

- **Cuándo:** Día 1 de cada mes a las 00:00 UTC
- **Cómo:** Cambio de `month_key` (ej: "2026-01" → "2026-02")
- **Efecto:** Las consultas automáticamente usan el nuevo `month_key`
- **Resultado:** `used = 0` para el nuevo mes

### ✅ Verificación

Para verificar que todo funciona:

```bash
# 1. Correr migración
python migrations/add_month_key_to_usage_events.py

# 2. Iniciar servidor
python start_server.py

# 3. Verificar límites
curl -H "Authorization: Bearer <token>" BACKEND_URL/user

# 4. Probar análisis hasta alcanzar límite
# Debería devolver 429 al llegar al límite
```

### 🎯 Testing Checklist

- [ ] Migración ejecutada sin errores
- [ ] Price IDs configurados en .env
- [ ] Usuario FREE: límite de 3 lifetime
- [ ] Usuario Starter: límite de 40/mes
- [ ] Usuario Pro: límite de 150/mes
- [ ] Usuario Business: límite de 500/mes
- [ ] Error 429 al alcanzar límite
- [ ] remaining_analyses correcto en /user
- [ ] Reset automático al cambiar de mes
- [ ] Stripe checkout funciona para los 3 planes
- [ ] Webhook actualiza plan correctamente

---

## 📝 Notas Importantes

1. **Backward Compatible:** El campo `week_key` se mantiene para datos históricos
2. **Índices:** Se crean índices en `month_key` para performance
3. **Rate Limiting:** Se mantiene el rate limit de 30 segundos entre análisis
4. **Kill Switches:** Se mantienen los switches de emergencia

---

**Fecha:** 2026-01-24  
**Versión:** 2.0.0  
**Status:** ✅ Implementado
