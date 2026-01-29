# 🧪 TEST PAYMENT FLOW - Flujo Completo de Pago

Guía paso a paso para probar el flujo completo desde registro hasta análisis AI con créditos.

---

## 📋 Pre-requisitos

### Backend
```bash
# Verificar que el backend esté corriendo
BACKEND_URL/health
# O en producción:
https://linkedin-lead-checker-api.onrender.com/health
```

### Frontend Web
```bash
# Verificar que el frontend esté corriendo
NEXT_PUBLIC_SITE_URL
# O en producción:
https://linkedinleadchecker.com
```

### Extensión Chrome
- Extensión cargada en `chrome://extensions/`
- Extension ID copiado y actualizado en `web/lib/extension.js:8`

### Stripe (Modo Test)
- Cuenta Stripe en modo test
- Webhook configurado y funcionando
- Productos y precios creados

---

## 🔄 FLUJO COMPLETO DE PRUEBA

---

## 1️⃣ **Usuario Nuevo - Registro**

### **Acción:**
```
1. Ir a: NEXT_PUBLIC_SITE_URL
2. Click en "Sign Up" o "Get Started"
3. Completar formulario:
   - Email: test.user+001@gmail.com
   - Password: TestPass123!
   - Confirmar password
4. Click "Create Account"
```

### **✅ Verificación:**

#### Frontend:
- [ ] Formulario se envía sin errores
- [ ] Redirección automática a página de confirmación o dashboard
- [ ] Mensaje: "Account created successfully"

#### Backend (Logs):
```bash
# Revisar logs del backend
grep "New user registered" logs/app.log
```

#### Base de Datos:
```sql
-- Verificar usuario creado
SELECT id, email, plan, created_at 
FROM users 
WHERE email = 'test.user+001@gmail.com';

-- Resultado esperado:
-- id: 123
-- email: test.user+001@gmail.com
-- plan: free
-- created_at: 2026-01-27 ...
```

#### Inicial State:
- Plan: **free**
- Créditos: **3/3**
- Stripe Customer ID: **NULL**

---

## 2️⃣ **Login**

### **Acción:**
```
1. Si no estás logueado, ir a login page
2. Email: test.user+001@gmail.com
3. Password: TestPass123!
4. Click "Login"
```

### **✅ Verificación:**

#### Frontend:
- [ ] Redirección a dashboard
- [ ] Header muestra email del usuario
- [ ] Badge muestra "Free Plan"
- [ ] Contador muestra "3/3 analyses this month"

#### Browser DevTools (Application > Storage):
```javascript
// LocalStorage
localStorage.getItem('access_token')  // JWT token presente
localStorage.getItem('user_email')    // test.user+001@gmail.com

// Cookies
document.cookie  // Verificar si hay cookie de sesión
```

#### Network Tab:
```
POST /auth/login
Response: 200 OK
Body: {
  "access_token": "eyJ...",
  "user": {
    "email": "test.user+001@gmail.com",
    "plan": "free"
  }
}
```

---

## 3️⃣ **Click Pricing**

### **Acción:**
```
1. Desde dashboard, click en "Upgrade" o "Pricing"
2. O navegar a: NEXT_PUBLIC_SITE_URL/pricing
```

### **✅ Verificación:**

#### Página de Pricing:
- [ ] 3 planes visibles: Free, Pro, Enterprise
- [ ] Botones de CTA correctos:
  - Free: "Current Plan" (deshabilitado)
  - Pro: "Upgrade to Pro"
  - Enterprise: "Upgrade to Enterprise"
- [ ] Precios mostrados correctamente:
  - Pro: $29/month
  - Enterprise: $99/month

#### Comparación de Features:
```
Free:
✓ 3 AI analyses/month
✓ Basic profile insights
✗ Priority support
✗ Custom ICP

Pro:
✓ 50 AI analyses/month
✓ Full AI insights
✓ Priority support
✗ Custom ICP

Enterprise:
✓ 500 AI analyses/month
✓ Full AI insights
✓ Priority support
✓ Custom ICP
```

---

## 4️⃣ **Checkout Stripe**

### **Acción:**
```
1. Click en "Upgrade to Pro"
2. Redirección a Stripe Checkout
```

### **✅ Verificación:**

#### Redirección:
```
URL: https://checkout.stripe.com/c/pay/cs_test_...
```

#### Stripe Checkout Page:
- [ ] Email pre-rellenado: test.user+001@gmail.com
- [ ] Producto: "Pro Plan"
- [ ] Precio: $29.00 USD / month
- [ ] Método de pago: Card input visible

