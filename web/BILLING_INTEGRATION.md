# Integración de Páginas de Billing - Referencia Rápida

## 🔗 Configuración de URLs de Retorno

Las páginas de billing deben configurarse en el endpoint de checkout del backend.

### URLs de Producción

```
Success: https://linkedin-lead-checker.vercel.app/billing/success?session_id={CHECKOUT_SESSION_ID}
Cancel:  https://linkedin-lead-checker.vercel.app/billing/cancel
```

### URLs de Desarrollo

```
Success: NEXT_PUBLIC_SITE_URL/billing/success?session_id={CHECKOUT_SESSION_ID}
Cancel:  NEXT_PUBLIC_SITE_URL/billing/cancel
```

---

## 📝 Actualización del Endpoint de Checkout

El endpoint `POST /billing/checkout` en el backend ya maneja las URLs de retorno mediante el parámetro `return_url`. Las páginas se acceden automáticamente cuando Stripe redirige después del pago.

### Flujo Actual (Ya Implementado):

```python
# En app/api/routes/billing.py
@router.post("/checkout")
def create_checkout_session(
    request: CheckoutRequest,  # Contiene return_url
    current_user: User = Depends(get_current_user),
    ...
):
    # El return_url viene del cliente (extension/web)
    # Formato: https://example.com/billing/success?session_id={CHECKOUT_SESSION_ID}
    
    result = stripe_service.create_checkout_session(
        user_id=str(current_user.id),
        email=current_user.email,
        return_url=request.return_url,
        plan=request.plan,
    )
    
    return CheckoutResponse(**result)
```

---

## 💻 Configuración desde la Extensión Chrome

### Ejemplo de Llamada desde Extension:

```javascript
// En la extensión Chrome
async function upgradeToPlan(plan) {
  const API_URL = 'NEXT_PUBLIC_API_URL';
  const WEB_URL = 'NEXT_PUBLIC_SITE_URL';
  
  const response = await fetch(`${API_URL}/billing/checkout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      plan: plan, // "starter", "pro", or "team"
      return_url: `${WEB_URL}/billing/success?session_id={CHECKOUT_SESSION_ID}`
    })
  });
  
  const { url } = await response.json();
  
  // Abrir Stripe checkout en nueva pestaña
  chrome.tabs.create({ url });
}
```

**Importante:** El placeholder `{CHECKOUT_SESSION_ID}` es reemplazado automáticamente por Stripe.

---

## 🌐 Configuración desde la Web App

### Ejemplo de Llamada desde Next.js:

```javascript
// En web/pages/upgrade.js o similar
import { authenticatedFetch } from '../lib/api';

async function handleUpgrade(plan) {
  try {
    // Construir return_url basado en el entorno
    const returnUrl = `${window.location.origin}/billing/success?session_id={CHECKOUT_SESSION_ID}`;
    
    const data = await authenticatedFetch('/billing/checkout', {
      method: 'POST',
      body: JSON.stringify({
        plan: plan,
        return_url: returnUrl
      })
    });
    
    // Redirigir a Stripe checkout
    window.location.href = data.url;
  } catch (error) {
    console.error('Checkout failed:', error);
    alert('Failed to start checkout. Please try again.');
  }
}
```

---

## 🔄 Flujo Completo

```
1. Usuario hace click en "Upgrade"
   ↓
2. Extension/Web llama a POST /billing/checkout
   Body: { plan: "pro", return_url: "https://...success?session_id={CHECKOUT_SESSION_ID}" }
   ↓
3. Backend crea sesión de Stripe
   ↓
4. Backend retorna { sessionId: "cs_xxx", url: "https://checkout.stripe.com/..." }
   ↓
5. Extension/Web abre URL de Stripe en nueva pestaña
   ↓
6. Usuario completa pago en Stripe
   ↓
7a. ÉXITO: Stripe redirige a /billing/success?session_id=cs_xxx
    - Página muestra "Payment Successful"
    - Llama a GET /billing/status
    - Muestra plan activo
    - Botón "Back to Extension"
   
7b. CANCELAR: Stripe redirige a /billing/cancel
    - Página muestra "Payment Cancelled"
    - Botón "View Pricing Plans"
    - Botón "Back to Extension"
