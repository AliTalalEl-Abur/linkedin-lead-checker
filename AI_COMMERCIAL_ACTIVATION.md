# 💰 Sistema de Activación Comercial de IA

## 🎯 Objetivo

**NUNCA pagar OpenAI antes de tener revenue activo.**

---

## 🔐 Reglas de Activación

La IA **SOLO** se activa cuando se cumplen **TODAS** estas condiciones:

1. ✅ `OPENAI_ENABLED=true` (variable de entorno)
2. ✅ `OPENAI_API_KEY` configurada (válida)
3. ✅ **Al menos 1 suscriptor activo** (Starter, Pro o Business)

---

## 📊 Estados del Sistema

### 1. **OpenAI Deshabilitado** 
```
OPENAI_ENABLED=false
→ Razón: "openai_disabled"
→ Mensaje: "AI launching soon"
→ Log: "AI_DISABLED: OPENAI_ENABLED=false"
```

### 2. **Sin Suscriptores** (Pre-Launch)
```
OPENAI_ENABLED=true
+ 0 suscriptores activos
→ Razón: "no_subscribers"  
→ Mensaje: "Full AI analysis coming soon - join the waitlist!"
→ Log: "AI_NOT_ACTIVATED: No active subscribers yet"
```

### 3. **IA ACTIVADA** 🚀 (Primera Vez)
```
OPENAI_ENABLED=true
+ 1+ suscriptores activos
→ Estado: allowed=True
→ Mensaje en log:
   🚀🚀🚀 AI COMMERCIALLY ACTIVATED! 🚀🚀🚀 | 
   subscribers=X | OpenAI API calls NOW ENABLED | 
   We have REVENUE - safe to pay OpenAI costs
```

### 4. **Budget Agotado** (Runtime Protection)
```
Gasto mensual >= Budget
→ Razón: "exhausted"
→ HTTP 503: "Analysis temporarily unavailable"
→ Log: "Global AI budget exhausted"
```

---

## 🏗️ Arquitectura

### Flujo de Verificación

```
┌─────────────────────────────────────────────────────────┐
│  Usuario hace request de análisis                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  1. Check OPENAI_ENABLED                                │
│     ├─ false → Retorna "openai_disabled"               │
│     └─ true → Continúa                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Count Active Subscribers                            │
│     SELECT COUNT(*) FROM users                          │
│     WHERE plan IN ('starter', 'pro', 'business')        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Evaluate Budget Status                              │
│     ├─ 0 subscribers → "no_subscribers"                 │
│     ├─ budget <= 0 → "no_budget"                        │
│     ├─ spend >= budget → "exhausted"                    │
│     └─ OK → allowed=True                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. First Activation Detection                          │
│     if subscribers > 0 AND not _ai_activation_logged:   │
│        LOG: 🚀 AI COMMERCIALLY ACTIVATED! 🚀            │
│        _ai_activation_logged = True                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Return Preview or AI Analysis                       │
│     ├─ allowed=False → Preview Mode                     │
│     │   └─ Mensaje: "AI launching soon"                │
│     └─ allowed=True → Full AI Analysis                  │
│         └─ Llamada a OpenAI                             │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env file

# ============================================
# ACTIVACIÓN COMERCIAL DE IA
# ============================================

# 1. Habilitar OpenAI (default: false)
OPENAI_ENABLED=false           # Pre-launch: false
                               # Post-launch: true cuando tengas 1+ suscriptor

# 2. API Key de OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# ============================================
# PRESUPUESTO MENSUAL (Auto-calculado)
# ============================================

# Revenue por usuario (usado para calcular budget)
REVENUE_PER_STARTER_USER=1.20   # $9/mes → $1.20 budget IA
REVENUE_PER_PRO_USER=4.50       # $19/mes → $4.50 budget IA
REVENUE_PER_BUSINESS_USER=15.0  # $49/mes → $15 budget IA

# Costo estimado por análisis
AI_COST_PER_ANALYSIS_USD=0.03   # ~$0.03 por análisis

# ============================================
# KILL SWITCHES (Emergencias)
# ============================================

DISABLE_ALL_ANALYSES=false      # Mata TODO el análisis
DISABLE_FREE_PLAN=false         # Mata solo FREE plan
```

---

## 📝 Código Relevante

### 1. Verificación de Activación (`app/core/usage.py`)

