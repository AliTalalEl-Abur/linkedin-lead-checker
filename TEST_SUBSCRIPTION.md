# 🧪 Test de Flujo de Suscripción

## 📋 Objetivo

Verificar que el flujo completo de suscripción funciona correctamente:
1. Usuario compra plan Starter
2. Stripe procesa el pago
3. Webhook actualiza la base de datos
4. Plan y límites se reflejan correctamente

---

## 🎯 Pre-requisitos

### Backend Running:
```powershell
# Terminal 1: Backend
python run.py
```

### Webhooks Configurados:
```bash
# Terminal 2: Stripe CLI (para testing local)
stripe listen --forward-to BACKEND_URL/billing/webhook/stripe
```

**O** configurar webhook en Stripe Dashboard para producción:
- URL: `https://tu-dominio.com/billing/webhook/stripe`
- Events: 
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`

### Verificación Inicial:
```powershell
# Verificar configuración de Stripe
python verify_stripe_sync.py
```

**Debe mostrar:**
```
✅ VERIFICATION PASSED - All checks successful!
```

---

## 📝 Procedimiento de Testing Manual

### Paso 1: Preparar Email de Prueba

**Email a usar:** `tu-email+starter-test@gmail.com`

**Por qué usar +suffix:**
- Gmail ignora todo después del `+`
- Los emails llegan a tu inbox normal
- Stripe lo trata como email diferente
- Puedes hacer múltiples tests: `+test1`, `+test2`, etc.

### Paso 2: Crear Usuario en el Backend (si no existe)

```powershell
# Opción A: Registrarse normalmente en la extensión
# 1. Instalar extensión en Chrome
# 2. Hacer sign up con tu-email+starter-test@gmail.com

# Opción B: Crear usuario directamente en base de datos
python -c "
from app.database import SessionLocal
from app.models.user import User
import bcrypt

db = SessionLocal()

# Verificar si existe
existing = db.query(User).filter(User.email == 'tu-email+starter-test@gmail.com').first()
if existing:
    print(f'Usuario ya existe: {existing.id}')
else:
    # Crear nuevo usuario
    user = User(
        email='tu-email+starter-test@gmail.com',
        password_hash=bcrypt.hashpw('password123'.encode(), bcrypt.gensalt()).decode(),
        plan='free',
        analyses_limit=10,
        analyses_used=0
    )
    db.add(user)
    db.commit()
    print(f'Usuario creado: {user.id}')

db.close()
"
```

### Paso 3: Verificar Estado Inicial del Usuario

```powershell
python test_subscription_flow.py tu-email+starter-test@gmail.com
```

**Output esperado:**
```
🗄️  Checking Database for user: tu-email+starter-test@gmail.com
======================================================================
✅ User found:
   • ID: 1
   • Email: tu-email+starter-test@gmail.com
   • Plan: free
   • Stripe Customer ID: None
   • Stripe Subscription ID: None
   • Analyses Used: 0/10
   • Subscription Status: None

🔍 Checking Stripe for customer: tu-email+starter-test@gmail.com
======================================================================
❌ No customer found with email: tu-email+starter-test@gmail.com
```

### Paso 4: Iniciar Checkout Session

**Opción A: Desde la extensión**
1. Abrir LinkedIn Lead Checker
2. Click en "Upgrade Plan" o "View Plans"
3. Seleccionar "Starter - $9/month"
4. Click "Subscribe"

**Opción B: URL directa**
```
BACKEND_URL/billing/checkout?plan=starter
```

**Opción C: Desde landing page**
```
BACKEND_URL/index.html#pricing
```

### Paso 5: Completar el Pago en Stripe

1. **Se abre Stripe Checkout**
   - Email: `tu-email+starter-test@gmail.com` (auto-completado)
   - Detalles del plan: LinkedIn Lead Checker – Starter
   - Precio: $9.00/mes

2. **Usar tarjeta de prueba:**
   - Número: `4242 4242 4242 4242`
   - Expiración: Cualquier fecha futura (ej: 12/30)
   - CVC: Cualquier 3 dígitos (ej: 123)
   - Nombre: Tu nombre
   - Código postal: Cualquiera (ej: 12345)

3. **Click "Subscribe"**
   - Stripe procesa el pago (modo test)
   - Redirige a success URL

4. **Deberías ver página de éxito:**
   ```
   ✅ Subscription Successful!
   
   Welcome to LinkedIn Lead Checker Starter
   
   Your subscription is now active
   40 analyses per month
   ```

### Paso 6: Verificar Webhook Recibido

**En logs del backend (Terminal 1), deberías ver:**
```
INFO: Received webhook: checkout.session.completed
INFO: Processing checkout session: cs_test_...
INFO: Customer created/found: cus_...
INFO: Subscription created: sub_...
INFO: User updated: plan=starter, limit=40
```

**En Stripe CLI (Terminal 2), deberías ver:**
```
-> checkout.session.completed [evt_...]
<- [200] POST BACKEND_URL/billing/webhook/stripe [evt_...]
```

### Paso 7: Verificar Suscripción

**Ejecutar script de verificación:**
```powershell
python test_subscription_flow.py tu-email+starter-test@gmail.com
```

**Output esperado (TODO CORRECTO):**
```
🧪 SUBSCRIPTION FLOW VERIFICATION
======================================================================

