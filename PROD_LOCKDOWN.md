# PROD_LOCKDOWN

## URLs de producción
- Web (Vercel): https://<YOUR_VERCEL_APP_DOMAIN>
- API (Render): https://<YOUR_RENDER_API_DOMAIN>
- Stripe Checkout Return: https://<YOUR_VERCEL_APP_DOMAIN>/billing-return.html?session_id={CHECKOUT_SESSION_ID}
- Stripe Webhook: https://<YOUR_RENDER_API_DOMAIN>/billing/webhook/stripe
- Chrome Web Store: https://chrome.google.com/webstore/detail/<YOUR_EXTENSION_ID>

## Variables de entorno (Vercel)
Configurar en Vercel (Project Settings → Environment Variables):
- NEXT_PUBLIC_SITE_URL=https://<YOUR_VERCEL_APP_DOMAIN>
- NEXT_PUBLIC_API_URL=https://<YOUR_RENDER_API_DOMAIN>
- NEXT_PUBLIC_CHECKOUT_RETURN_URL=https://<YOUR_VERCEL_APP_DOMAIN>/billing-return.html?session_id={CHECKOUT_SESSION_ID}
- NEXT_PUBLIC_CHROME_WEBSTORE_URL=https://chrome.google.com/webstore/detail/<YOUR_EXTENSION_ID>

## Variables de entorno (Render)
Configurar en Render (Service → Environment):
- ENV=production
- DATABASE_URL=postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
- CORS_ALLOW_ORIGINS=https://<YOUR_VERCEL_APP_DOMAIN>,chrome-extension://<YOUR_EXTENSION_ID>
- CORS_ALLOW_ORIGIN_REGEX=chrome-extension://.*
- JWT_SECRET_KEY=<MIN_32_CHARS_RANDOM>

Stripe:
- STRIPE_API_KEY=sk_live_...
- STRIPE_WEBHOOK_SECRET=whsec_...
- STRIPE_PRICE_STARTER_ID=price_...
- STRIPE_PRICE_PRO_ID=price_...
- STRIPE_PRICE_TEAM_ID=price_...

Opcional (si aplica):
- OPENAI_ENABLED=true
- OPENAI_API_KEY=sk-...
- STRIPE_SUCCESS_URL=https://<YOUR_VERCEL_APP_DOMAIN>/billing/success
- STRIPE_CANCEL_URL=https://<YOUR_VERCEL_APP_DOMAIN>/billing/cancel

## Checklist de verificación manual (10 pasos)
1. Abrir la web en https://<YOUR_VERCEL_APP_DOMAIN> y confirmar que carga sin errores.
2. Verificar que el health check responde: https://<YOUR_RENDER_API_DOMAIN>/health.
3. Iniciar sesión con un email de prueba desde la web.
4. Confirmar que el dashboard carga y muestra plan y usage.
5. Hacer clic en un botón de plan (Starter/Pro/Team) y verificar que abre Stripe Checkout.
6. Completar un pago de prueba (o en vivo) y validar el redirect a /billing-return.html.
7. En /billing-return.html, confirmar que aparece “Pago Exitoso” y CTA activa.
8. Volver al dashboard y verificar que el plan cambió (starter/pro/team).
9. Revisar en Stripe Dashboard que el webhook se recibe en https://<YOUR_RENDER_API_DOMAIN>/billing/webhook/stripe.
10. Ejecutar el script de verificación con envs de producción y confirmar “Production checks passed”.
