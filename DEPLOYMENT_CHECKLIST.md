# Stripe Integration - Deployment Checklist

## Pre-Launch Verification (Development)

### Backend Setup
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Test suite passes: `python test_stripe_integration.py` → 5/5 tests
- [ ] Backend starts: `uvicorn app.main:app --reload`
- [ ] API docs accessible: http://127.0.0.1:8000/docs
- [ ] Health check works: http://127.0.0.1:8000/health

### Frontend Setup
- [ ] Node dependencies installed: `cd web && npm install`
- [ ] Frontend starts: `npm run dev`
- [ ] Pages load:
  - [ ] http://localhost:3000/login
  - [ ] http://localhost:3000/onboarding
  - [ ] http://localhost:3000/dashboard
  - [ ] http://localhost:3000/upgrade
  - [ ] http://localhost:3000/checkout-result

### Stripe Test Account
- [ ] Stripe account created at https://dashboard.stripe.com
- [ ] Test API keys obtained (sk_test_...)
- [ ] Webhook secret obtained (whsec_test_...)
- [ ] Pro product created with price
- [ ] Price ID copied (price_...)
- [ ] Webhook endpoint configured:
  - [ ] URL: http://localhost:8000/api/billing/webhook/stripe
  - [ ] Events: checkout.session.completed, customer.subscription.deleted
  - [ ] Enabled in Stripe dashboard

### Environment Configuration
- [ ] `.env` file created with:
  - [ ] `STRIPE_SECRET_KEY=sk_test_...`
  - [ ] `STRIPE_WEBHOOK_SECRET=whsec_...`
  - [ ] `STRIPE_PRO_PRICE_ID=price_...`
- [ ] Test using: `python test_stripe_integration.py`

---

## Manual Testing (Development)

### User Flow: Free → Pro
- [ ] Login with test email
- [ ] Dashboard shows "Free" plan badge
- [ ] Dashboard shows "0 / 5 analyses this week"
- [ ] Click "🚀 Upgrade to Pro"
- [ ] /upgrade page loads with plan benefits
- [ ] Click "Upgrade Now"
- [ ] Redirects to Stripe checkout
- [ ] Use test card: 4242 4242 4242 4242
- [ ] Complete payment successfully
- [ ] See success message on /checkout-result
- [ ] Auto-redirect to /dashboard after 3 seconds
- [ ] Dashboard shows "Pro" plan badge
- [ ] Dashboard shows "0 / 500 analyses this week"

### Webhook Testing (Advanced)
- [ ] Install Stripe CLI
- [ ] Run: `stripe listen --forward-to localhost:8000/api/billing/webhook/stripe`
- [ ] In another terminal: `stripe trigger checkout.session.completed`
- [ ] Check backend logs for webhook processing
- [ ] Verify user plan updated in database

### Error Cases
- [ ] Cancel at Stripe checkout → /checkout-result shows cancel message
- [ ] Invalid Stripe credentials → 400 error with message
- [ ] Missing JWT token → 401 unauthorized
- [ ] Webhook signature invalid → 400 signature error
- [ ] Non-existent user in webhook → graceful handling

---

## Production Deployment

### Stripe Configuration
- [ ] Switch to **live** API keys:
  - [ ] `STRIPE_SECRET_KEY=sk_live_...`
  - [ ] `STRIPE_WEBHOOK_SECRET=whsec_live_...`
- [ ] Create **live** Pro product with pricing
- [ ] Copy **live** `STRIPE_PRO_PRICE_ID=price_...`
- [ ] Configure webhook endpoint to **production domain**:
  - [ ] URL: `https://yourdomain.com/api/billing/webhook/stripe`
  - [ ] Events: checkout.session.completed, customer.subscription.deleted

### Backend Deployment
- [ ] Set environment variables on production server
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations (if using Alembic): `alembic upgrade head`
- [ ] Start with production ASGI server (e.g., Gunicorn):
  ```bash
  gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
  ```
- [ ] Verify endpoints are accessible:
  - [ ] GET /health → 200 OK
  - [ ] POST /billing/checkout → 401 (requires JWT)
  - [ ] POST /billing/webhook/stripe → 400 (invalid signature for test)

### Frontend Deployment
- [ ] Update environment variables:
  - [ ] `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
  - [ ] `NEXT_PUBLIC_CHECKOUT_RETURN_URL=https://yourdomain.com/checkout-result?session_id={CHECKOUT_SESSION_ID}`
- [ ] Build for production: `npm run build`
- [ ] Test build locally: `npm run start`
- [ ] Deploy to hosting (Vercel, AWS, etc.)
- [ ] Verify pages load over HTTPS:
  - [ ] https://yourdomain.com/login
  - [ ] https://yourdomain.com/dashboard
  - [ ] https://yourdomain.com/upgrade

