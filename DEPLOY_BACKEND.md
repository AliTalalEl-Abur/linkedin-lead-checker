# Backend Deploy Guide - Render Free Web Service

🎯 **Objetivo**: Desplegar FastAPI en Render Free Web Service sin coste inicial.

> **Garantía**: Este backend puede ejecutarse en Render Free sin coste alguno hasta que haya suscriptores Pro.

---

## 🚀 Render Free Web Service (RECOMENDADO)

### Por qué Render Free es ideal:
- ✅ No requiere tarjeta de crédito
- ✅ Soporta Python y FastAPI nativamente
- ✅ Incluye Postgres gratuito
- ✅ Sleep automático (sin coste en inactividad)
- ✅ OpenAI deshabilitado por defecto (costo = $0)

### Pasos de Despliegue

#### 1. Preparar Base de Datos
```bash
# Crear instancia Postgres en Render
# Dashboard → New → PostgreSQL
# Plan: Free
# Copiar DATABASE_URL (ej: postgresql+psycopg2://...)
```

#### 2. Generar Secrets Seguros
```bash
# En terminal local (NO en Render):
openssl rand -hex 32
# Ejemplo output: 3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c3e5d9f2b1a4c6e8d0f3a5b7c9e1d3f

# Copiar este valor como JWT_SECRET_KEY
```