```

---

## 🎯 Variables de Entorno

### Backend (.env)

```bash
# Stripe Configuration
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER_ID=price_...  # $9/mo - 40 analyses
STRIPE_PRICE_PRO_ID=price_...      # $19/mo - 150 analyses
STRIPE_PRICE_TEAM_ID=price_...     # $49/mo - 500 analyses
```

### Frontend (.env.local)

```bash
# API URL
NEXT_PUBLIC_API_URL=https://your-api.com  # Producción
# O
NEXT_PUBLIC_API_URL=NEXT_PUBLIC_API_URL
```

---

## ✅ Testing End-to-End

### 1. Testing Local (Development)

```bash
# Terminal 1: Backend
cd linkedin-lead-checker
python run.py

# Terminal 2: Frontend
cd web
npm run dev

# Navegar a:
# NEXT_PUBLIC_SITE_URL/upgrade
# Click en "Upgrade to Pro"
# Completar pago en Stripe Test Mode
# Verificar redirección a /billing/success
```

### 2. Testing con Stripe Test Mode

Usar estas tarjetas de prueba:
- **Éxito:** 4242 4242 4242 4242
- **Requiere 3D Secure:** 4000 0027 6000 3184
- **Falla:** 4000 0000 0000 0002

### 3. Verificar Webhook

```bash
# Instalar Stripe CLI
stripe login

# Escuchar webhooks
stripe listen --forward-to BACKEND_URL/billing/webhook/stripe

# Trigger test event
stripe trigger checkout.session.completed
```

---

## 🚨 Troubleshooting

### Problema: Página de éxito muestra "Loading..." indefinidamente

**Causa:** No puede obtener /billing/status (no autenticado o token inválido)

**Solución:**
1. Verificar que el usuario esté logueado
2. Verificar que el token JWT sea válido
3. Verificar que el endpoint /billing/status responda correctamente

### Problema: "Session ID not found"

**Causa:** URL no tiene el parámetro session_id

**Solución:**
1. Verificar que `return_url` incluya `{CHECKOUT_SESSION_ID}`
2. Verificar que Stripe esté reemplazando el placeholder

### Problema: Plan no se actualiza después del pago

**Causa:** Webhook de Stripe no está funcionando

**Solución:**
1. Verificar que el webhook esté configurado en Stripe Dashboard
2. Verificar que `STRIPE_WEBHOOK_SECRET` sea correcto
3. Verificar logs del backend para ver si el webhook está llegando
4. Usar Stripe CLI para testing local

---

## 📱 Responsive Design

Ambas páginas son completamente responsive:

- **Mobile:** Vista optimizada para pantallas pequeñas
- **Tablet:** Contenido centrado con buen espaciado
- **Desktop:** Máximo ancho de 512px (lg) para mejor legibilidad

---

## 🎨 Personalización

### Cambiar colores de planes:

```javascript
// En success.js
const getPlanDisplay = (plan) => {
  const plans = {
    starter: { name: 'Starter', color: 'text-green-600', ... },
    pro: { name: 'Pro', color: 'text-blue-600', ... },
    team: { name: 'Team', color: 'text-purple-600', ... }
  };
  return plans[plan] || { ... };
};
```

### Cambiar mensajes:

Editar directamente los textos en:
- `web/pages/billing/success.js`
- `web/pages/billing/cancel.js`

### Añadir analytics:

```javascript
// En success.js, después de cargar el status
useEffect(() => {
  if (!status.loading && status.plan) {
    // Track successful payment
    gtag('event', 'purchase', {
      transaction_id: session_id,
      value: getPlanValue(status.plan),
      currency: 'USD',
      items: [{
        item_id: status.plan,
        item_name: `${status.plan} Plan`,
      }]
    });
  }
}, [status]);
```

---

## ✅ Checklist de Deploy

Antes de hacer deploy a producción:

- [ ] Actualizar `NEXT_PUBLIC_API_URL` en Vercel
- [ ] Configurar webhooks en Stripe Dashboard
- [ ] Probar flujo completo en staging
- [ ] Verificar URLs de retorno en código
- [ ] Probar ambas páginas (success y cancel)
- [ ] Verificar que /billing/status funcione
- [ ] Probar en mobile y desktop
- [ ] Verificar analytics (si aplica)

---

## 📞 Soporte

Si encuentras problemas:
1. Revisar logs del backend
2. Revisar consola del navegador
3. Verificar configuración de Stripe
4. Contactar al equipo de desarrollo
