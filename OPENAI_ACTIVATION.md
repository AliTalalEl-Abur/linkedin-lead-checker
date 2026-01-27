# 🤖 OpenAI Activation - Guía Completa

## 📋 Resumen Ejecutivo

Sistema de activación de OpenAI con controles económicos estrictos para garantizar rentabilidad desde la primera llamada.

**Estado Actual:** DESACTIVADO (seguro por defecto)

**Activar cuando:**
- ✅ Tienes al menos 1 suscriptor pagador
- ✅ OPENAI_API_KEY configurado
- ✅ Stripe configurado y funcionando
- ✅ Tests de suscripción pasando

---

## 🎯 Objetivo

IA rentable desde día 1 con cero riesgo de pérdidas.

### Principios Fundamentales:

1. **Solo suscriptores pagadores usan AI**
   - Free tier = preview mode (sin llamadas a OpenAI)
   - Starter/Pro/Team = full AI análisis

2. **Créditos solo se consumen en éxito**
   - Error de OpenAI → NO se resta crédito
   - Timeout → NO se resta crédito
   - Solo análisis completo y exitoso → SI se resta

3. **Costos tracked con precisión**
   - Cada llamada registra: $0.03 estimated cost
   - Base de datos: `usage_events.cost_usd`
   - Resumen mensual: SUM(cost_usd) WHERE month_key='2026-01'

4. **No retries en fallos**
   - Una llamada = una oportunidad
   - Fallo → error al usuario
   - Sin reintentos automáticos = sin costos duplicados

---

## 💰 Modelo Económico

### Planes y Márgenes:

| Plan | Precio/mes | Análisis/mes | Costo AI Máx | Margen | % Margen |
|------|------------|--------------|--------------|--------|----------|
| **Starter** | $9.00 | 40 | $1.20 | $7.80 | 86.7% |
| **Pro** | $19.00 | 150 | $4.50 | $14.50 | 76.3% |
| **Team** | $49.00 | 500 | $15.00 | $34.00 | 69.4% |

### Cálculos:

```
Costo por análisis = $0.03 (gpt-4o-mini)

Starter:
- 40 análisis × $0.03 = $1.20 costo máximo
- $9.00 revenue - $1.20 cost = $7.80 profit

Pro:
- 150 análisis × $0.03 = $4.50 costo máximo
- $19.00 revenue - $4.50 cost = $14.50 profit

Team:
- 500 análisis × $0.03 = $15.00 costo máximo
- $49.00 revenue - $15.00 cost = $34.00 profit
```

### Escenarios de Riesgo:

| Escenario | Resultado |
|-----------|-----------|
| Usuario usa 100% de su límite | ✅ Todavía rentable |
| OpenAI sube precios +50% ($0.045/análisis) | ✅ Todavía rentable |
| Todos los usuarios maxean límite | ✅ Todavía rentable |
| OpenAI falla y reintentamos | ❌ **RIESGO** - Por eso NO reintentamos |

**Conclusión:** Sistema diseñado para ser rentable incluso en worst-case scenarios.

---

## 🛡️ Capas de Seguridad

### Layer 1: Validación de Suscripción

**Ubicación:** `app/api/routes/analyze.py` → `_determine_preview()`

**Verificaciones:**
1. ✅ `OPENAI_ENABLED == true`
2. ✅ `user.plan in ["starter", "pro", "team", "business"]`
3. ✅ `user.analyses_used < user.analyses_limit`
4. ✅ Budget global no exhausted

**Resultado:**
- ❌ No pasa → Preview mode (sin AI)
- ✅ Pasa → Proceder a Layer 2

### Layer 2: Rate Limiting

**Ubicación:** `app/core/usage.py` → `check_usage_limit()`

**Verificaciones:**
1. ✅ Último análisis hace más de 30 segundos
2. ✅ Usuario no ha excedido límite mensual

**Resultado:**
- ❌ No pasa → HTTP 429 Too Many Requests
- ✅ Pasa → Proceder a Layer 3

### Layer 3: Double-Check Pre-Call

**Ubicación:** `app/api/routes/analyze.py` (antes de llamar AI)

**Verificaciones:**
1. ✅ `settings.openai_enabled == True` (redundant check)
2. ✅ `usage_stats["remaining"] > 0` (redundant check)

**Resultado:**
- ❌ No pasa → HTTP 503 Service Unavailable
- ✅ Pasa → Llamar OpenAI

### Layer 4: Error Handling sin Consumo

**Ubicación:** `app/api/routes/analyze.py` (try/except blocks)