#### 3. Crear Web Service en Render
1. Ir a [render.com](https://render.com)
2. Dashboard → **New** → **Web Service**
3. Conectar repositorio Git
4. Configurar:

| Campo | Valor |
|-------|-------|
| **Name** | `linkedin-lead-checker-api` |
| **Environment** | Python 3 |
| **Region** | Frankfurt (EU) o Virginia (US) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers` |
| **Plan** | Free |

#### 4. Variables de Entorno (Render Dashboard)

**REQUERIDAS** (El servicio no arrancará sin estas):

```
DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname
JWT_SECRET_KEY=3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c3e5d9f2b1a4c6e8d0f3a5b7c9e1d3f
ENV=prod
```

**RECOMENDADAS** (Seguras por defecto):

```
OPENAI_ENABLED=false
CORS_ALLOW_ORIGINS=https://linkedin-lead-checker.extension.com,https://app.example.com
```

**OPCIONALES** (No rompen arranque si faltan):

```
OPENAI_API_KEY=sk-... (solo si OPENAI_ENABLED=true)
STRIPE_API_KEY=sk_live_... o sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO_ID=price_1A2B3C4D...
STRIPE_PRICE_TEAM_ID=price_5E6F7G8H...
```

#### 5. Health Check (Configuración Automática)
Render detecta automáticamente `/health`. Verifica:

```bash
curl https://your-service.onrender.com/health
# Respuesta esperada:
# {"ok": true, "env": "prod"}
```

#### 6. Deploy
1. Push a main branch
2. Render despliega automáticamente
3. Verifica logs en Dashboard → Logs
4. Busca: `service_ready=true` ✓

---

## ✅ Startup Validation Checklist

El backend loggea estos mensajes al arrancar (verifica en Render Logs):

```
INFO: Environment: prod
INFO: ✓ Required environment variables validated
INFO: openai_enabled=false
INFO: service_ready=true
```

**No deben aparecer:**
- ❌ `STARTUP VALIDATION ERROR`
- ❌ `ERROR` (excepto warnings normales)
- ❌ `connection refused` (DB error)

---

## 📋 Variables de Entorno Explicadas

### REQUERIDAS

| Variable | Valor Ejemplo | Descripción |
|----------|---------------|------------|
| `DATABASE_URL` | `postgresql+psycopg2://...` | Conexión PostgreSQL. Cópiala desde Render Postgres instance |
| `JWT_SECRET_KEY` | `openssl rand -hex 32` | Mínimo 32 caracteres. **NUNCA** usar valor por defecto en prod |
| `ENV` | `prod` | Activa modo producción en Render |

### RECOMENDADAS

| Variable | Valor Defecto | Descripción |
|----------|--------------|------------|
| `OPENAI_ENABLED` | `false` | **Mantén en false** hasta tener suscriptores Pro. Evita coste OpenAI |
| `CORS_ALLOW_ORIGINS` | `localhost` | Actualiza con tu dominio de extensión/webapp |

### OPCIONALES (No rompen arranque si faltan)

| Variable | Descripción |
|----------|------------|
| `OPENAI_API_KEY` | Solo necesaria si `OPENAI_ENABLED=true` |
| `STRIPE_API_KEY` | Si no está, Stripe deshabilitado (sin pagos) |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification |
| `STRIPE_PRICE_PRO_ID` | ID de plan Pro en Stripe |
| `STRIPE_PRICE_TEAM_ID` | ID de plan Team en Stripe |

---

## 🛡️ Comportamiento en Render Free (CRÍTICO)

### Arranque Rápido
```
✓ Sin migraciones bloqueantes
✓ Sin llamadas a OpenAI en startup
✓ Sin tareas programadas
✓ Sin workers en background
Resultado: Arranque < 10 segundos
```

### OpenAI = $0 (Por Defecto)
```
Si OPENAI_ENABLED=false (por defecto):
  → OpenAI NO se ejecuta
  → Usuarios ven "Preview Mode"
  → Coste = $0
  
Si no hay suscriptores activos:
  → Presupuesto global = $0
  → OpenAI bloqueado automáticamente
  → Coste = $0
```

### Sleep Policy (Render Free)
```
Después de 15 min inactividad:
  → Servicio duerme (no gasta RAM/CPU)
  → Próxima solicitud lo reactiva (~5s)
  → Base de datos sigue activa
  → Sin coste de versionado/almacenamiento
```

---

## 🔧 Comandos de Build & Start (EXACTOS)

**Build Command** (instala dependencias):
```bash
pip install -r requirements.txt
```

**Start Command** (inicia servidor):
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers
```

⚠️ **No usar** `application` en lugar de `app` (es `app.main:app`)

---

## 📊 Health Check (Render-Compatible)

**Endpoint**: `GET /health`

**Características**:
- ✅ Siempre devuelve `200 OK`
- ✅ No depende de Database
- ✅ No depende de OpenAI
- ✅ No depende de Stripe
- ✅ No depende de suscriptores activos

**Respuesta**:
```json
{
  "ok": true,
  "env": "prod"
}
```

---

## 🔐 Configuración de Seguridad

### JWT_SECRET_KEY (CRÍTICO)

**Generar seguro**:
```bash
# En tu máquina local:
openssl rand -hex 32

# Resultado: 3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c...
# Copiar a Render → Environment Variables → JWT_SECRET_KEY
```

**Validación automática**:
- ✓ Mínimo 32 caracteres (validado en startup)
- ✓ No puede ser el valor por defecto en `env=prod`
- ✓ Error fatídico si no cumple (backend no arranca)

### Database (DATABASE_URL)

**Formato requerido**:
```
postgresql+psycopg2://user:password@host:5432/database
```

**Cómo obtener en Render**:
1. Dashboard → Postgres Instance
2. Copiar "Connection string"
3. Pegar en Render Web Service → Environment → DATABASE_URL

### CORS Origins

**Actualizar según tu extensión/webapp**:
```
CORS_ALLOW_ORIGINS=https://tu-extension.chrome,https://app.example.com
```

**Defecto**: Permite `chrome-extension://.*` (extensión local)

---

## 🧪 Testing Post-Deploy

### 1. Health Check
```bash
curl https://your-service.onrender.com/health
# Esperado: {"ok": true, "env": "prod"}
```

### 2. Logs
```
Render Dashboard → Service → Logs
Buscar: "service_ready=true"
```

### 3. Database Connectivity
```bash
# Auth endpoint (verifica conexión DB):
curl -X POST https://your-service.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
# Si responde 200/400/422 → DB ok
# Si 503/timeout → DB error
```

### 4. OpenAI Status
```bash
# Crear usuario y solicitar análisis:
# Debe devolver 200 con "preview_mode": true
# No debe hacer llamada a OpenAI (si OPENAI_ENABLED=false)
```

---

## 🆘 Troubleshooting

### Backend no arranca
```
Causa: STARTUP VALIDATION ERROR
Solución:
  1. Verifica DATABASE_URL en Render env vars
  2. Verifica JWT_SECRET_KEY existe y ≥32 caracteres
  3. Verifica ENV=prod
  4. Revisa logs exactos en Render Dashboard
```

### Health check falla
```
Causa: Servicio no escuchando en puerto correcto
Solución:
  1. Verifica start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  2. Espera 30s después de deploy (arranque lento en free tier)
  3. Revisa logs: "Backend ready to receive traffic"
```

### CORS errors en extensión
```
Solución:
  1. Actualiza CORS_ALLOW_ORIGINS con dominio exacto
  2. Sin trailing slash: https://example.com (no https://example.com/)
  3. Para extensión: mantén CORS_ALLOW_ORIGIN_REGEX=chrome-extension://.*
```

### Analítica devuelve 503
```
Si OPENAI_ENABLED=false (por defecto):
  → Esperado: Preview mode (sin análisis)
  → Solución: No configurar OpenAI hasta tener suscriptores
  
Si OPENAI_ENABLED=true pero sin suscriptores:
  → Presupuesto = $0 → análisis bloqueado
  → Solución: Crea suscriptor Pro de prueba en Stripe
```

---

## 💰 Garantía de Costo Zero

Este backend en Render Free garantiza **costo = $0** hasta suscriptores Pro:

| Recurso | Costo Free | Condición |
|---------|-----------|-----------|
| **Web Service** | Gratis | Sleep after 15min inactivity |
| **PostgreSQL** | Gratis | Incluido (hasta 5GB) |
| **OpenAI API** | **$0** | `OPENAI_ENABLED=false` (defecto) |
| **Stripe** | Gratis | Sin transacciones sin suscriptores |

**Total**: `$0/mes` hasta suscriptores Pro ✅

---

## 📈 Escalada a Producción

Cuando tengas usuarios pagos:

1. **Upgrade Render**:
   - Plan: Starter ($7/mes) o Pro ($12/mes)
   - Quita sleep (always on)

2. **Habilitar OpenAI**:
   ```
   OPENAI_ENABLED=true
   OPENAI_API_KEY=sk-...
   ```
   Costo protegido: (suscriptores × $12-36) covers OpenAI

3. **Stripe Webhook**:
   ```
   https://your-service.onrender.com/api/billing/webhook/stripe
   ```
   Verificado automáticamente

4. **Monitoring**:
   - Logs: Render Dashboard
   - Errors: Integrar con Sentry (opcional)
   - Uptime: Render alerts

---

## ✨ Diferencias con Otras Plataformas

| Aspecto | Render Free | Fly.io | Railway |
|--------|-----------|--------|----------|
| **Coste Base** | Gratis | Gratis (generoso) | $5/mes min |
| **PostgreSQL Gratis** | ✅ 5GB | ✅ 3GB | ❌ No incluido |
| **Python Support** | ✅ Nativo | ✅ Docker | ✅ Nativo |
| **Health Checks** | ✅ Automático | ✅ Manual | ✅ Manual |
| **Deploy Git** | ✅ Auto | ⚠️ Manual | ✅ Auto |
| **Sleep Policy** | ✅ 15min | ❌ Siempre on | ❌ Siempre on |
| **Recomendado para MVP** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📝 Checklist Final

- [ ] Repository en GitHub/GitLab (Render lo detecta)
- [ ] `requirements.txt` actualizado con todas las dependencias
- [ ] `app/main.py` define `app = create_app()`
- [ ] `DATABASE_URL` válida (Postgres en Render)
- [ ] `JWT_SECRET_KEY` ≥32 caracteres (generado con openssl)
- [ ] `ENV=prod` configurado
- [ ] `OPENAI_ENABLED=false` (por defecto, seguro)
- [ ] CORS origins actualizado
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers`
- [ ] Health check responde: `GET /health` → `{"ok": true}`
- [ ] Logs muestran: `service_ready=true` ✓

---

## 🎉 ¡Listo!

Backend desplegado en Render Free, sin coste, listo para producción.
Próximo paso: Integrar extensión Chrome y configurar Stripe cuando haya usuarios.

