# 🚀 Despliegue Completo: Render + Vercel + Stripe

## Estado Actual

✅ **Backend (.env local)**: Configurado con Stripe
✅ **Frontend (web/.env)**: Configurado para conectar a Render
✅ **Stripe**: Productos creados con Price IDs

---

## 📋 Paso 1: Desplegar Backend en Render

### 1.1 Crear cuenta en Render
- Ve a https://render.com
- Regístrate con GitHub

### 1.2 Crear PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Nombre: `linkedin-lead-checker-db`
3. Plan: **Free**
4. Región: Oregon (US West)
5. Click "Create Database"
6. **Copia el "Internal Database URL"** (postgresql+psycopg2://...)

### 1.3 Crear Web Service
1. Click "New +" → "Web Service"
2. Conecta tu repositorio GitHub
3. Configuración:
   - **Name**: `linkedin-lead-checker-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers`
   - **Plan**: Free

### 1.4 Configurar Variables de Entorno en Render

Click en "Environment" y agrega estas variables:

#### ✅ REQUERIDAS
```bash
DATABASE_URL=postgresql+psycopg2://user:pass@host/db  # Copiar de Postgres instance
JWT_SECRET_KEY=3f8a9c2e1d4b7e6f5a3c9e2d1b4f7a8c9e2d1b4f  # Generar con: openssl rand -hex 32
ENV=prod
```

#### ✅ CORS (Importante para que el frontend se conecte)
```bash
CORS_ALLOW_ORIGINS=FRONTEND_URL
CORS_ALLOW_ORIGIN_REGEX=chrome-extension://.*
```

#### ✅ STRIPE (Ya tienes estas en tu .env local)
```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_STARTER_ID=price_xxx
STRIPE_PRICE_PRO_ID=price_xxx
STRIPE_PRICE_TEAM_ID=price_xxx
```

#### ✅ OPENAI (Ya lo tienes)
```bash
OPENAI_ENABLED=true
OPENAI_API_KEY=sk-proj-xxxx
```

#### ✅ USAGE LIMITS
```bash
USAGE_LIMIT_STARTER=40
USAGE_LIMIT_PRO=150
USAGE_LIMIT_TEAM=500
SOFT_LAUNCH_MODE=true
DAILY_REGISTRATION_LIMIT=20
```

### 1.5 Desplegar
- Click "Create Web Service"
- Render desplegará automáticamente
- Espera 5-10 minutos
- URL será: `https://linkedin-lead-checker-api.onrender.com`

### 1.6 Verificar Backend
```bash
curl https://linkedin-lead-checker-api.onrender.com/health
```
Debería devolver: `{"status":"healthy"}`

---

## 📋 Paso 2: Configurar Webhook de Stripe

### 2.1 Ir a Stripe Dashboard
1. Ve a https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"

### 2.2 Configurar Endpoint
```
URL: https://linkedin-lead-checker-api.onrender.com/billing/webhook/stripe
Description: LinkedIn Lead Checker webhook
```

### 2.3 Seleccionar Eventos
- ✅ `checkout.session.completed`
- ✅ `customer.subscription.deleted`
- ✅ `customer.subscription.updated`

### 2.4 Copiar Webhook Secret
- Después de crear, verás el webhook secret (`whsec_...`)
- **SI ES DIFERENTE AL QUE YA TIENES**, actualízalo en Render Dashboard
  - Ve a Render → Tu servicio → Environment
  - Actualiza `STRIPE_WEBHOOK_SECRET`

---

## 📋 Paso 3: Desplegar Frontend en Vercel

### 3.1 Crear cuenta en Vercel
- Ve a https://vercel.com
- Regístrate con GitHub

### 3.2 Importar Proyecto
1. Click "Add New..." → "Project"
2. Selecciona tu repositorio
3. **Root Directory**: `web`
4. Framework Preset: Next.js (auto-detectado)

### 3.3 Configurar Variables de Entorno en Vercel
En "Environment Variables":

```bash
NEXT_PUBLIC_API_URL=https://linkedin-lead-checker-api.onrender.com
NEXT_PUBLIC_CHECKOUT_RETURN_URL=https://linkedin-lead-checker.vercel.app/checkout-result?session_id={CHECKOUT_SESSION_ID}
```

### 3.4 Desplegar
- Click "Deploy"
- Vercel desplegará automáticamente
- URL será: `https://linkedin-lead-checker.vercel.app`

---

## 📋 Paso 4: Actualizar CORS en Backend

Una vez que tengas la URL de Vercel:

1. Ve a Render Dashboard → Tu servicio → Environment
2. Actualiza `CORS_ALLOW_ORIGINS`:
   ```
  FRONTEND_URL
   ```
3. Guarda (Render redesplegará automáticamente)

---

## ✅ Verificación Final

### Backend (Render)
```bash
# Health check
curl https://linkedin-lead-checker-api.onrender.com/health

# Login test
curl -X POST https://linkedin-lead-checker-api.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

### Frontend (Vercel)
1. Abre `https://linkedin-lead-checker.vercel.app`
2. Intenta hacer login
3. Si funciona, ve a Pricing y prueba crear un checkout

### Stripe Webhook
1. Ve a Stripe Dashboard → Webhooks
2. Debería mostrar el endpoint como "Active"
3. Haz una compra de prueba
4. Verifica que el webhook recibe eventos

---

## 🔧 Para Desarrollo Local

### Backend
```bash
# Usar tu .env actual (ya configurado)
python run.py
```

### Frontend
```bash
cd web
npm run dev
```
Debería conectarse automáticamente a Render en producción.

---

## 📝 URLs de Referencia

| Servicio | URL | Dashboard |
|----------|-----|-----------|
| **Backend (Render)** | `https://linkedin-lead-checker-api.onrender.com` | https://dashboard.render.com |
| **Frontend (Vercel)** | `https://linkedin-lead-checker.vercel.app` | https://vercel.com/dashboard |
| **Database (Render)** | Internal URL en Render | https://dashboard.render.com |
| **Stripe** | - | https://dashboard.stripe.com |
| **Stripe Webhooks** | - | https://dashboard.stripe.com/test/webhooks |

---

## 🚨 Troubleshooting

### Error: "Failed to fetch"
- Verifica que `NEXT_PUBLIC_API_URL` esté configurado en Vercel
- Verifica que `CORS_ALLOW_ORIGINS` incluya tu dominio de Vercel en Render

### Error: "Checkout failed"
- Verifica que todos los `STRIPE_PRICE_*_ID` estén configurados en Render
- Verifica que `STRIPE_SECRET_KEY` sea correcto

### Error: "Database connection failed"
- Verifica que `DATABASE_URL` esté correcto en Render
- Verifica que la base de datos esté activa

### Backend muy lento (primera request)
- Es normal en Render Free (sleep después de 15 min de inactividad)
- Primera request tarda ~30-60 segundos en despertar

---

## 📊 Costos Estimados

| Servicio | Plan | Costo |
|----------|------|-------|
| Render (Backend) | Free | $0/mes |
| Render (Database) | Free | $0/mes |
| Vercel (Frontend) | Hobby | $0/mes |
| Stripe | Pay as you go | 2.9% + $0.30 por transacción |
| OpenAI | Pay as you go | ~$0.03 por análisis |

**Total base**: $0/mes + costos variables por uso

---

## 🎯 Próximos Pasos

1. ✅ Desplegar backend en Render
2. ✅ Desplegar frontend en Vercel
3. ✅ Configurar webhook de Stripe
4. ✅ Probar flujo completo de checkout
5. 📱 Desplegar extensión de Chrome
6. 🚀 Lanzar en ProductHunt / redes sociales

---

**¿Preguntas?** Revisa los archivos:
- [RENDER_SETUP.md](RENDER_SETUP.md) - Guía detallada de Render
- [STRIPE_INTEGRATION.md](STRIPE_INTEGRATION.md) - Guía de Stripe
- [web/VERCEL_DEPLOYMENT.md](web/VERCEL_DEPLOYMENT.md) - Guía de Vercel