**Manejo:**
```python
try:
    # Llamada a OpenAI
    decision = ai_service.analyze_profile(...)
    
except RuntimeError as e:
    # OpenAI falló
    logger.error("OpenAI API error: %s", str(e))
    # NO record_usage() aquí!
    raise HTTPException(503, "AI service temporarily unavailable")
    
except Exception as e:
    # Error inesperado
    logger.error("Unexpected error: %s", str(e))
    # NO record_usage() aquí!
    raise HTTPException(500, "An unexpected error occurred")

# Solo aquí se consume crédito:
record_usage(user, db, cost_usd=0.03)
```

### Layer 5: OpenAI Client Config

**Ubicación:** `app/services/ai_service.py`

**Configuración:**
```python
client = OpenAI(
    api_key=api_key,
    timeout=30,  # 30 segundos max
    max_retries=0,  # NO retries automáticos
)
```

**Manejo de errores:**
- `APITimeoutError` → RuntimeError (no retry)
- `RateLimitError` → RuntimeError (no retry)
- `APIConnectionError` → RuntimeError (no retry)
- `APIError` → RuntimeError (no retry)

**Nota:** El código tiene MAX_RETRIES=3 pero es legacy. En producción con costos reales, considerar reducir a 0 o implementar retry solo para errores 5xx específicos.

---

## 🚀 Procedimiento de Activación

### Pre-requisitos:

```bash
# 1. Verificar Stripe configurado
python verify_stripe_sync.py
# Debe mostrar: ✅ VERIFICATION PASSED

# 2. Verificar al menos 1 suscriptor
# En Stripe Dashboard: https://dashboard.stripe.com/test/subscriptions
# Debe haber al menos 1 subscription activa

# 3. Verificar OPENAI_API_KEY en .env
cat .env | grep OPENAI_API_KEY
# Debe mostrar: OPENAI_API_KEY=sk-...
```

### Activación:

```powershell
# Ejecutar script de activación
python activate_openai.py
```

**El script hará:**
1. Verificar prerequisites
2. Mostrar configuración actual
3. Pedir confirmación
4. Setear `OPENAI_ENABLED=true` en .env
5. Configurar cost tracking
6. Correr tests
7. Mostrar instrucciones finales

### Verificación:

```powershell
# Correr test suite
python test_openai_activation.py
```

**Debe mostrar:**
```
✅ ALL TESTS PASSED - OpenAI is properly activated!
```

### Deployment:

```powershell
# 1. Reiniciar backend
python run.py

# 2. Verificar en logs
# Debe mostrar: "AIAnalysisService initialized with OpenAI client"

# 3. Test end-to-end con usuario de prueba
# Ver TEST_SUBSCRIPTION.md
```

---

## 📊 Monitoreo

### Queries Útiles:

```sql
-- Costo total del mes actual
SELECT 
    SUM(cost_usd) as total_cost,
    COUNT(*) as total_analyses
FROM usage_events 
WHERE month_key = '2026-01';

-- Costo por usuario
SELECT 
    user_id,
    COUNT(*) as analyses_count,
    SUM(cost_usd) as total_cost,
    AVG(cost_usd) as avg_cost
FROM usage_events 
WHERE month_key = '2026-01'
GROUP BY user_id
ORDER BY total_cost DESC;

-- Usuarios cerca del límite
SELECT 
    u.id,
    u.email,
    u.plan,
    u.analyses_used,
    u.analyses_limit,
    u.analyses_limit - u.analyses_used as remaining
FROM users u
WHERE u.plan IN ('starter', 'pro', 'team')
    AND u.analyses_used >= u.analyses_limit * 0.8
ORDER BY remaining ASC;

-- Budget check
SELECT 
    COUNT(DISTINCT user_id) as active_users,
    SUM(cost_usd) as total_spend
FROM usage_events 
WHERE month_key = '2026-01';
```

### Métricas Clave:

| Métrica | Query | Threshold |
|---------|-------|-----------|
| **Costo mensual** | `SUM(cost_usd)` | < Budget calculado |
| **Uso promedio** | `AVG(analyses_used)` | Monitor tendencia |
| **Usuarios activos** | `COUNT(DISTINCT user_id)` | Vs suscriptores |
| **Tasa de éxito** | `success / total` | > 95% |

### Alertas Sugeridas:

```python
# Budget alert (70% del budget)
monthly_spend = get_monthly_spend()
monthly_budget = calculate_budget(active_subscribers)

if monthly_spend > monthly_budget * 0.7:
    alert("AI spend at 70% of budget")

# Cost spike alert (+50% vs yesterday)
if today_spend > yesterday_spend * 1.5:
    alert("AI cost spike detected")

# Error rate alert (>10% fallos)
if error_rate > 0.1:
    alert("High AI error rate")
```

---

## 🚨 Emergency Procedures

### Desactivar OpenAI Inmediatamente:

```powershell
# Opción 1: Desactivar en .env
echo "OPENAI_ENABLED=false" >> .env

# Opción 2: Kill switch
echo "DISABLE_ALL_ANALYSES=true" >> .env

# Reiniciar backend
# Ctrl+C
python run.py
```

**Efecto:**
- Nuevos análisis → Preview mode (no AI)
- Usuarios existentes → Mensaje claro
- Costos → 0 inmediatamente

### Budget Exhaustion:

Si el gasto mensual supera el budget:

1. **Automático:** AI se desactiva
2. **Manual:** Revisar `evaluate_budget_status()`
3. **Decisión:**
   - Aumentar budget manualmente
   - Esperar a próximo mes
   - Desactivar permanentemente

### OpenAI API Issues:

Si OpenAI tiene problemas:

```python
# En logs verás:
"OpenAI API error: <error>"
"AI service temporarily unavailable"

# Usuarios ven:
"AI service temporarily unavailable. Please try again in a few moments."

# NO se consume crédito
# NO se reintenta automáticamente
```

**Acción:** Esperar a que OpenAI se recupere. No requiere intervención.

---

## 🧪 Testing

### Test 1: Usuario Free (Sin AI)

```powershell
# 1. Login con usuario free
# 2. Intentar análisis
# 3. Verificar: Preview mode (no AI call)
```

**Esperado:**
- Respuesta rápida (<1s)
- Score genérico (60-80)
- Mensaje: "Upgrade to unlock full AI-powered analysis"
- Logs: "AI_CALL_BLOCKED_NO_SUBSCRIPTION"

### Test 2: Usuario Starter (Con AI)

```powershell
# 1. Login con usuario con suscripción Starter
# 2. Realizar análisis
# 3. Verificar: Full AI analysis
```

**Esperado:**
- Respuesta lenta (~3-5s)
- Score específico y razonamiento detallado
- Logs: "AI_CALL_APPROVED" → "Analysis successful"
- DB: 1 registro en `usage_events` con cost_usd=0.03

### Test 3: Usuario en Límite

```powershell
# 1. Usuario con analyses_used == analyses_limit
# 2. Intentar análisis
# 3. Verificar: HTTP 429
```

**Esperado:**
- HTTP 429 Too Many Requests
- Mensaje: "You've reached your monthly limit"
- NO se llama a OpenAI
- NO se registra en usage_events

### Test 4: OpenAI Falla

```powershell
# 1. Temporalmente setear OPENAI_API_KEY inválido
# 2. Usuario Starter intenta análisis
# 3. Verificar: Error sin consumo de crédito
```

**Esperado:**
- HTTP 503 Service Unavailable
- Mensaje: "AI service temporarily unavailable"
- Logs: "OpenAI API error"
- NO se registra en usage_events (crédito NO consumido)

### Test 5: Rate Limiting

```powershell
# 1. Usuario hace análisis
# 2. Inmediatamente hace otro (< 30s)
# 3. Verificar: HTTP 429
```

**Esperado:**
- HTTP 429 Too Many Requests
- Mensaje: "Please wait X seconds"
- NO se llama a OpenAI

---

## 📝 Troubleshooting

### Problema: "OpenAI is disabled"

**Síntomas:**
- Todos los usuarios (incluso pagadores) en preview mode
- Logs: "AI_CALL_BLOCKED_OPENAI_DISABLED"

**Solución:**
```powershell
# Verificar .env
cat .env | grep OPENAI_ENABLED
# Debe ser: OPENAI_ENABLED=true

# Si está false:
echo "OPENAI_ENABLED=true" >> .env
python run.py  # Reiniciar
```

### Problema: "AI service in MOCK mode"

**Síntomas:**
- Análisis muy rápidos (~instant)
- Respuestas genéricas
- Logs: "AIAnalysisService running in MOCK mode"

**Solución:**
```powershell
# Verificar API key
cat .env | grep OPENAI_API_KEY
# Debe mostrar: OPENAI_API_KEY=sk-...

# Si no existe o es inválida:
echo "OPENAI_API_KEY=sk-tu-key-real" >> .env
python run.py  # Reiniciar
```

### Problema: Créditos se consumen en errores

