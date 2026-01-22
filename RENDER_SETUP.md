# 🚀 Render Free Deployment Guide

Esta guía paso a paso configura el backend en **Render Free Web Service** sin coste inicial.

## ✨ ¿Por qué Render Free?

| Ventaja | Detalles |
|---------|----------|
| 💰 **Sin tarjeta** | No requiere pago inicial |
| 🐘 **Postgres gratis** | 5GB incluidos |
| 🌙 **Sleep inteligente** | Duerme sin coste (se reactiva en <5s) |
| 🔐 **OpenAI = $0** | Deshabilitado por defecto |
| 📝 **Configuración simple** | Dashboard intuitivo |

---

## 📋 Pre-requisitos

- [ ] Repositorio en GitHub
- [ ] Render account: https://render.com (sign up es gratis)
- [ ] PostgreSQL en Render (lo crearemos juntos)
- [ ] Generador de secrets: `openssl rand -hex 32`

---

## 🔧 Paso 1: Configurar Database (PostgreSQL)

### En Render Dashboard:

1. **New** → **PostgreSQL**
2. **Name**: `linkedin-lead-checker-db`
3. **Region**: Frankfurt (EU) o tu región
4. **Plan**: Free (5GB)
5. **Crear**: Click "Create Database"

### Copiar Connection String:

Cuando la base de datos esté lista:
1. Ir a Database → Copy Connection String
2. Guardarlo (ejemplo: `postgresql+psycopg2://user:pass@host/db`)

> Este es tu `DATABASE_URL`

---

## 🔐 Paso 2: Generar JWT Secret

```bash
# En tu terminal local (NO en Render):
openssl rand -hex 32

# Output ejemplo:
# 3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c3e5d9f2b1a4c6e8d0f3a5b7c9e1d3f
```

Copia este valor, lo usarás como `JWT_SECRET_KEY`.

---

## 🌐 Paso 3: Crear Web Service

### En Render Dashboard:

1. **New** → **Web Service**
2. Conectar repositorio GitHub
3. Seleccionar branch: `main`

### Configuración:

| Campo | Valor |
|-------|-------|
| **Name** | `linkedin-lead-checker-api` |
| **Environment** | Python 3 |
| **Region** | Frankfurt o tu región |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers` |
| **Plan** | Free |

✅ Click **Create Web Service**

---

## 🔧 Paso 4: Variables de Entorno

Render automáticamente muestra el formulario para env vars.

### REQUERIDAS (sin estas, no arranca):

```
DATABASE_URL = postgresql+psycopg2://user:pass@host/db
JWT_SECRET_KEY = 3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c...
ENV = prod
```

### RECOMENDADAS (seguras por defecto):

```
OPENAI_ENABLED = false
```

### OPCIONALES (dejar vacías):

```
OPENAI_API_KEY = 
STRIPE_API_KEY = 
STRIPE_WEBHOOK_SECRET = 
STRIPE_PRICE_PRO_ID = 
STRIPE_PRICE_TEAM_ID = 
```

Luego iremos rellenándolas conforme necesites Stripe/OpenAI.

✅ Click **Save** (Render redeploya automáticamente)

---

## ✅ Paso 5: Verificar Despliegue

### Esperar a que compile:

1. Ir a **Logs** en Render Dashboard
2. Buscar:
   ```
   INFO: Environment: prod
   INFO: ✓ Required environment variables validated
   INFO: openai_enabled=false
   INFO: service_ready=true
   ```

### Probar Health Check:

```bash
# Reemplaza YOUR_SERVICE_NAME
curl https://linkedin-lead-checker-api.onrender.com/health