🔍 Checking Stripe for customer: tu-email+starter-test@gmail.com
======================================================================
✅ Customer found:
   • ID: cus_ABC123XYZ
   • Email: tu-email+starter-test@gmail.com
   • Created: 2026-01-26 10:30:45

📋 Subscriptions (1):

   Subscription 1:
   • ID: sub_XYZ789ABC
   • Status: active
   • Current Period: 2026-01-26 to 2026-02-26
   • Price ID: price_1StrzhPc1lhDefcvp0TJY0rS
   • Amount: $9.00/month
   • Plan: ⭐ Starter

🗄️  Checking Database for user: tu-email+starter-test@gmail.com
======================================================================
✅ User found:
   • ID: 1
   • Email: tu-email+starter-test@gmail.com
   • Plan: starter
   • Stripe Customer ID: cus_ABC123XYZ
   • Stripe Subscription ID: sub_XYZ789ABC
   • Analyses Used: 0/40
   • Subscription Status: active
   • Subscription End: 2026-02-26

======================================================================
📊 VERIFICATION RESULTS
======================================================================
✅ Stripe: 1 active subscription(s)
✅ Database: User exists
✅ Database: Has stripe_customer_id
✅ Database: Has stripe_subscription_id
✅ Database: User on 'starter' plan
✅ Database: Correct analyses limit (40)
✅ Sync: Customer ID matches
✅ Sync: Subscription ID matches

======================================================================
🎉 ALL CHECKS PASSED!
   Subscription flow is working correctly
======================================================================
```

### Paso 8: Verificar en Stripe Dashboard

1. **Ir a:** https://dashboard.stripe.com/test/customers
2. **Buscar:** `tu-email+starter-test@gmail.com`
3. **Verificar:**
   - ✅ Customer existe
   - ✅ Subscription activa
   - ✅ Precio: $9.00/month
   - ✅ Plan: LinkedIn Lead Checker – Starter
   - ✅ Estado: Active

4. **Ir a:** https://dashboard.stripe.com/test/subscriptions
5. **Verificar subscription:**
   - ✅ Customer: tu-email+starter-test@gmail.com
   - ✅ Status: Active
   - ✅ Billing period: Monthly
   - ✅ Next invoice: ~1 mes después

### Paso 9: Verificar en la Extensión

1. **Abrir extensión Chrome**
2. **Login con:** `tu-email+starter-test@gmail.com`
3. **Verificar:**
   - ✅ Plan mostrado: "Starter"
   - ✅ Límite: 40 analyses
   - ✅ Badge o indicador de plan activo
   - ✅ Botón "Manage Subscription" visible

4. **Realizar un análisis:**
   - Abrir perfil de LinkedIn
   - Click "Analyze Profile"
   - ✅ Análisis se ejecuta correctamente
   - ✅ Contador de uso: 1/40

### Paso 10: Verificar Límites Actualizados

```powershell
# Verificar en base de datos
python -c "
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'tu-email+starter-test@gmail.com').first()

print(f'Plan: {user.plan}')
print(f'Limit: {user.analyses_limit}')
print(f'Used: {user.analyses_used}')
print(f'Remaining: {user.analyses_limit - user.analyses_used}')