```python
def evaluate_budget_status(db: Session) -> BudgetStatus:
    """
    Compute global budget availability based on active subscribers.
    
    COMMERCIAL ACTIVATION SYSTEM:
    - OpenAI only activates if OPENAI_ENABLED=true AND at least 1 active subscriber
    - If OPENAI_ENABLED=false → returns "openai_disabled"
    - If no active subscribers → returns "no_subscribers" (AI launching soon)
    - If budget exhausted → returns "exhausted" (CRITICAL)
    
    This ensures we NEVER PAY OPENAI BEFORE WE HAVE REVENUE.
    """
    settings = get_settings()
    
    # CRITICAL: Check if OpenAI is globally enabled first
    if not settings.openai_enabled:
        logger.info("AI_DISABLED: OPENAI_ENABLED=false")
        return BudgetStatus(
            budget=0.0,
            spend=0.0,
            active_pro_users=0,
            active_team_users=0,
            allowed=False,
            reason="openai_disabled",
        )
    
    active_starter, active_pro, active_business = get_active_subscriber_counts(db)
    total_subscribers = active_starter + active_pro + active_business
    
    budget = (
        (active_starter * settings.revenue_per_starter_user) +
        (active_pro * settings.revenue_per_pro_user) +
        (active_business * settings.revenue_per_business_user)
    )
    spend = get_monthly_ai_spend(db)

    # Check for first activation (0 -> 1+ subscribers)
    if total_subscribers > 0:
        _log_ai_activation_if_first(db, total_subscribers)

    if total_subscribers == 0:
        logger.info("AI_NOT_ACTIVATED: No active subscribers yet")
        return BudgetStatus(
            budget=budget,
            spend=spend,
            active_pro_users=active_pro,
            active_team_users=0,
            allowed=False,
            reason="no_subscribers",
        )
    
    # ... resto del código
```

### 2. Logging de Primera Activación

```python
# Global flag to track first activation
_ai_activation_logged = False

def _log_ai_activation_if_first(db: Session, subscriber_count: int) -> None:
    """
    Log when AI activates for the FIRST TIME (first paying subscriber).
    This is a critical business event: we can now start using OpenAI.
    """
    global _ai_activation_logged
    
    if not _ai_activation_logged and subscriber_count > 0:
        _ai_activation_logged = True
        logger.warning(
            "🚀🚀🚀 AI COMMERCIALLY ACTIVATED! 🚀🚀🚀 | "
            "subscribers=%d | OpenAI API calls NOW ENABLED | "
            "We have REVENUE - safe to pay OpenAI costs",
            subscriber_count
        )
```

### 3. Mensajes en Endpoints (`app/api/routes/analyze.py`)

```python
# Constantes de mensajes
AI_LAUNCHING_SOON = "AI analysis launching soon. Be among the first!"
AI_SOON_MESSAGE = "Full AI analysis coming soon - join the waitlist!"

# En _determine_preview()
if budget_status.reason == "no_subscribers":
    logger.info(
        "AI_LAUNCHING_SOON: No subscribers yet - showing preview (user_id=%d)",
        user.id
    )
    return True, "no_subscribers"

# En _free_tier_profile_response()
if preview_reason == "no_subscribers":
    banner = "Preview Mode"
    message = AI_SOON_MESSAGE

# En _preview_linkedin_response()
if preview_reason in ["no_subscribers", "openai_disabled"]:
    banner = "Preview Mode - AI Launching Soon"
```

---

## 🧪 Testing

### Pre-Launch (Sin Suscriptores)

```bash
# 1. Configurar
export OPENAI_ENABLED=true
export OPENAI_API_KEY=sk-xxxxx

# 2. Asegurar 0 suscriptores
sqlite3 linkedin_lead_checker.db
> UPDATE users SET plan='free' WHERE plan != 'free';

# 3. Hacer request de análisis
curl -X POST BACKEND_URL/analyze/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile": {...}}'

# Resultado esperado:
# {
#   "preview": true,
#   "message": "Full AI analysis coming soon - join the waitlist!",
#   "banner": "Preview Mode",
#   ...
# }

# Log esperado:
# INFO - AI_NOT_ACTIVATED: No active subscribers yet
# INFO - AI_LAUNCHING_SOON: No subscribers yet - showing preview
```

### First Activation (Primer Suscriptor)

```bash
# 1. Crear primer suscriptor
sqlite3 linkedin_lead_checker.db
> UPDATE users SET plan='starter' WHERE email='test@example.com';

# 2. Hacer request de análisis
curl -X POST BACKEND_URL/analyze/profile \
  -H "Authorization: Bearer <token_del_starter>" \
  -H "Content-Type: application/json" \
  -d '{"profile": {...}}'

# Log esperado (PRIMERA VEZ):
# WARNING - 🚀🚀🚀 AI COMMERCIALLY ACTIVATED! 🚀🚀🚀 | 
#           subscribers=1 | OpenAI API calls NOW ENABLED | 
#           We have REVENUE - safe to pay OpenAI costs
# INFO - Starting profile analysis (mock=False)
# INFO - Profile analysis completed in 2.34s

# Resultado esperado:
# {
#   "preview": false,
#   "should_contact": true,
#   "score": 85.0,
#   ...
# }
```

### OpenAI Deshabilitado

```bash
# 1. Deshabilitar OpenAI
export OPENAI_ENABLED=false

# 2. Hacer request (incluso con suscriptores activos)
curl -X POST BACKEND_URL/analyze/profile \
  -H "Authorization: Bearer <token>" \
  -d '{"profile": {...}}'

# Resultado:
# {
#   "preview": true,
#   "message": "AI launching soon. Be among the first!",
#   "banner": "Preview Mode",
#   ...
# }

# Log:
# INFO - AI_DISABLED: OPENAI_ENABLED=false
# INFO - AI_CALL_BLOCKED_OPENAI_DISABLED
```