#### Backend (Logs):
```bash
# Log de creación de checkout session
grep "Stripe checkout session created" logs/app.log

# Output esperado:
# Stripe checkout session created: cs_test_abc123 (user_id=123, plan=pro)
```

#### Base de Datos (Pre-Pago):
```sql
-- Usuario aún en plan free
SELECT plan, stripe_customer_id, stripe_subscription_id 
FROM users 
WHERE email = 'test.user+001@gmail.com';

-- Resultado esperado:
-- plan: free
-- stripe_customer_id: NULL (o cus_... si ya existe)
-- stripe_subscription_id: NULL
```

---

## 5️⃣ **Pago Completado**

### **Acción:**
```
1. En Stripe Checkout, ingresar tarjeta de prueba:
   - Número: 4242 4242 4242 4242
   - Fecha: 12/34 (cualquier fecha futura)
   - CVC: 123
   - ZIP: 12345

2. Click "Subscribe" o "Pay"
```

### **✅ Verificación:**

#### Stripe Checkout:
- [ ] Procesando pago (spinner)
- [ ] Success message: "Payment successful"
- [ ] Redirección automática iniciada

#### Webhook Recibido (Backend Logs):
```bash
# Webhook de Stripe
grep "Stripe webhook received" logs/app.log

# Output esperado:
# Stripe webhook received: checkout.session.completed (session_id=cs_test_abc123)
# User plan upgraded: user_id=123, plan=pro
# Stripe customer created: cus_xyz789
# Stripe subscription created: sub_abc456
```

#### Base de Datos (Post-Webhook):
```sql
-- Verificar upgrade
SELECT 
  plan, 
  stripe_customer_id, 
  stripe_subscription_id, 
  subscription_status,
  subscription_current_period_end
FROM users 
WHERE email = 'test.user+001@gmail.com';

-- Resultado esperado:
-- plan: pro
-- stripe_customer_id: cus_xyz789
-- stripe_subscription_id: sub_abc456
-- subscription_status: active
-- subscription_current_period_end: 2026-02-27 (1 mes después)
```

#### Stripe Dashboard:
```
1. Ir a: https://dashboard.stripe.com/test/customers
2. Buscar: test.user+001@gmail.com
3. Verificar:
   - Customer creado
   - Subscription activa: "Pro Plan"
   - Próximo pago: 2026-02-27
   - Estado: Active
```

---

## 6️⃣ **Redirección Success**

### **Acción:**
```
Automático después del pago
```

### **✅ Verificación:**

#### URL de Success:
```
NEXT_PUBLIC_SITE_URL/payment-success?session_id=cs_test_abc123
# O producción:
https://linkedinleadchecker.com/payment-success?session_id=cs_test_abc123
```

#### Página de Success:
- [ ] Título: "🎉 Payment Successful!"
- [ ] Mensaje: "Welcome to Pro Plan"
- [ ] Créditos mostrados: "50 AI analyses/month"
- [ ] Badge: "Pro Plan" visible
- [ ] Botón: "Go to Dashboard" o "Start Analyzing"

#### Network Request (Billing Status):
```javascript
GET /billing/status
Response: {
  "plan": "pro",
  "usage_current": 0,
  "usage_limit": 50,
  "can_analyze": true,
  "subscription_status": "active",
  "subscription_current_period_end": "2026-02-27T..."
}
```

#### LocalStorage Updated:
```javascript
localStorage.getItem('billing_status')  // JSON con plan: pro
localStorage.getItem('cached_plan')     // "pro"
```

---

## 7️⃣ **Back to Extension**

### **Acción:**
```
1. Ir a LinkedIn: https://www.linkedin.com/in/cualquier-perfil/
2. Click en el icono de la extensión (arriba a la derecha)
3. Popup se abre
```

### **✅ Verificación:**

#### Extension Popup UI:
- [ ] Badge muestra: "✓ Pro Plan"
- [ ] Contador: "50/50 analyses remaining"
- [ ] Botón "Analyze LinkedIn Profile" **habilitado** (azul)
- [ ] Email mostrado: test.user+001@gmail.com

#### Extension Console (F12 en popup):
```javascript
// Verificar billing status
chrome.storage.local.get(['billing_status'], (result) => {
  console.log(result.billing_status);
});

// Output esperado:
{
  plan: "pro",
  usage_current: 0,
  usage_limit: 50,
  can_analyze: true
}
```

#### Network Request (desde Extension):
```
GET https://linkedin-lead-checker-api.onrender.com/billing/status
Authorization: Bearer eyJ...
Response: 200 OK
Body: { plan: "pro", usage_current: 0, usage_limit: 50, can_analyze: true }
```

---

## 8️⃣ **Análisis AI Exitoso**