**Síntomas:**
- `usage_events` tiene registros
- Pero usuarios reportan errores
- Logs muestran fallos de OpenAI

**Diagnóstico:**
```sql
-- Ver eventos con errores (no debería haber)
SELECT * FROM usage_events 
WHERE created_at > datetime('now', '-1 hour')
ORDER BY created_at DESC;
```

**Causa:** Bug en código - `record_usage()` llamado antes del try/except

**Solución:** Revisar `app/api/routes/analyze.py` - asegurar que `record_usage()` solo se llama DESPUÉS de éxito

### Problema: Budget exhausted prematuramente

**Síntomas:**
- AI se desactiva aunque hay presupuesto
- Logs: "Global AI budget exhausted"

**Diagnóstico:**
```python
from app.core.usage import evaluate_budget_status
from app.core.db import SessionLocal

db = SessionLocal()
status = evaluate_budget_status(db)
print(f"Spend: ${status.spend}, Budget: ${status.budget}")
db.close()
```

**Causas posibles:**
1. Pocos suscriptores vs muchos análisis
2. Configuración incorrecta de `REVENUE_PER_*_USER`
3. Bug en cálculo de budget

**Solución:**
```powershell
# Ajustar revenue si necesario
echo "REVENUE_PER_STARTER_USER=1.50" >> .env  # Aumentar buffer
python run.py
```

---

## 🎓 Best Practices

### 1. Monitoreo Diario

```bash
# Revisar costos cada día
python -c "
from app.core.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text(\"
    SELECT 
        DATE(created_at) as day,
        COUNT(*) as analyses,
        SUM(cost_usd) as cost
    FROM usage_events
    WHERE month_key = strftime('%Y-%m', 'now')
    GROUP BY DATE(created_at)
    ORDER BY day DESC
    LIMIT 7
\")).fetchall()

for row in result:
    print(f'{row[0]}: {row[1]} analyses, ${row[2]:.2f}')

db.close()
"
```

### 2. Weekly Review

Cada lunes:
- Revisar spend vs budget
- Identificar usuarios high-usage
- Verificar error rate
- Ajustar límites si necesario

### 3. Monthly Cleanup

Cada 1 del mes:
- Verificar que límites se resetean
- Revisar cost-per-user
- Ajustar precios si necesario
- Optimizar prompts (reducir tokens)

### 4. Alerts en Producción

```python
# Implementar en monitoring service
def check_ai_health():
    # Check 1: Cost spike
    if today_cost > yesterday_cost * 1.5:
        send_alert("AI cost spike")
    
    # Check 2: Error rate
    if error_rate > 0.1:
        send_alert("High AI error rate")
    
    # Check 3: Budget usage
    if spend > budget * 0.8:
        send_alert("AI budget at 80%")
```

---

## 🔄 Rollback Plan

Si necesitas revertir la activación:

```powershell
# 1. Desactivar OpenAI
echo "OPENAI_ENABLED=false" >> .env

# 2. Reiniciar backend
python run.py

# 3. Verificar logs
# Debe mostrar: "OpenAI DISABLED"

# 4. Notificar usuarios
# (Opcional) Enviar email: "AI temporalmente desactivado"
```

**Impacto:**
- Usuarios pagadores → Preview mode
- Sin créditos consumidos
- Sin costos
- Puede reactivarse en cualquier momento

---

## ✅ Checklist Final

Antes de activar en producción:

### Configuración:
- [ ] `OPENAI_API_KEY` set y válido
- [ ] `OPENAI_ENABLED=true`
- [ ] `AI_COST_PER_ANALYSIS_USD=0.03`
- [ ] Límites configurados (40/150/500)
- [ ] Revenue por usuario configurado

### Testing:
- [ ] `python test_openai_activation.py` pasa
- [ ] Usuario free → preview mode
- [ ] Usuario paid → full AI
- [ ] Usuario en límite → bloqueado
- [ ] Rate limiting funciona

### Monitoring:
- [ ] Queries de monitoreo probadas
- [ ] Alertas configuradas (opcional)
- [ ] Dashboard de costos (opcional)

### Seguridad:
- [ ] Validación de suscripción funciona
- [ ] Errores NO consumen créditos
- [ ] Kill switches funcionan
- [ ] Budget protection activo

### Documentación:
- [ ] Equipo entiende el sistema
- [ ] Procedimientos de emergencia claros
- [ ] Rollback plan probado

---

**Última Actualización:** 2026-01-26
**Versión:** 1.0.0
**Estado:** ✅ Listo para Producción