---

## 📊 Monitoreo

### Queries Útiles

```sql
-- Contar suscriptores activos
SELECT 
  plan,
  COUNT(*) as count
FROM users 
WHERE plan IN ('starter', 'pro', 'business')
GROUP BY plan;

-- Ver gasto mensual de IA
SELECT 
  DATE_TRUNC('month', created_at) as month,
  COUNT(*) as analyses,
  SUM(cost_usd) as total_cost
FROM usage_events
WHERE event_type = 'profile_analysis'
GROUP BY month
ORDER BY month DESC;

-- Ver budget actual
SELECT 
  (SELECT COUNT(*) FROM users WHERE plan='starter') * 1.20 +
  (SELECT COUNT(*) FROM users WHERE plan='pro') * 4.50 +
  (SELECT COUNT(*) FROM users WHERE plan='business') * 15.0
AS monthly_ai_budget;
```

### Logs a Monitorear

```bash
# Buscar primera activación
grep "AI COMMERCIALLY ACTIVATED" server.log

# Ver intentos bloqueados
grep "AI_NOT_ACTIVATED" server.log

# Ver budget status
grep "evaluate_budget_status" server.log
```

---

## ⚠️ Advertencias

### 1. **No Desactivar OpenAI con Suscriptores Activos**
```bash
# ❌ MAL: Tienes suscriptores pero desactivas IA
OPENAI_ENABLED=false  # Con 10 suscriptores pagando

# Resultado: Usuarios PAGANDO pero sin servicio
# Solo hacer esto en emergencias
```

### 2. **El Flag de Activación NO Se Resetea**
```python
# _ai_activation_logged se mantiene True hasta restart del servidor
# Esto es intencional - solo queremos loguear la PRIMERA activación
```

### 3. **Test en Dev Sin Afectar Producción**
```bash
# Usa base de datos separada para testing
DATABASE_URL=sqlite:///./test.db python start_server.py
```

---

## 🚀 Deployment Checklist

### Pre-Launch
- [ ] `OPENAI_ENABLED=false` en producción
- [ ] Sin `OPENAI_API_KEY` configurada (o inválida)
- [ ] Usuarios pueden registrarse pero ven "AI launching soon"

### Soft Launch (Primeros Suscriptores)
- [ ] Configurar `OPENAI_API_KEY` válida
- [ ] `OPENAI_ENABLED=true`
- [ ] Monitorear logs para "AI COMMERCIALLY ACTIVATED"
- [ ] Verificar que primeros análisis funcionan
- [ ] Monitorear gasto en OpenAI dashboard

### Production
- [ ] Budget auto-calculado por suscriptores
- [ ] Alertas si `spend >= 80% * budget`
- [ ] Kill switch listo: `DISABLE_ALL_ANALYSES=true`
- [ ] Backup plan si OpenAI falla

---

## 📈 Ejemplo de Crecimiento

```
Mes 1:
- 0 suscriptores → OPENAI_ENABLED=false
- Budget: $0
- Gasto: $0
- Estado: "AI launching soon"

Mes 2 (Día 15):
- Primer suscriptor (Starter) → 🚀 AI ACTIVADA
- Budget: $1.20
- Gasto: $0.15 (5 análisis)
- Estado: ✅ Operando con ganancia

Mes 3:
- 10 Starter + 3 Pro
- Budget: (10 * $1.20) + (3 * $4.50) = $25.50
- Gasto: $18.00 (600 análisis)
- Margen: $7.50
- Estado: ✅ Escalando rentablemente

Mes 6:
- 50 Starter + 20 Pro + 5 Business
- Budget: $225
- Gasto: $180 (6,000 análisis)
- Margen: $45
- Estado: ✅ Producto consolidado
```

---

## ✅ Checklist de Implementación

- [x] `evaluate_budget_status` verifica OPENAI_ENABLED
- [x] Cuenta suscriptores activos antes de activar
- [x] Logging de primera activación con emoji 🚀
- [x] Mensajes específicos: "AI launching soon"
- [x] Preview mode cuando no hay suscriptores
- [x] Kill switch respetado (OPENAI_ENABLED)
- [x] Budget auto-calculado por revenue
- [x] Documentación completa

---

## 🎯 Resumen

**Sistema de 3 Niveles:**

1. **Pre-Launch:** `OPENAI_ENABLED=false` → Todos ven preview
2. **Soft Launch:** `OPENAI_ENABLED=true` + 0 suscriptores → Preview con "AI launching soon"
3. **Active:** `OPENAI_ENABLED=true` + 1+ suscriptores → **IA ACTIVADA** 🚀

**Garantía:**
> **Nunca pagaremos OpenAI antes de tener revenue activo.**

✅ Sistema implementado y funcionando.