### **Acción:**
```
1. En LinkedIn, estar en cualquier perfil: linkedin.com/in/username/
2. Abrir extension popup
3. Click en "Analyze LinkedIn Profile"
```

### **✅ Verificación:**

#### Extension UI (Durante Análisis):
```
Estado 1: "Getting active tab..." (info)
Estado 2: "Checking credits..." (info)
Estado 3: "Extracting profile data..." (info)
Estado 4: "Analyzing profile with AI..." (info)
```

#### Network Tab (Extension):
```
1. GET /billing/status
   Response: 200 OK { can_analyze: true, usage_current: 0 }

2. POST /analyze/linkedin
   Request Body: {
     "profile_extract": {
       "name": "John Doe",
       "headline": "Senior Product Manager at Tech Corp",
       "about": "Experienced PM with...",
       "experience_titles": ["Senior PM", "Product Lead", ...]
     },
     "profile_url": "https://linkedin.com/in/johndoe/"
   }
   
   Response: 200 OK {
     "qualification": { ... },
     "ui": {
       "should_contact": true,
       "priority": "high",
       "score": 85,
       "reasoning": "Strong fit based on...",
       "key_points": ["5+ years in target industry", ...],
       "suggested_approach": "Reference recent post about...",
       "red_flags": [],
       "next_steps": "Schedule intro call"
     },
     "plan": "pro",
     "preview": false,
     "message": "AI-powered profile analysis...",
     "cache_hit": false
   }
```

#### Extension UI (Resultados):
- [ ] Spinner desaparece
- [ ] Resultados mostrados:
  - Badge: "🔥 Recommended Contact (high priority)"
  - Estrellas: ⭐⭐⭐⭐⭐ (basado en score)
  - Key insights listados (3-5 bullets)
  - Suggested approach visible
  - Red flags (si hay)
- [ ] Botón "Analyze" ocultado
- [ ] Botón "← Back" visible

#### Backend Logs:
```bash
# Verificar análisis exitoso
grep "AI_CALL_APPROVED" logs/app.log
grep "LinkedIn analysis successful" logs/app.log

# Output esperado:
# AI_CALL_APPROVED: Starting LinkedIn analysis (user_id=123, plan=pro, remaining=50)
# LinkedIn analysis successful for user_id=123, decision=True
```

---

## 9️⃣ **Crédito Decrementado**

### **✅ Verificación:**

#### Extension UI (Actualizada):
```
1. Después de ver resultados, click "← Back"
2. Verificar contador: "49/50 analyses remaining" (decrementó 1)
```

#### Network Request (Auto-refresh):
```
GET /billing/status
Response: {
  "plan": "pro",
  "usage_current": 1,    // ← Incrementó de 0 a 1
  "usage_limit": 50,
  "can_analyze": true,
  "remaining": 49
}
```

#### Base de Datos:
```sql
-- 1. Verificar registro en usage_logs
SELECT * FROM usage_logs 
WHERE user_id = 123 
ORDER BY timestamp DESC 
LIMIT 1;

-- Resultado esperado:
-- id: 456
-- user_id: 123
-- action: analyze_profile
-- timestamp: 2026-01-27 14:30:00
-- cost_usd: 0.05
-- metadata: {"profile_url": "https://linkedin.com/in/johndoe/"}

-- 2. Verificar total de análisis del mes
SELECT COUNT(*) as total_analyses
FROM usage_logs
WHERE user_id = 123
  AND action = 'analyze_profile'
  AND timestamp >= DATE_TRUNC('month', CURRENT_DATE);

-- Resultado esperado:
-- total_analyses: 1
```

#### Stripe Dashboard (Opcional):
```
1. Ir a: https://dashboard.stripe.com/test/subscriptions
2. Buscar subscription: sub_abc456
3. Verificar:
   - Status: Active
   - Plan: Pro Plan ($29/month)
   - Current period: 2026-01-27 - 2026-02-27
   - Next invoice: 2026-02-27
```

---

## 🔁 **Pruebas Adicionales**

### **Análisis Múltiples (Usar Créditos)**

#### Test: Usar 5 créditos
```
1. Hacer 5 análisis consecutivos
2. Verificar después de cada uno:
   - 50 → 49 → 48 → 47 → 46 → 45
3. Verificar logs: 5 registros en usage_logs
```

```sql
SELECT COUNT(*) FROM usage_logs WHERE user_id = 123;
-- Expected: 5
```

### **Alcanzar Límite (Plan Free)**

#### Test: Usuario Free alcanza límite
```
1. Crear usuario free nuevo
2. Hacer 3 análisis (usar todos los créditos)
3. Intentar 4to análisis
4. ✅ Verificar: Modal de upgrade aparece
5. ✅ Verificar: Backend responde 429 Too Many Requests
```

