# 🎯 Configuración Final de Stripe - Guía Paso a Paso

**Status**: ✅ Productos ya creados | ⚠️ Webhook pendiente

## ✅ Verificación: Productos Configurados

Tu `.env` ya tiene los price IDs correctos:

```env
STRIPE_PRICE_STARTER_ID=price_1Ssu7IPc1lhDefcvGhmgzOoZ  # $9/mo - 40 análisis
STRIPE_PRICE_PRO_ID=price_1Ssu7KPc1lhDefcvgbL0z62T      # $19/mo - 150 análisis
STRIPE_PRICE_BUSINESS_ID=price_1Ssu7LPc1lhDefcv6NzhAtgz # $49/mo - 500 análisis
STRIPE_WEBHOOK_SECRET=whsec_4ec04ff985219270dabdf72840814c9505af3b6bf2e136398011398a3bcd90c9
```

✅ **Productos creados en Stripe** (Enero 2026)  
✅ **Price IDs configurados**  
✅ **API Key configurada**

---

## 🔗 Paso Final: Configurar Webhook en Stripe

### 1. Abre Stripe Dashboard

**Test Mode** (para pruebas):
```
https://dashboard.stripe.com/test/webhooks
```

**Live Mode** (para producción):
```
https://dashboard.stripe.com/webhooks
```

### 2. Click "Add endpoint"

### 3. Configura el endpoint:

**Endpoint URL**:
- **Webhook URL**: `BACKEND_URL/billing/webhook/stripe`
- **Render production**: `https://linkedin-lead-checker-api.onrender.com/billing/webhook/stripe`
- **Vercel/otro**: `https://tu-dominio.com/billing/webhook/stripe`

### 4. Selecciona eventos (Select events):

Marca estos 3 eventos:

```
✅ checkout.session.completed
✅ customer.subscription.deleted  
✅ customer.subscription.updated
```

**Descripción de cada evento**:
- `checkout.session.completed` → Usuario completa el pago (activa plan)
- `customer.subscription.deleted` → Usuario cancela suscripción (vuelve a free)
- `customer.subscription.updated` → Usuario cambia de plan o actualiza método de pago

### 5. Copia el Webhook Secret

Después de crear el webhook, Stripe te mostrará un **Signing secret**:

```
whsec_...
```

Copia este valor y actualiza tu `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_tu_nuevo_secret_aqui
```

---

## 🧪 Testing del Webhook (Local)

Si quieres probar webhooks localmente, usa **Stripe CLI**:

### Instalar Stripe CLI:

```powershell
# Usando Scoop (Windows)
scoop install stripe

# O descarga desde:
# https://github.com/stripe/stripe-cli/releases
```

### Forward webhooks:

```powershell
stripe login
stripe listen --forward-to BACKEND_URL/billing/webhook/stripe
```

Esto te dará un webhook secret temporal que puedes usar en `.env` local.

### Trigger test events:

```powershell
# Test checkout completed
stripe trigger checkout.session.completed

# Test subscription deleted
stripe trigger customer.subscription.deleted
```

---

## 🚀 Verificar que Todo Funciona

### 1. Reinicia el backend:

```powershell
cd c:\Users\LENOVO\Desktop\linkedin-lead-checker
python start_server.py
```

Deberías ver en los logs:

```
Stripe: ENABLED (billing available)
  - starter_price_id: configured
  - pro_price_id: configured
  - business_price_id: configured
  - webhook_secret: configured
```

### 2. Test checkout desde la extensión:

1. Login en la extensión
2. Click "View Pricing Plans"
3. Selecciona un plan
4. Deberías ver el checkout de Stripe

### 3. Monitorea los logs:

```powershell
# Mientras el servidor corre, busca estos eventos:
# CHECKOUT_STARTED | user_id=... | plan=pro | session_id=cs_...
# CHECKOUT_COMPLETED | user_id=... | plan=pro | customer_id=cus_...
# SUBSCRIPTION_ACTIVATED | user_id=... | plan=pro | subscription_id=sub_...
```

---

## 📊 Monitoreo en Producción

Cuando despliegues en Render, verifica:

### Logs del servidor:

```bash
# En Render dashboard → Logs
grep "CHECKOUT_STARTED" logs
grep "CHECKOUT_COMPLETED" logs  
grep "SUBSCRIPTION_ACTIVATED" logs
```

### Webhooks en Stripe Dashboard:

```
https://dashboard.stripe.com/webhooks
```

Verifica que los eventos lleguen (Status: succeeded)

---

## ⚡ Comandos Rápidos

### Re-crear productos en Stripe (si necesitas cambiar precios):

```powershell
python setup_stripe_products.py
```

### Verificar configuración actual:

```powershell
python -c "from app.core.config import get_settings; s=get_settings(); print(f'Starter: {bool(s.stripe_price_starter_id)}, Pro: {bool(s.stripe_price_pro_id)}, Business: {bool(s.stripe_price_business_id)}')"
```

### Test de checkout (requiere servidor corriendo):

```powershell
# Con curl (Windows):
curl -X POST BACKEND_URL/billing/checkout `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_JWT_TOKEN" `
  -d '{"plan":"pro","return_url":"NEXT_PUBLIC_SITE_URL/checkout?session_id={CHECKOUT_SESSION_ID}"}'
```

---

## 🎯 Checklist Final

- [x] ✅ Productos creados en Stripe
- [x] ✅ Price IDs en `.env`
- [ ] ⚠️ **Webhook configurado en Stripe Dashboard**
- [ ] ⚠️ **Webhook secret actualizado en `.env`**
- [ ] ⚠️ **Backend reiniciado**
- [ ] ⚠️ **Test de checkout completado**

---

## 🚨 Notas Importantes

### Modo Test vs Live

- **Test Mode**: Usa `sk_test_...` y price IDs de test
- **Live Mode**: Cambia a `sk_live_...` y crea productos nuevos en live mode

Los productos de test NO funcionan en live mode (y viceversa).

### OpenAI Status

⚠️ **OpenAI permanece DISABLED**  
No actives hasta tener suscriptores pagos:

```env
OPENAI_ENABLED=false  # ✅ Mantener así
```

### Soft Launch Mode

Tu configuración actual:

```env
SOFT_LAUNCH_MODE=true
DAILY_REGISTRATION_LIMIT=20
```

Esto limita registros a 20/día (perfecto para validación inicial).

---

## 📞 Soporte

Si algo no funciona:

1. Verifica logs del servidor
2. Revisa Stripe Dashboard → Webhooks → Recent deliveries
3. Verifica que el webhook secret coincida

**Tu Stripe está 95% listo** - Solo falta configurar el webhook endpoint 🎉