### Security Checklist
- [ ] HTTPS enabled on all endpoints (Stripe requires it)
- [ ] CORS configured for production domain:
  - [ ] `CORS_ALLOW_ORIGINS=https://yourdomain.com`
  - [ ] `CORS_ALLOW_ORIGIN_REGEX=chrome-extension://[your-extension-id]`
- [ ] JWT secret key changed from default
- [ ] Database password secure (not in code)
- [ ] No API keys logged or exposed
- [ ] Webhook signature verification enabled
- [ ] Rate limiting configured (prevent abuse)
- [ ] HTTPS only (redirect HTTP → HTTPS)

### Post-Deployment Testing
- [ ] Test complete flow with production credentials:
  1. Login
  2. Go to dashboard
  3. Click upgrade
  4. Complete real payment (small amount)
  5. Verify plan upgraded
  6. Check webhook logs in Stripe dashboard
- [ ] Monitor error logs for issues
- [ ] Test cancellation flow:
  1. Cancel subscription in Stripe dashboard
  2. Verify webhook fires
  3. Check user plan reverted to free
- [ ] Test re-upgrade:
  1. User can re-upgrade after cancellation
  2. New payment succeeds
  3. Plan updates immediately

### Monitoring & Maintenance
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor webhook failures in Stripe dashboard
- [ ] Set up alerts for:
  - [ ] Failed transactions
  - [ ] Webhook delivery issues
  - [ ] Database errors
  - [ ] API errors
- [ ] Regular backups of database
- [ ] Review Stripe logs weekly for anomalies
- [ ] Keep Stripe SDK updated: `pip install --upgrade stripe`

---

## Database Schema Verification

### Users Table
```sql
SELECT * FROM users LIMIT 1;
```
Should have columns:
- `id` (primary key)
- `email` (unique)
- `plan` (varchar, default 'free')
- `stripe_customer_id` (nullable)
- `stripe_subscription_id` (nullable)
- `icp_config_json` (JSON)
- `created_at` (timestamp)

### Usage Events Table
```sql
SELECT * FROM usage_events WHERE event_type='analyze' LIMIT 1;
```
Should track analyses with:
- `user_id`
- `event_type` ('analyze')
- `timestamp`
- `metadata` (JSON)

---

## Rollback Plan

If issues occur in production:

1. **Revert Stripe Configuration**:
   - [ ] Switch back to test API keys in environment
   - [ ] Test locally first before re-deploying

2. **Database Rollback**:
   - [ ] Restore from backup if data corruption
   - [ ] Reset user plans manually if needed

3. **Code Rollback**:
   - [ ] Revert to previous commit with `git revert`
   - [ ] Rebuild and redeploy frontend

4. **Communication**:
   - [ ] Notify users of service disruption
   - [ ] Provide status updates
   - [ ] ETA for resolution

---

## Documentation

Ensure users have access to:
- [ ] Quick start guide: `STRIPE_QUICKSTART.md`
- [ ] Full documentation: `STRIPE_INTEGRATION.md`
- [ ] API documentation: `/docs` (Swagger UI)
- [ ] Support email/contact

---

## Sign-Off

- [ ] **Developer**: Code review completed, all tests passing
- [ ] **QA**: Manual testing completed, edge cases verified
- [ ] **Product**: Feature requirements met
- [ ] **DevOps**: Production environment configured
- [ ] **Security**: Security checklist completed
- [ ] **Manager**: Approval to launch

**Launch Date**: _____________  
**Deployed By**: _____________  
**Version**: 1.0  

---

## Post-Launch Monitoring (First Week)

- [ ] Check error logs daily
- [ ] Monitor webhook success rate (should be >99%)
- [ ] Monitor user conversion rate (free → pro)
- [ ] Check average payment time
- [ ] Monitor API response times
- [ ] Track customer support issues
- [ ] Verify usage limits working correctly
- [ ] Check database performance

---

## Useful Commands

### Check Logs
```bash
# Backend logs
tail -f logs/app.log

# Stripe test webhook
stripe trigger checkout.session.completed

# Database query
sqlite3 linkedin_lead_checker.db "SELECT plan, COUNT(*) FROM users GROUP BY plan;"
```

### Quick Verification
```bash
# Health check
curl https://yourdomain.com/api/health

# API docs
https://yourdomain.com/api/docs

# Test checkout endpoint (with valid JWT)
curl -X POST https://yourdomain.com/api/billing/checkout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"return_url": "https://yourdomain.com/checkout-result?session_id={CHECKOUT_SESSION_ID}"}'
```

---

**Status**: Ready for deployment  
**Last Updated**: 2024-12-19  
**Questions?** See STRIPE_INTEGRATION.md