#### Backend Response (4to análisis):
```json
POST /analyze/linkedin
Response: 429 Too Many Requests
{
  "detail": "You've reached your monthly limit (3 analyses/month). Your limit will reset on the 1st of next month."
}
```

### **Cache Hit (Mismo Perfil)**

#### Test: Re-analizar mismo perfil
```
1. Analizar perfil A → Éxito (crédito usado)
2. Inmediatamente analizar perfil A de nuevo
3. ✅ Verificar: Resultados instantáneos (cache hit)
4. ✅ Verificar: NO se usa crédito adicional (cache_hit=true)
```

#### Backend Response (2da vez):
```json
{
  "qualification": { ... },
  "ui": { ... },
  "cache_hit": true,  // ← Cache hit
  "preview": false
}
```

---

## 🐛 **Troubleshooting**

### Problema: Webhook no recibido
```bash
# Verificar webhook configurado
stripe listen --forward-to BACKEND_URL/webhooks/stripe

# Verificar logs
grep "Stripe webhook" logs/app.log
```

### Problema: Plan no actualizado después de pago
```sql
-- Verificar estado de suscripción
SELECT 
  email, 
  plan, 
  stripe_subscription_id, 
  subscription_status 
FROM users 
WHERE email = 'test.user+001@gmail.com';

-- Si plan sigue en 'free' pero subscription_id presente:
-- 1. Verificar webhook recibido
-- 2. Revisar logs de error
-- 3. Manualmente actualizar:
UPDATE users 
SET plan = 'pro', subscription_status = 'active' 
WHERE email = 'test.user+001@gmail.com';
```

### Problema: Créditos no decrementan
```bash
# Verificar llamada a record_usage
grep "record_usage" logs/app.log

# Verificar tabla usage_logs
SELECT * FROM usage_logs WHERE user_id = 123;
```

### Problema: Modal de límite aparece incorrectamente
```javascript
// En extension popup, verificar:
chrome.storage.local.get(['billing_status'], (result) => {
  console.log('Can analyze:', result.billing_status.can_analyze);
  console.log('Usage:', result.billing_status.usage_current, '/', result.billing_status.usage_limit);
});

// Si can_analyze=false pero tiene créditos:
// 1. Logout/login
// 2. Verificar /billing/status responde correctamente
```

---

## 📊 **Checklist de Validación Final**

### Usuario & Autenticación
- [ ] Usuario creado en DB
- [ ] Login exitoso con JWT token
- [ ] Token almacenado en localStorage
- [ ] Session persiste después de cerrar/abrir browser

### Pago & Suscripción
- [ ] Checkout session creada en Stripe
- [ ] Pago procesado correctamente
- [ ] Webhook recibido y procesado
- [ ] Plan actualizado en DB (free → pro)
- [ ] Stripe customer_id y subscription_id guardados
- [ ] Subscription status = "active"

### Extensión & UI
- [ ] Extension cargada sin errores
- [ ] Popup muestra plan correcto (Pro)
- [ ] Contador de créditos correcto (50/50 inicial)
- [ ] Botón "Analyze" habilitado

### Análisis AI
- [ ] Perfil extraído correctamente del DOM
- [ ] Request enviada a /analyze/linkedin
- [ ] Response 200 OK con resultados reales
- [ ] preview=false (no es preview mode)
- [ ] Resultados mostrados en UI

### Créditos & Tracking
- [ ] Crédito decrementado (50 → 49)
- [ ] Registro creado en usage_logs
- [ ] can_analyze permanece true (aún hay créditos)
- [ ] UI actualizada automáticamente
- [ ] Cache funciona (re-analizar mismo perfil no usa crédito)

---

## ✅ **Éxito Total**

Si todos los pasos pasan:
- ✅ Flujo de pago funciona end-to-end
- ✅ Suscripción activa en Stripe
- ✅ Plan actualizado en DB y UI
- ✅ Análisis AI funciona con créditos reales
- ✅ Sistema de créditos funciona correctamente
- ✅ Tracking de uso funciona

**¡Sistema listo para producción!** 🎉🚀

---

## 📝 Notas Finales

### Tarjetas de Prueba Stripe
```
Éxito: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
Insufficient funds: 4000 0000 0000 9995
```

### Reset Test Data
```sql
-- Limpiar usuario de prueba
DELETE FROM usage_logs WHERE user_id = 123;
DELETE FROM users WHERE email LIKE 'test.user%';
```

### Monitoreo Continuo
```bash
# Logs en tiempo real
tail -f logs/app.log | grep -E "AI_CALL|Stripe|usage"
```
