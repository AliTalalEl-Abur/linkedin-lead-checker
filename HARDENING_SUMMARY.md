# Hardening y Control de Límites

Sistema de hardening implementado para garantizar estabilidad, control de costos y manejo robusto de errores.

## 🛡️ Características Implementadas

### 1. **Timeouts**
- **Timeout OpenAI**: 30 segundos por llamada
- Configurado a nivel de cliente OpenAI
- Evita llamadas colgadas que consumen recursos
- Ubicación: `app/services/ai_service.py`

```python
OPENAI_TIMEOUT = 30  # seconds
client = OpenAI(api_key=key, timeout=OPENAI_TIMEOUT)
```

### 2. **Retries con Backoff Exponencial**
- **Máximo de reintentos**: 3 intentos
- **Estrategia de backoff**: Exponencial con límite máximo
- **Delay base**: 1 segundo
- **Delay máximo**: 10 segundos (20s para rate limits)

```python
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 10  # seconds

# Fórmula: min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
# Attempt 1: 1s
# Attempt 2: 2s
# Attempt 3: 4s
```

### 3. **Manejo Robusto de Errores OpenAI**

#### Errores Manejados:
- **APITimeoutError**: Reintentos con backoff
- **RateLimitError**: Reintentos con backoff extendido (2x)
- **APIConnectionError**: Reintentos con backoff
- **APIError 5xx**: Reintentos (errores de servidor)
- **APIError 4xx**: NO reintenta (errores de cliente)
- **JSONDecodeError**: Falla inmediatamente
- **Errores inesperados**: Falla inmediatamente

#### Ejemplo de Manejo:

```python
try:
    completion = client.chat.completions.create(...)
except APITimeoutError:
    # Retry with exponential backoff
except RateLimitError:
    # Retry with extended backoff (2x)
except APIConnectionError:
    # Retry with backoff
except APIError as e:
    if 500 <= e.status_code < 600:
        # Server error - retry
    else:
        # Client error (4xx) - fail immediately
```

### 4. **Kill Switches para Free Users**

Dos niveles de control de emergencia:

#### Kill Switch Global
```python
disable_all_analyses: bool = False  # Desactiva TODOS los análisis
```

**Uso**: Emergencias críticas, mantenimiento, incidentes de seguridad

#### Kill Switch FREE Plan
```python
disable_free_plan: bool = False  # Desactiva solo plan FREE
```

**Uso**: Control de costos, abuso detectado en tier gratuito

#### Implementación:
```python
# En check_usage_limit() - se ejecuta ANTES de cualquier llamada a OpenAI
if settings.disable_all_analyses:
    raise HTTPException(503, "Service temporarily disabled")

if user.plan == "free" and settings.disable_free_plan:
    raise HTTPException(402, "Free plan temporarily disabled. Upgrade to Pro.")
```

### 5. **Logging Básico Estructurado**

Sistema de logging jerárquico con niveles apropiados:

#### Configuración Global
```python
# En main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

#### Eventos Registrados:

**INFO**:
- Inicio de aplicación
- Inicialización de servicios
- Análisis exitosos
- Checks de límites pasados
- Duración de operaciones

**WARNING**:
- Kill switches activados
- Rate limits excedidos
- Límites de plan alcanzados
- Reintentos de OpenAI

**ERROR**:
- Fallos de OpenAI después de reintentos
- Errores de parsing JSON
- Errores inesperados

#### Ejemplos de Logs:

```
2026-01-21 10:30:15 - app.main - INFO - Starting LinkedIn Lead Checker API
2026-01-21 10:30:15 - app.services.ai_service - INFO - AIAnalysisService initialized with OpenAI client (timeout=30s)
2026-01-21 10:30:20 - app.core.usage - INFO - PRO user_id=123 usage check passed (5/100 used this week)
2026-01-21 10:30:22 - app.services.ai_service - INFO - Profile analysis completed in 2.34s
2026-01-21 10:31:45 - app.core.usage - WARNING - Rate limit exceeded for user_id=456 (plan=free, wait=15s)
2026-01-21 10:32:10 - app.services.ai_service - WARNING - OpenAI timeout on attempt 1/3
2026-01-21 10:32:12 - app.services.ai_service - INFO - Retrying in 1.0s...
```

## 🎯 Flujo de Protección

### Orden de Ejecución:
1. **Autenticación** (JWT token)
2. **Kill Switch Global** (service disabled?)
3. **Kill Switch FREE** (free plan disabled?)
4. **Rate Limit** (30 segundos entre análisis)
5. **Plan Limit** (FREE: 3 total, PRO: 100/semana, TEAM: 300/semana)
6. **OpenAI Call** (con timeout, retries, error handling)
7. **Record Usage** (solo si exitoso)

```
Request → Auth → Kill Switches → Rate Limit → Plan Limit → AI Call → Usage Record → Response
          ↓        ↓               ↓            ↓            ↓          ↓
         402      503             429          402/429      503/500    200
