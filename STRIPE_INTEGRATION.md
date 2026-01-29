# Stripe Payment Integration Guide

This document describes the complete Stripe checkout flow for upgrading users from **Free** to **Pro** plan.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ User Flow: Free → Pro Upgrade                                   │
├─────────────────────────────────────────────────────────────────┤
│ 1. User on /dashboard (free plan)                              │
│    ↓ Clicks "🚀 Upgrade to Pro" button                         │
│ 2. Redirects to /upgrade page                                  │
│    ↓ User clicks "Upgrade Now"                                 │
│ 3. POST /billing/checkout with return_url                      │
│    ↓ Backend creates Stripe checkout session                   │
│ 4. Backend returns {sessionId, url}                            │
│    ↓ Frontend redirects user to Stripe checkout URL            │
│ 5. User completes payment on Stripe                            │
│    ↓ Stripe redirects to /checkout-result?session_id=...       │
│ 6. User sees success/cancel message                            │
│    ↓ Redirects back to /dashboard after 3 seconds              │
│ 7. Stripe fires webhook: checkout.session.completed            │
│    ↓ Backend receives webhook at POST /billing/webhook/stripe  │
│ 8. Backend verifies signature, updates user.plan = "pro"       │
│    ↓ User can now use Pro features (500 analyses/week)         │
└─────────────────────────────────────────────────────────────────┘
```

## Cancellation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Subscription Cancellation                                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. User cancels subscription in Stripe dashboard                │
│    ↓ Stripe immediately fires webhook                          │
│ 2. Stripe fires: customer.subscription.deleted                 │
│    ↓ Backend receives at POST /billing/webhook/stripe          │
│ 3. Backend verifies signature, updates user.plan = "free"      │
│    ↓ User loses Pro benefits immediately                       │
│ 4. User can re-upgrade anytime from /dashboard                │
└─────────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Get Stripe Credentials

1. Create a **Stripe account** at https://dashboard.stripe.com
2. Go to **Developers → API keys**
3. Copy **Secret key** (starts with `sk_test_` or `sk_live_`)
4. Go to **Webhooks**
5. Create new webhook endpoint:
   - URL: `https://your-domain.com/api/billing/webhook/stripe`
   - Events: `checkout.session.completed`, `customer.subscription.deleted`
6. Copy **Signing secret** (starts with `whsec_`)

### 2. Create "Pro" Product

1. In Stripe dashboard, go to **Products**
2. Create new product:
   - Name: "Pro Plan"
   - Description: "500 analyses per week, advanced filtering"
3. Create pricing:
   - Currency: USD
   - Amount: 29.00 (or your preferred amount)
   - Billing period: Monthly (recurring)
4. Copy **Price ID** (starts with `price_`)

### 3. Configure Environment Variables

Create `.env` file or set environment variables:

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_test_your_webhook_secret_here
STRIPE_PRO_PRICE_ID=price_your_price_id_here

# Frontend
NEXT_PUBLIC_CHECKOUT_RETURN_URL=NEXT_PUBLIC_SITE_URL/checkout-result?session_id={CHECKOUT_SESSION_ID}
```

### 4. Start Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (with hot reload)
uvicorn app.main:app --reload --port 8000
```

Verify Stripe routes work:
```bash
curl -X POST BACKEND_URL/billing/checkout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"return_url": "NEXT_PUBLIC_SITE_URL/checkout-result?session_id={CHECKOUT_SESSION_ID}"}'
```

Expected response:
```json
{
  "sessionId": "cs_test_xxx",
  "url": "https://checkout.stripe.com/pay/cs_test_xxx"
}
```

### 5. Start Frontend

```bash
cd web
npm install
npm run dev
```

Visit `NEXT_PUBLIC_SITE_URL` in browser.

### 6. Test Webhook Locally (Optional)

Use **Stripe CLI** to forward webhooks to your local server:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login  # authenticate with your Stripe account
stripe listen --forward-to BACKEND_URL/api/billing/webhook/stripe

