# ENV_MATRIX

## Frontend (Vercel)
**Required**
- NEXT_PUBLIC_API_URL=https://<tu-backend-render>
- NEXT_PUBLIC_SITE_URL=https://<tu-landing-vercel>
- NEXT_PUBLIC_CHECKOUT_RETURN_URL=https://<tu-landing-vercel>/billing-return.html?session_id={CHECKOUT_SESSION_ID}
- NEXT_PUBLIC_CHROME_WEBSTORE_URL=https://chrome.google.com/webstore/detail/<your-extension-id>

## Backend (Render)
**Required**
- FRONTEND_URL=https://<tu-landing-vercel>
- CORS_ALLOW_ORIGINS=FRONTEND_URL,chrome-extension://*
- CORS_ALLOW_ORIGIN_REGEX=chrome-extension://.*
- DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/<db>
- JWT_SECRET_KEY=<min-32-chars>
- ENV=production

**Stripe**
- STRIPE_API_KEY=sk_live_...
- STRIPE_WEBHOOK_SECRET=whsec_...
- STRIPE_PRICE_STARTER_ID=price_...
- STRIPE_PRICE_PRO_ID=price_...
- STRIPE_PRICE_TEAM_ID=price_...

**Optional**
- OPENAI_ENABLED=true
- OPENAI_API_KEY=sk-...
- STRIPE_SUCCESS_URL=FRONTEND_URL/billing/success
- STRIPE_CANCEL_URL=FRONTEND_URL/billing/cancel

## Extension (Chrome)
**Required**
- BACKEND_URL=https://<tu-backend-render>

**Notes**
- BACKEND_URL debe coincidir con NEXT_PUBLIC_API_URL.
- FRONTEND_URL debe coincidir con NEXT_PUBLIC_SITE_URL.