# Esperado:
# {"ok": true, "env": "prod"}
```

Si ves `{"ok": true}` → ¡Despliegue exitoso! ✅

---

## 🎯 Próximos Pasos

### Básico (Sin OpenAI/Stripe):
- ✅ Listo para usar
- ✅ Usuarios ven "Preview Mode"
- ✅ Coste = $0

### Agregar Stripe (Pagos):

1. Crear cuenta Stripe: https://stripe.com
2. Ir a API Keys (test o live)
3. Copiar `sk_test_...` o `sk_live_...`
4. En Render:
   - **STRIPE_API_KEY** = `sk_test_...`
   - **STRIPE_PRICE_PRO_ID** = (crear en Stripe dashboard)
   - **STRIPE_PRICE_TEAM_ID** = (crear en Stripe dashboard)
5. Configurar webhook:
   - URL: `https://linkedin-lead-checker-api.onrender.com/api/billing/webhook/stripe`
   - Eventos: `checkout.session.completed`, `customer.subscription.deleted`

### Agregar OpenAI (Análisis AI):

⚠️ **Esperar hasta tener suscriptores Pro** (para cubrir costos)

1. Crear cuenta OpenAI: https://platform.openai.com
2. Copiar API key
3. En Render:
   - **OPENAI_API_KEY** = `sk-proj-...`
   - **OPENAI_ENABLED** = `true`
4. Ahora sí, usuarios Pro tendrán análisis con AI

---

## 🆘 Troubleshooting

### Backend no arranca

**Síntoma**: Error 503 o "Build failed"

**Soluciones**:
1. Revisar **Logs** en Render Dashboard
2. Buscar "STARTUP VALIDATION ERROR"
3. Típicamente: falta `DATABASE_URL` o `JWT_SECRET_KEY`
4. Actualizar en **Environment** → Save → Redeploy

### Health check no responde

**Síntoma**: `curl /health` → timeout

**Soluciones**:
1. Esperar 30-60s tras redeploy (arranque lento en Free tier)
2. Verificar logs: "Backend ready to receive traffic"
3. Revisar que start command es exacto (no espacios extra)

### CORS errors

**Síntoma**: Extension no puede conectar

**Solución**:
```
CORS_ALLOW_ORIGINS = https://extension.example.com,https://app.example.com
```

### OpenAI regresa 503

**Si `OPENAI_ENABLED=false`** (por defecto):
- Esperado: usuarios ven preview mode
- No configurar OpenAI hasta tener suscriptores

**Si `OPENAI_ENABLED=true` pero sin suscriptores**:
- Presupuesto = $0 → análisis bloqueado
- Crear suscriptor Pro de prueba en Stripe

---

## 💰 Coste Garantizado = $0

| Componente | Coste | Condición |
|-----------|-------|-----------|
| Web Service (Free) | $0 | Sleep automático después 15 min |
| PostgreSQL (5GB) | $0 | Incluido en Free |
| OpenAI | **$0** | `OPENAI_ENABLED=false` (defecto) |
| Stripe | $0 | Sin transacciones sin suscriptores |
| **TOTAL** | **$0** | Hasta suscriptores Pro |

✨ **Garantía**: Render Free no gasta dinero hasta que haya usuarios pagos.

---

## 🎯 Checklist Final

- [ ] Database PostgreSQL creada en Render
- [ ] `DATABASE_URL` copiada
- [ ] `JWT_SECRET_KEY` generado (openssl rand -hex 32)
- [ ] Web Service creado
- [ ] Environment vars configuradas (requeridas + recomendadas)
- [ ] Health check responde: `{"ok": true}`
- [ ] Logs muestran: `service_ready=true`
- [ ] Backend en producción 🎉

---

## 📞 Soporte

Si algo no funciona:

1. **Revisar Logs** en Render Dashboard (hay mucha info)
2. **Curl health check**: `curl https://your-service.onrender.com/health`
3. **Validar env vars**: Todos los REQUERIDOS configurados
4. **Check JWT**: Mínimo 32 caracteres
5. **Database test**: Crear usuario en `/api/auth/signup` → si 400, DB funciona

---

**¡Listo para producción!** Ahora puedes:
- Integrar extensión Chrome
- Agregar Stripe cuando haya usuarios
- Habilitar OpenAI cuando haya presupuesto

🚀 Render Free + LinkedIn Lead Checker = MVP gratis
