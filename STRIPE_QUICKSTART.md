# Stripe Integration - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get Stripe Test Credentials (2 minutes)
1. Sign up at https://dashboard.stripe.com
2. Go to **Developers → API keys**
3. Copy **Secret key** (starts with `sk_test_`)
4. Go to **Webhooks**
5. Click **Add endpoint**
   - URL: `http://localhost:8000/api/billing/webhook/stripe`
   - Events: Select `checkout.session.completed` and `customer.subscription.deleted`
6. Copy **Signing secret** (starts with `whsec_`)
7. In **Products**, create a new product:
   - Name: "Pro Plan"
   - Create pricing: $29/month (recurring)
8. Copy **Price ID** (starts with `price_`)

### Step 2: Set Environment Variables (30 seconds)
Create `.env` file in project root:
```bash
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
STRIPE_PRO_PRICE_ID=price_your_price_here
```

### Step 3: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 4: Start Backend (30 seconds)
```bash
uvicorn app.main:app --reload --port 8000
```
Visit: http://127.0.0.1:8000/docs

### Step 5: Start Frontend (1 minute)
```bash
cd web
npm install
npm run dev
```
Visit: http://localhost:3000

### Step 6: Test the Flow (30 seconds)
1. Go to http://localhost:3000/login
2. Enter any email (e.g., test@example.com)
3. Go to http://localhost:3000/dashboard
4. Click **"🚀 Upgrade to Pro"**
5. Click **"Upgrade Now"**
6. Use Stripe test card: **4242 4242 4242 4242**
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
7. Complete payment
8. See success message and auto-redirect to dashboard
9. Verify plan changed to **"Pro"** ✅

---

## 🧪 Verify Installation

Run the test suite:
```bash
python test_stripe_integration.py
```

Expected output:
```
✅ PASS: Stripe Service
✅ PASS: Billing Routes
✅ PASS: User Model
✅ PASS: Webhook Signature
✅ PASS: Configuration

📈 Total: 5/5 tests passed
```

---

## 🔧 Useful Commands

### Check Backend Status
```bash
curl http://127.0.0.1:8000/health
```

### Check API Docs
```
http://127.0.0.1:8000/docs
```

### Test Webhook Locally (Advanced)
```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/api/billing/webhook/stripe

# In another terminal:
stripe trigger checkout.session.completed
```

---

## 📋 What's Implemented

✅ **Stripe Checkout**: Free → Pro plan upgrade  
✅ **Webhook Integration**: Automatic plan updates  
✅ **Database**: User plan and Stripe fields  
✅ **Frontend Pages**: `/upgrade` and `/checkout-result`  
✅ **Backend Endpoints**: `/billing/checkout` and `/billing/webhook/stripe`  
✅ **Error Handling**: Comprehensive error messages  
✅ **Usage Limits**: 5/week (free) vs 500/week (pro)  
✅ **Security**: HMAC-SHA256 signature verification  

---

## 📚 Full Documentation

For detailed setup, troubleshooting, and production deployment:
👉 See [STRIPE_INTEGRATION.md](./STRIPE_INTEGRATION.md)

---

## 🎯 Next Steps

### For Development
- [ ] Test with Stripe test cards (see list below)
- [ ] Test subscription cancellation
- [ ] Test webhook with Stripe CLI
- [ ] Verify usage limits work correctly

### For Production
- [ ] Switch to **live** Stripe credentials (sk_live_...)
- [ ] Update webhook URL to production domain
- [ ] Update `NEXT_PUBLIC_CHECKOUT_RETURN_URL` to production domain
- [ ] Deploy backend and frontend
- [ ] Run full integration tests
- [ ] Monitor webhook events in Stripe dashboard

---

## 💳 Stripe Test Cards

| Card Number | Behavior |
|-------------|----------|
| 4242 4242 4242 4242 | ✅ Successful charge |
| 4000 0000 0000 0002 | ❌ Card declined |
| 4000 0025 0000 3155 | ⚠️ Expired card |
| 4000 0000 0000 0010 | 3D Secure required |

All test cards use:
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **Name**: Any name

---

## 🐛 Troubleshooting

### "Invalid signature" error
→ Make sure `STRIPE_WEBHOOK_SECRET` is correct  
→ Verify webhook is enabled in Stripe dashboard  

### "Failed to create checkout session"
→ Check `STRIPE_SECRET_KEY` is correct  
→ Verify `STRIPE_PRO_PRICE_ID` exists in Stripe  

### User not upgrading after payment
→ Check webhook logs in Stripe dashboard  
→ Verify endpoint URL is accessible  
→ Check backend logs for errors  

### "404 Route not found"
→ Verify backend started with `uvicorn app.main:app --reload`  
→ Check that billing router was imported in `app/main.py`  

---

## ✨ Features

- **Seamless Checkout**: One-click upgrade to Pro
- **Instant Updates**: Plan changes immediately after payment
- **Flexible Cancellation**: Cancel anytime from Stripe dashboard
- **Beautiful UI**: Modern design with plan badges and upgrade buttons
- **Usage Tracking**: Monitor analyses per week by plan
- **Security**: Webhook signature verification prevents fraud

---

**Questions?** See [STRIPE_INTEGRATION.md](./STRIPE_INTEGRATION.md) for comprehensive documentation.

---

**Status**: ✅ Ready to use
**Version**: 1.0
**Last Updated**: 2024-12-19