db.close()
"
```

**Output esperado:**
```
Plan: starter
Limit: 40
Used: 1
Remaining: 39
```

---

## ✅ Checklist de Verificación

### Backend:
- [ ] Backend corriendo en BACKEND_URL
- [ ] Webhook endpoint configurado
- [ ] Stripe CLI escuchando (local) O webhook en Dashboard (producción)
- [ ] Variables de entorno configuradas (.env)

### Usuario:
- [ ] Usuario creado/registrado
- [ ] Estado inicial: plan='free', limit=10
- [ ] Email de prueba usa formato +suffix

### Checkout:
- [ ] URL de checkout accesible
- [ ] Stripe Checkout se abre correctamente
- [ ] Email auto-completado
- [ ] Plan correcto mostrado (Starter - $9/month)
- [ ] Tarjeta de prueba aceptada

### Webhook:
- [ ] Webhook `checkout.session.completed` recibido
- [ ] Logs muestran procesamiento exitoso
- [ ] Sin errores en logs
- [ ] HTTP 200 response

### Stripe:
- [ ] Customer creado en Stripe
- [ ] Subscription activa
- [ ] Price ID correcto (starter)
- [ ] Monto correcto ($9.00/month)

### Base de Datos:
- [ ] User.plan = 'starter'
- [ ] User.stripe_customer_id != None
- [ ] User.stripe_subscription_id != None
- [ ] User.analyses_limit = 40
- [ ] User.subscription_status = 'active'
- [ ] User.subscription_end_date configurada

### Sincronización:
- [ ] Customer ID coincide (Stripe ↔ DB)
- [ ] Subscription ID coincide (Stripe ↔ DB)
- [ ] Plan coincide
- [ ] Límites actualizados

### Funcionalidad:
- [ ] Usuario puede hacer login
- [ ] Plan se muestra en extensión
- [ ] Puede realizar análisis
- [ ] Contador se incrementa
- [ ] Límites se respetan

---

## 🚨 Troubleshooting

### Problema: Webhook no recibido

**Síntomas:**
- Pago exitoso en Stripe
- Usuario sigue en plan 'free'
- No hay logs de webhook

**Diagnóstico:**
```powershell
# 1. Verificar webhook está escuchando
# En Stripe CLI debe mostrar:
stripe listen --forward-to BACKEND_URL/billing/webhook/stripe
# Output: Ready! Your webhook signing secret is whsec_...

# 2. Verificar endpoint responde
curl -X POST BACKEND_URL/billing/webhook/stripe
# Debe retornar HTTP 400 (signature inválida es OK)

# 3. Ver eventos recientes en Stripe
stripe events list --limit 5
```

**Soluciones:**
1. **Reiniciar Stripe CLI:**
   ```powershell
   # Ctrl+C para detener
   stripe listen --forward-to BACKEND_URL/billing/webhook/stripe
   ```

2. **Reenviar webhook manualmente:**
   - Ir a: https://dashboard.stripe.com/test/webhooks
   - Click en el endpoint
   - Tab "Webhook attempts"
   - Click "..." en el evento
   - Click "Resend"

3. **Verificar secret:**
   ```bash
   # En .env debe haber:
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Problema: Usuario no actualizado en DB

**Síntomas:**
- Webhook recibido (logs lo confirman)
- Usuario sigue en plan 'free'

**Diagnóstico:**
```powershell
# Ver logs completos del webhook
# Buscar errores tipo:
# - "User not found"
# - "Database error"
# - "Invalid price_id"
```

**Soluciones:**
1. **Verificar user_id en logs:**
   - Webhook debe encontrar usuario por email
   - Si no existe, verificar que email coincide exactamente

2. **Verificar price_id válido:**
   ```powershell
   python test_stripe_security.py
   # Debe pasar - confirma price_id en whitelist
   ```

3. **Actualizar manualmente (como workaround):**
   ```powershell
   python -c "
   from app.database import SessionLocal
   from app.models.user import User
   
   db = SessionLocal()
   user = db.query(User).filter(User.email == 'tu-email@gmail.com').first()
   
   user.plan = 'starter'
   user.analyses_limit = 40
   user.stripe_customer_id = 'cus_...'  # Copiar de Stripe
   user.stripe_subscription_id = 'sub_...'  # Copiar de Stripe
   user.subscription_status = 'active'
   
   db.commit()
   db.close()
   print('✅ User updated manually')
   "
   ```

### Problema: Error "Invalid price_id"

**Síntomas:**
- Webhook falla con error de validación
- Logs muestran "SECURITY_VIOLATION"

**Causa:** Price_id no está en whitelist del backend

**Solución:**
```powershell
# 1. Verificar price_ids
python verify_stripe_sync.py

# 2. Actualizar .env con price_ids correctos
# Copiar desde STRIPE_IDS.md

# 3. Reiniciar backend
# Ctrl+C y volver a ejecutar: python run.py
```

