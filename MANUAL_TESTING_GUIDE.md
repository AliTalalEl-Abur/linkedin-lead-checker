# 🧪 Guía de Testing Manual - Botones de Pricing

## ✅ Estado Actual

- ✅ Backend configurado y funcionando
- ✅ Frontend actualizado con handleCheckout()
- ✅ Price IDs configurados en .env
- ✅ Autenticación JWT implementada

---

## 🚀 Cómo Probar

### 1. Iniciar Backend

```bash
# Terminal 1
python run.py
```

Deberías ver:
```
✓ Required environment variables validated
Stripe: ENABLED (billing available)
  - starter_price_id: configured
  - pro_price_id: configured
  - team_price_id: configured
Backend ready to receive traffic
```

### 2. Iniciar Frontend

```bash
# Terminal 2
cd web
npm run dev
```

### 3. Probar el Flujo

#### Paso A: Navegar a la Landing Page
```
http://localhost:3000
```

#### Paso B: Hacer Scroll hasta la Sección de Pricing
Verás 3 planes:
- **Starter** - $9/mes - "Get Started"
- **Pro** - $19/mes - "Get Started" 
- **Team** - $49/mes - "Get Started"

#### Paso C: Click en Cualquier Botón (Sin Login)
- **Resultado esperado:** Redirige a `/login`
- ✅ Esto confirma que la validación de autenticación funciona

#### Paso D: Hacer Login
1. Ir a `http://localhost:3000/login`
2. Ingresar email (cualquier email válido)
3. Click en "Continue"
4. **Resultado esperado:** Redirige a `/dashboard`

#### Paso E: Regresar a Landing y Hacer Click en un Plan
1. Ir a `http://localhost:3000`
2. Scroll hasta pricing
3. Click en "Subscribe Now" de cualquier plan
4. **Resultado esperado:**
   - ✅ Abre una nueva ventana/tab
   - ✅ URL es de Stripe Checkout: `checkout.stripe.com/pay/cs_test_...`
   - ✅ Muestra el plan correcto y precio correcto
   - ✅ Formulario de tarjeta de Stripe visible

#### Paso F: Completar el Pago (Modo Test)
**Tarjeta de prueba:**
```
Número: 4242 4242 4242 4242
Fecha: Cualquier fecha futura (ej: 12/25)
CVC: Cualquier 3 dígitos (ej: 123)
ZIP: Cualquier código (ej: 12345)
```

Click en "Subscribe"

**Resultado esperado:**
- ✅ Redirige a `/billing-return.html?session_id=...&status=success`
- ✅ Muestra mensaje de éxito

---

## 🔍 Verificaciones en Consola del Navegador

### Abrir DevTools (F12)

#### 1. Verificar Token JWT
```javascript
// En Console:
localStorage.getItem('authToken')
```

Deberías ver un string largo como:
```
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 2. Verificar Llamada al API
Cuando haces click en un botón de pricing:

**Network Tab:**
1. Buscar request a `billing/checkout`
2. **Request Headers:**
   - ✅ `Authorization: Bearer eyJ...`
3. **Request Payload:**
   ```json
   {
     "return_url": "http://localhost:3000/billing-return.html?session_id={CHECKOUT_SESSION_ID}",
     "plan": "pro"  // o "starter" o "team"
   }
   ```
4. **Response:**
   ```json
   {
     "sessionId": "cs_test_...",
     "url": "https://checkout.stripe.com/pay/cs_test_..."
   }
   ```

---

## 🐛 Troubleshooting

### Error: "Not authenticated"
**Causa:** No hay token JWT en localStorage
**Solución:**
1. Ir a `/login`
2. Ingresar email
3. Intentar nuevamente

### Error: No redirige a Stripe
**Causa posible:** Error en el backend
**Debug:**
1. Abrir DevTools → Network tab
2. Ver la respuesta del request a `/billing/checkout`
3. Si hay error 500, revisar logs del backend

### Error 403 en /billing/checkout
**Causa:** JWT token no válido
**Solución:**
1. Hacer logout (borrar localStorage)
2. Login nuevamente
3. Intentar de nuevo

### Stripe muestra precio incorrecto
**Causa:** Price ID incorrecto en .env
**Solución:**
```bash
# Verificar price IDs
python verify_stripe_products.py
```

---

## ✅ Checklist de Testing

### Funcionalidad Básica
- [ ] Botones visibles en pricing section
- [ ] Click sin login → Redirige a `/login`
- [ ] Click con login → Abre Stripe Checkout
- [ ] Cada plan abre Stripe con precio correcto

### Validación de Planes
- [ ] Starter ($9/mes) → Precio correcto en Stripe
- [ ] Pro ($19/mes) → Precio correcto en Stripe
- [ ] Team ($49/mes) → Precio correcto en Stripe

### Seguridad
- [ ] Sin JWT → Request a `/billing/checkout` falla (401/403)
- [ ] Con JWT → Request a `/billing/checkout` funciona (200)
- [ ] Cada plan usa su price_id correcto

### Flujo Completo
- [ ] Login funciona
- [ ] Checkout se crea correctamente
- [ ] Redirige a Stripe
- [ ] Pago de prueba funciona
- [ ] Webhook actualiza plan del usuario (verificar en logs backend)

---

## 📊 Testing con Stripe CLI (Opcional)

Si quieres probar webhooks localmente:

```bash
# Terminal 3
stripe login
stripe listen --forward-to http://127.0.0.1:8000/billing/webhook/stripe
```

Esto mostrará eventos en tiempo real cuando completes un pago.

---

## 🎉 Si Todo Funciona

Verás este flujo:
```
Landing → Click Plan → Login (si necesario) → 
Stripe Checkout → Pago → Success Page → 
Backend recibe webhook → User.plan actualizado
```

**¡La integración está completa!** 🚀

---

## 📝 Próximos Pasos

1. ✅ Testing manual completado
2. Testing con Stripe CLI para webhooks
3. Deploy a staging/production
4. Cambiar a price IDs de producción
5. ¡Go live!