```

## 📊 Códigos de Estado HTTP

| Código | Situación | Descripción |
|--------|-----------|-------------|
| 200 | Éxito | Análisis completado |
| 402 | Payment Required | Límite FREE alcanzado o FREE plan deshabilitado |
| 429 | Too Many Requests | Rate limit o límite semanal excedido |
| 500 | Internal Server Error | Error inesperado o JSON inválido |
| 503 | Service Unavailable | Kill switch global o error OpenAI después de reintentos |

## 🔧 Variables de Entorno

```bash
# Configuración de OpenAI (ya existente)
OPENAI_API_KEY=sk-...

# Kill Switches (nuevos)
DISABLE_ALL_ANALYSES=false      # Emergencia global
DISABLE_FREE_PLAN=false          # Control de tier gratuito

# Límites (ya existentes)
USAGE_LIMIT_FREE=3              # Total lifetime
USAGE_LIMIT_PRO=100             # Por semana
USAGE_LIMIT_TEAM=300            # Por semana
RATE_LIMIT_SECONDS=30           # Entre análisis
```

## 🧪 Testing

### Test de Timeout
```python
# Forzar timeout (ajustar OPENAI_TIMEOUT = 1)
# Debería reintentar 3 veces y luego fallar con 503
```

### Test de Retries
```python
# Simular error de red intermitente
# El sistema debería recuperarse automáticamente
```

### Test de Kill Switches
```bash
# Test 1: Kill switch global
export DISABLE_ALL_ANALYSES=true
# Resultado: 503 Service Unavailable para todos los usuarios

# Test 2: Kill switch FREE
export DISABLE_FREE_PLAN=true
# Resultado: 402 Payment Required solo para usuarios FREE
```

### Test de Logging
```bash
# Ejecutar servidor y verificar logs
uvicorn app.main:application --log-level info

# Deberías ver:
# - INFO al iniciar
# - INFO/WARNING en cada análisis
# - ERROR si hay fallos
```

## 📈 Monitoreo

### Logs Críticos a Vigilar:

1. **Kill Switch Activations**:
   ```
   WARNING - KILL SWITCH TRIGGERED: All analyses disabled
   WARNING - KILL SWITCH TRIGGERED: Free plan disabled
   ```

2. **Rate Limit Patterns**:
   ```
   WARNING - Rate limit exceeded for user_id=X
   ```
   Si es frecuente: posible abuso o ajustar límite

3. **OpenAI Errors**:
   ```
   ERROR - OpenAI API error after 3 attempts
   ERROR - OpenAI rate limit exceeded after 3 attempts
   ```
   Si es frecuente: revisar límites de API o aumentar timeout

4. **Performance**:
   ```
   INFO - Profile analysis completed in X.XXs
   ```
   Monitorear duración promedio (debería ser < 5s)

## 🚨 Respuesta a Incidentes

### Escenario 1: OpenAI Down
```bash
# Acción: Activar kill switch global
export DISABLE_ALL_ANALYSES=true
# O actualizar en base de datos/config management
```

### Escenario 2: Abuso del Tier FREE
```bash
# Acción: Deshabilitar plan FREE temporalmente
export DISABLE_FREE_PLAN=true
```

### Escenario 3: Costos Elevados
1. Revisar logs para identificar usuarios con alto uso
2. Considerar reducir límites temporalmente
3. Activar kill switch si es urgente

## ✅ Beneficios Implementados

- ✅ **Resiliencia**: Sistema se recupera automáticamente de errores transitorios
- ✅ **Control de Costos**: Kill switches previenen gastos no autorizados
- ✅ **Observabilidad**: Logs estructurados facilitan debugging
- ✅ **User Experience**: Mensajes de error claros y específicos
- ✅ **Seguridad**: Validación en múltiples capas antes de llamadas costosas
- ✅ **Mantenibilidad**: Código bien documentado con constantes configurables

## 📝 Próximos Pasos (Opcionales)

- [ ] Integrar con servicio de métricas (Prometheus, DataDog)
- [ ] Añadir alertas automáticas por email/Slack
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Circuit breaker pattern para fallos consecutivos
- [ ] Rate limiting por IP además de por usuario
- [ ] Logs estructurados en formato JSON para mejor parsing
