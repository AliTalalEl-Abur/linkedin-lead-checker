# 🚨 Stripe Duplicate Prevention - Quick Reference

## ⚡ Quick Commands

### Verificación Completa:
```powershell
python verify_stripe_sync.py
```

### Before Creating/Updating Products:
```powershell
python test_duplicate_prevention.py
```

### Create/Update Products (Safe - Validation Included):
```powershell
python setup_stripe_products.py
```

### Clean Up Duplicates:
```powershell
python archive_old_stripe_products.py
```

### Test Security:
```powershell
python test_stripe_security.py
```

---

## 🎯 Expected State

### ✅ Healthy State:
- **Active Products:** 3
- **Product Names:** 
  - LinkedIn Lead Checker – Starter
  - LinkedIn Lead Checker – Pro
  - LinkedIn Lead Checker – Team
- **Archived Products:** 8
- **Similar Products:** 0

### ❌ Unhealthy State:
- Active Products > 3 → Run archive script
- Similar Products > 0 → Review and archive
- Duplicate names → CRITICAL: Archive immediately

---

## 🔍 What Each Script Does

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `test_duplicate_prevention.py` | Check for duplicates | **ALWAYS** before setup |
| `setup_stripe_products.py` | Create/update products | Initial setup or price updates |
| `archive_old_stripe_products.py` | Archive old products | When duplicates detected |
| `test_stripe_security.py` | Test price_id whitelist | After any Stripe changes |

---

## 🚦 Decision Tree

```
Need to create/update products?
  ↓
Run: python test_duplicate_prevention.py
  ↓
Result: PASSED?
  ├─ YES → Run: python setup_stripe_products.py
  │         (Will update existing or create new safely)
  │
  └─ NO → Duplicates detected?
           ↓
           Run: python archive_old_stripe_products.py
           ↓
           Re-test: python test_duplicate_prevention.py
           ↓
           Now safe → Run: python setup_stripe_products.py
```

---

## 📋 Checklist Before Production

- [ ] `test_duplicate_prevention.py` passes
- [ ] Exactly 3 active products in Stripe
- [ ] All products have exact names
- [ ] Each product has 1 active price
- [ ] `.env` has correct price_ids
- [ ] `STRIPE_IDS.md` is up to date
- [ ] `test_stripe_security.py` passes
- [ ] Backend whitelist updated

---

## 🆘 Emergency Procedures

### If Duplicates Created Accidentally:

1. **STOP** all product creation
2. Run: `python test_duplicate_prevention.py`
3. Identify duplicate products
4. Run: `python archive_old_stripe_products.py`
5. Verify: `python test_duplicate_prevention.py`
6. Update docs: `python setup_stripe_products.py`

### If Wrong price_id in Production:

1. Check `.env` for correct price_ids
2. Verify in `STRIPE_IDS.md`
3. Update `.env` with correct IDs
4. Restart backend server
5. Test: `python test_stripe_security.py`

---

## 📊 Current IDs (Quick Copy)

```bash
# Starter Plan
STRIPE_PRICE_STARTER_ID=price_1StrzhPc1lhDefcvp0TJY0rS

# Pro Plan
STRIPE_PRICE_PRO_ID=price_1StrziPc1lhDefcvrfIRB0n0

# Team Plan
STRIPE_PRICE_TEAM_ID=price_1StrzjPc1lhDefcvgp2rRqh4
```

---

## 🔗 Documentation Links

- Full Guide: [STRIPE_DUPLICATE_PREVENTION.md](./STRIPE_DUPLICATE_PREVENTION.md)
- Implementation: [STRIPE_DUPLICATE_PREVENTION_IMPLEMENTATION.md](./STRIPE_DUPLICATE_PREVENTION_IMPLEMENTATION.md)
- Product IDs: [STRIPE_IDS.md](./STRIPE_IDS.md)
- Cleanup History: [STRIPE_CLEANUP.md](./STRIPE_CLEANUP.md)
- Security: [STRIPE_SECURITY_IMPLEMENTATION.md](./STRIPE_SECURITY_IMPLEMENTATION.md)

---

## 💡 Pro Tips

1. **Always test first:** Run `test_duplicate_prevention.py` before any Stripe operations
2. **Archive, don't delete:** Keep historical data with `active=False`
3. **Exact names matter:** "Pro" ≠ "– Pro" ≠ "- Pro"
4. **Document everything:** Auto-generated docs prevent confusion
5. **Validate security:** Run `test_stripe_security.py` after changes

---

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