### Problema: Checkout redirige pero no crea subscription

**Síntomas:**
- Checkout exitoso
- Success page se muestra
- Pero no hay subscription en Stripe

**Causa:** Modo de pago incorrecto o configuración de producto

**Solución:**
1. **Verificar producto tiene precio recurrente:**
   ```powershell
   python verify_stripe_sync.py
   # Debe confirmar: "recurring: month"
   ```

2. **Verificar modo en checkout:**
   - En `app/api/routes/billing.py`
   - `mode='subscription'` (NO 'payment')

---

## 📊 Tests Adicionales

### Test 2: Upgrade de Plan

```powershell
# 1. Usuario ya tiene plan Starter
# 2. Comprar plan Pro
curl "BACKEND_URL/billing/checkout?plan=pro"

# 3. Verificar upgrade
python test_subscription_flow.py tu-email+starter-test@gmail.com

# Debe mostrar:
# • Plan: pro
# • Limit: 150
```

### Test 3: Cancelación de Subscription

```powershell
# 1. Ir a Stripe Dashboard
# 2. Subscriptions > Buscar usuario
# 3. Click "Cancel subscription"
# 4. Confirm cancellation

# 5. Webhook se recibe automáticamente
# 6. Verificar usuario
python test_subscription_flow.py tu-email+starter-test@gmail.com

# Debe mostrar:
# • Subscription Status: canceled
# • Plan: revierte a 'free' (dependiendo de lógica)
```

### Test 4: Multiple Checkouts

```powershell
# Usar diferentes sufijos:
# tu-email+test1@gmail.com
# tu-email+test2@gmail.com
# tu-email+test3@gmail.com

# Verificar cada uno:
python test_subscription_flow.py tu-email+test1@gmail.com
python test_subscription_flow.py tu-email+test2@gmail.com
python test_subscription_flow.py tu-email+test3@gmail.com
```

---

## 🎯 Criterios de Éxito

### ✅ Test Pasa Si:

1. **Checkout:**
   - URL funciona
   - Stripe Checkout se abre
   - Pago se procesa

2. **Webhook:**
   - Evento recibido en <5 segundos
   - HTTP 200 response
   - Logs sin errores

3. **Database:**
   - User.plan = 'starter'
   - User.analyses_limit = 40
   - User.stripe_customer_id y stripe_subscription_id set
   - User.subscription_status = 'active'

4. **Stripe:**
   - Customer creado
   - Subscription activa
   - Price ID correcto

5. **Verificación:**
   - `python test_subscription_flow.py email` muestra "ALL CHECKS PASSED"

6. **Funcionalidad:**
   - Usuario puede analizar perfiles
   - Límites se respetan
   - Plan se muestra correctamente

### ❌ Test Falla Si:

- Checkout no se abre
- Webhook no llega
- Usuario no se actualiza
- Límites incorrectos
- Customer no en Stripe
- Subscription no activa
- Script de verificación muestra errores

---

## 📈 Métricas a Monitorear

### Durante el Test:
- Tiempo desde checkout hasta webhook: **< 5 segundos**
- Tiempo de actualización DB: **< 1 segundo**
- Success rate de webhooks: **100%**

### En Producción:
- Checkout abandonment rate
- Subscription creation success rate
- Webhook failure rate
- Average time to activation

---

## 🔗 Scripts Relacionados

| Script | Uso |
|--------|-----|
| `test_subscription_flow.py` | Verificar estado de suscripción |
| `verify_stripe_sync.py` | Verificar configuración general |
| `test_stripe_security.py` | Verificar whitelist de price_ids |

---

## 📝 Documentar Resultados

Después de completar el test, documentar:

```markdown
## Test Results - [Fecha]

**Email usado:** tu-email+test@gmail.com
**Plan:** Starter
**Resultado:** ✅ PASS / ❌ FAIL

### Checkout:
- Time: XX segundos
- Issues: Ninguno

### Webhook:
- Received: ✅ Yes
- Latency: X segundos
- Issues: Ninguno

### Database:
- Plan updated: ✅ Yes
- Limits correct: ✅ Yes
- Issues: Ninguno

### Verification:
- All checks: ✅ PASSED
- Errors: 0
- Warnings: 0

### Notas:
- [Cualquier observación]
```

---

**Última Actualización:** 2026-01-26
**Versión:** 1.0.0
**Responsable:** Equipo de Testing