# In another terminal, trigger test event:
stripe trigger checkout.session.completed
```

## API Endpoints

### POST /billing/checkout
Create Stripe checkout session for authenticated user.

**Request:**
```json
{
  "return_url": "NEXT_PUBLIC_SITE_URL/checkout-result?session_id={CHECKOUT_SESSION_ID}"
}
```

**Response (Success):**
```json
{
  "sessionId": "cs_test_1234567890",
  "url": "https://checkout.stripe.com/pay/cs_test_1234567890"
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated (missing JWT)
- `400 Bad Request`: Invalid return_url or Stripe error

---

### POST /billing/webhook/stripe
Stripe webhook endpoint (public, no auth required).

**Signature Verification:**
- Header: `stripe-signature`
- Uses HMAC-SHA256 with webhook signing secret
- Stripe Python SDK handles verification automatically

**Handled Events:**
1. `checkout.session.completed`:
   - Extracts `client_reference_id` (user_id) from session
   - Updates `user.plan = "pro"`
   - Saves `stripe_customer_id` and `stripe_subscription_id`
   
2. `customer.subscription.deleted`:
   - Finds user by `stripe_customer_id`
   - Reverts `user.plan = "free"`
   - Allows re-upgrade anytime

**Response:**
```json
{
  "status": "ok",
  "event": "checkout.session.completed"
}
```

---

## Database Schema Updates

### User Model
```python
class User:
    id: int (primary key)
    email: str (unique)
    plan: str (default "free")  # "free" or "pro"
    stripe_customer_id: str | None  # Stripe customer ID
    stripe_subscription_id: str | None  # Stripe subscription ID
    icp_config_json: dict | None  # User's ICP config
    created_at: datetime
```

---

## Usage Control by Plan

### Free Plan Limits
- **5 analyses per week** (Tuesday-Monday)
- Enforced in `POST /analyze/linkedin` endpoint
- Returns `402 Payment Required` if limit exceeded

### Pro Plan Limits
- **500 analyses per week**
- Same usage tracking, higher limit
- Automatic upgrade via Stripe webhook

---

## Frontend Pages

### /upgrade
Button page for initiating checkout.
```bash
NEXT_PUBLIC_SITE_URL/upgrade
```

- Shows Pro plan benefits
- "Upgrade Now" button → calls POST /billing/checkout
- Returns redirect to Stripe checkout URL
- "Back to Dashboard" button for cancellation

### /checkout-result
Results page after Stripe checkout.
```bash
NEXT_PUBLIC_SITE_URL/checkout-result?session_id=cs_test_xxx&status=success
```

- Shows success/cancel message
- Auto-redirects to /dashboard after 3 seconds
- Status query params: `success` or `cancel`

### /dashboard
Main dashboard showing user's plan.
```bash
NEXT_PUBLIC_SITE_URL/dashboard
```

- Displays current plan (Free/Pro badge)
- Shows usage: "X / 500 analyses this week"
- Free users see "🚀 Upgrade to Pro" button
- Pro users see plan details
- Logout button

---

## Production Checklist

- [ ] Use **production Stripe credentials** (sk_live_...)
- [ ] Update **webhook URL** to production domain
- [ ] Set environment variables in production:
  - `STRIPE_SECRET_KEY=sk_live_xxx`
  - `STRIPE_WEBHOOK_SECRET=whsec_live_xxx`
  - `STRIPE_PRO_PRICE_ID=price_xxx`
- [ ] Set **NEXT_PUBLIC_CHECKOUT_RETURN_URL** to production domain
- [ ] Update **CORS_ALLOW_ORIGINS** to production domain
- [ ] Use **HTTPS only** (Stripe requires it)
- [ ] Test complete flow:
  1. Free user → Upgrade → Checkout → Success → Pro upgrade verified
  2. Cancel subscription → User reverts to Free
  3. Re-upgrade → Works seamlessly

---

## Troubleshooting

### "Invalid signature" error in webhook
- Ensure `STRIPE_WEBHOOK_SECRET` is set correctly
- Verify webhook is configured in Stripe dashboard
- Check request body is not being processed before verification

### Payment fails with 402 error
- Verify `STRIPE_PRO_PRICE_ID` exists in Stripe
- Check Stripe mode (test vs live) matches API key

### User not upgraded after payment
- Check Stripe webhook is configured and enabled
- Verify `client_reference_id` matches user ID format
- Check database logs for webhook processing errors

### Webhook not firing
- Use Stripe CLI to test: `stripe trigger checkout.session.completed`
- Verify endpoint URL is publicly accessible (not loopback)
- Check webhook event list in Stripe dashboard for failures

---

## Code Architecture

### Backend Services
- **`app/core/stripe_service.py`**: Core Stripe logic
  - `create_checkout_session()`: Session creation
  - `handle_checkout_completed()`: Payment success handling
  - `handle_subscription_deleted()`: Cancellation handling
  - `verify_webhook_signature()`: HMAC verification

- **`app/api/routes/billing.py`**: Public endpoints
  - `POST /billing/checkout`: Create checkout session
  - `POST /billing/webhook/stripe`: Webhook handler

### Frontend Pages
- **`web/pages/upgrade.js`**: Upgrade initiation
- **`web/pages/checkout-result.js`**: Payment result display
- **`web/pages/dashboard.js`**: Plan display and upgrade button

### Utilities
- **`web/lib/api.js`**: `authenticatedFetch()` for JWT headers

---

## Security Considerations

1. **Webhook Signature Verification**: Always verify HMAC-SHA256
2. **JWT Authentication**: Checkout endpoint requires valid JWT
3. **CORS**: Webhook endpoint is public but validates signatures
4. **Price Validation**: Price ID should be environment-specific (test/live)
5. **No Hardcoded Secrets**: Use environment variables, not code

---

## Example Test Flow

```bash
# 1. Login (get JWT token)
curl -X POST BACKEND_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
# Response: {"access_token": "eyJ0eX...", "token_type": "bearer"}

# 2. Create checkout session
TOKEN="eyJ0eX..."
curl -X POST BACKEND_URL/billing/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"return_url": "NEXT_PUBLIC_SITE_URL/checkout-result?session_id={CHECKOUT_SESSION_ID}"}'
# Response: {"sessionId": "cs_test_xxx", "url": "https://checkout.stripe.com/..."}

# 3. Simulate webhook (local testing only)
curl -X POST BACKEND_URL/billing/webhook/stripe \
  -H "stripe-signature: t=123,v1=abc" \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed","data":{"object":{"client_reference_id":"1","customer":"cus_test","subscription":"sub_test"}}}'
# Note: This will fail signature verification - use Stripe CLI for real testing

# 4. Check user upgraded
curl -X GET BACKEND_URL/user \
  -H "Authorization: Bearer $TOKEN"
# Response: {"id": 1, "email": "user@example.com", "plan": "pro", ...}
```

---

## References

- [Stripe Python SDK Docs](https://github.com/stripe/stripe-python)
- [Stripe Checkout Guide](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Test Cards](https://stripe.com/docs/testing)

---

**Last Updated**: 2024-12-19
