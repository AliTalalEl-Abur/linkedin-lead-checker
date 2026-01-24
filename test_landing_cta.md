# Testing Landing Page Dynamic CTAs

## ✅ Implementación Completada

### Archivos Modificados:

1. **web/pages/index.js**
   - Agregado `useEffect` para verificar estado de autenticación al montar
   - Agregado estado `userState` con `loading`, `isAuthenticated`, `hasSubscription`, `plan`
   - Función `getPrimaryCTA()` - Retorna CTA dinámico para Hero
   - Función `getPricingCTA(planName)` - Retorna CTA dinámico para pricing cards
   - CTAs actualizados para usar lógica condicional

2. **web/components/PricingCard.js**
   - Agregado prop `ctaOnClick` para manejar clicks
   - Botón ahora acepta `onClick` handler

3. **web/lib/api.js**
   - Agregado `API_URL` constant con detección SSR-safe
   - Compatible con localhost y producción

---

## 🎯 Lógica de CTAs

### Hero Section (Primary CTA)

| Estado Usuario | CTA Text | Acción |
|---|---|---|
| **No logueado** | "Install Chrome Extension (Free Preview)" | Abre Chrome Web Store |
| **Logueado sin suscripción** | "Unlock Full AI Analysis" | Redirige a `/upgrade` |
| **Suscriptor activo** | "Open Extension" | Alert con instrucciones |

### Pricing Cards

| Estado Usuario | CTA Text | Acción |
|---|---|---|
| **No logueado** | "Get Started" | Redirige a `/login` |
| **Logueado sin suscripción** | "Subscribe Now" | Redirige a `/billing/checkout?plan={plan}` |
| **Plan actual** | "Current Plan" | Redirige a `/dashboard` |
| **Otro plan activo** | "Switch Plan" | Redirige a `/billing/checkout?plan={plan}` |

---

## 🧪 Testing Manual

### Escenario 1: Usuario No Logueado
```
1. Abrir landing page (/)
2. Verificar Hero CTA: "Install Chrome Extension (Free Preview)"
3. Verificar Pricing CTAs: "Get Started"
4. Click Hero CTA → Abre Chrome Web Store
5. Click Pricing CTA → Redirige a /login
```

### Escenario 2: Usuario Logueado Sin Suscripción
```
1. Login en /login
2. Visitar landing page (/)
3. Verificar Hero CTA: "Unlock Full AI Analysis"
4. Verificar Pricing CTAs: "Subscribe Now"
5. Click Hero CTA → Redirige a /upgrade
6. Click Pricing CTA → Redirige a /billing/checkout?plan=starter
```

### Escenario 3: Suscriptor Activo (Plan Pro)
```
1. Login con cuenta Pro
2. Visitar landing page (/)
3. Verificar Hero CTA: "Open Extension"
4. Verificar Pricing CTAs:
   - Starter: "Switch Plan"
   - Pro: "Current Plan"
   - Business: "Switch Plan"
5. Click Hero CTA → Muestra alert
6. Click "Current Plan" → Redirige a /dashboard
7. Click "Switch Plan" → Redirige a checkout
```

---

## 🔒 Protección SSR

### Verificaciones Implementadas:

1. **`getStoredToken()`** - Verifica `typeof window !== "undefined"`
2. **`useEffect`** - Solo ejecuta en client-side
3. **`API_URL`** - Detecta entorno SSR-safe
4. **Estado inicial** - `loading: true` previene flash de contenido incorrecto

### No Rompe:
- ✅ Server-Side Rendering (Next.js SSR)
- ✅ Static Site Generation (Next.js SSG)
- ✅ Routing de Next.js
- ✅ Hydration

---

## 📝 Ejemplo de Código

### Hero CTA Dinámico:
```jsx
<Button 
  variant="primary" 
  onClick={primaryCTA.onClick}
  disabled={userState.loading}
>
  {primaryCTA.text}
</Button>
```

### Pricing CTA Dinámico:
```jsx
<PricingCard
  title="Pro"
  price="19"
  cta={getPricingCTA('pro').text}
  ctaOnClick={getPricingCTA('pro').onClick}
/>
```

### Función de Lógica:
```javascript
const getPrimaryCTA = () => {
  if (!userState.isAuthenticated) {
    return {
      text: 'Install Chrome Extension (Free Preview)',
      onClick: () => window.open('https://chrome.google.com/webstore', '_blank')
    };
  }
  
  if (!userState.hasSubscription) {
    return {
      text: 'Unlock Full AI Analysis',
      onClick: () => window.location.href = '/upgrade'
    };
  }
  
  return {
    text: 'Open Extension',
    onClick: () => alert('Click the icon in your Chrome toolbar!')
  };
};
```

---

## 🚀 Despliegue

### Variables de Entorno:
```env
# No required - auto-detected
# Production: https://linkedin-lead-checker-api.onrender.com
# Localhost: http://127.0.0.1:8000
```

### Build Command:
```bash
cd web
npm run build
npm run start
```

---

## ✨ Mejoras Futuras

1. **Loading State**: Spinner mientras carga estado de autenticación
2. **Error Handling**: Manejo de errores de API más robusto
3. **Caching**: Cachear estado de usuario para reducir llamadas
4. **Analytics**: Trackear conversión de cada CTA
5. **A/B Testing**: Testear diferentes copies de CTAs

---

**Status:** ✅ Implementado y listo para testing
**SSR Safe:** ✅ Compatible
**Breaking Changes:** ❌ Ninguno
