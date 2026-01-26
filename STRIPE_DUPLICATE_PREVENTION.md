# 🛡️ Stripe Duplicate Prevention System

## 📋 Overview

This document describes the protections implemented to prevent creating duplicate Stripe products in the future.

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---

## 🚨 Critical Rules

### ⛔ DO NOT:
- Run `setup_stripe_products.py` without checking for duplicates first
- Create new Stripe products manually in the Dashboard without cleanup
- Archive products without documenting their IDs
- Use old price_ids in production code

### ✅ DO:
- Run `test_duplicate_prevention.py` before creating products
- Use `archive_old_stripe_products.py` to clean up duplicates
- Always document product_ids and price_ids in `STRIPE_IDS.md`
- Update `.env` with new price_ids after any changes

---

## 🔍 Duplicate Prevention Features

### 1. Pre-Flight Validation in setup_stripe_products.py

The setup script now includes comprehensive validation **before** creating any products:

```python
# 🚨 CRITICAL: Validate Stripe state BEFORE creating anything
duplicate_info = check_for_duplicates()
validate_stripe_state(duplicate_info)
```

**What it checks:**
- ✅ Exact product name matches (prevents duplicate "LinkedIn Lead Checker – Pro")
- ✅ Similar product names (warns about "LinkedIn Lead Checker Pro" vs "Lead Checker - Pro")
- ✅ Multiple products with same name (blocks execution if found)
- ✅ Archived products (counts them for safety)

**What happens if duplicates detected:**
```
❌ VALIDATION FAILED: Found X products named 'LinkedIn Lead Checker – Pro'
⚠️  DO NOT PROCEED WITHOUT CLEANUP!
   Run archive_old_stripe_products.py first to clean up duplicates
```

### 2. Enhanced create_or_update_product()

The product creation function now:

```python
# Check for exact match first
if existing_product:
    print(f"   ℹ️  Product '{name}' already exists (ID: {existing_product.id})")
    print(f"   ⚠️  UPDATING EXISTING - NOT CREATING NEW")
    return existing_product.id

# ⚠️ WARNING: Creating NEW product - make sure this is intended
print(f"   🆕 Creating NEW product: {name}")
print(f"   ⚠️  WARNING: This will create a new product in Stripe!")
```

**Safety features:**
- Searches for exact name match before creating
- Updates existing products instead of creating duplicates
- Prints clear warnings when creating new products
- Requires explicit confirmation in logs

### 3. Documentation Requirements

**STRIPE_IDS.md must contain:**
- ✅ All product_ids
- ✅ All price_ids
- ✅ Creation date/time
- ✅ Exact product names used
- ✅ Links to verify in Stripe Dashboard

**Example:**
```markdown
## Product IDs
| Plan | Product ID | Product Name |
|------|------------|--------------|
| Pro | prod_abc123 | LinkedIn Lead Checker – Pro |
```

---

## 🧪 Testing Workflow

### Before Running setup_stripe_products.py:

1. **Test duplicate detection:**
   ```powershell
   python test_duplicate_prevention.py
   ```

2. **Expected output (safe state):**
   ```
   ✅ PASSED: Exactly 3 unique products with expected names exist
   ✅ Safe to run setup_stripe_products.py (will update existing products)
   ```

3. **If duplicates found:**
   ```
   ❌ FAILED: Duplicate products detected!
   ⚠️  DANGER: Run archive_old_stripe_products.py to clean up duplicates
   ```
   **DO NOT PROCEED** - clean up first!

### After Cleaning Up:

1. **Archive old products:**
   ```powershell
   python archive_old_stripe_products.py
   ```

2. **Re-test:**
   ```powershell
   python test_duplicate_prevention.py
   ```

3. **Verify in Stripe Dashboard:**
   - Go to https://dashboard.stripe.com/products
   - Confirm only 3 active products:
     - ✅ LinkedIn Lead Checker – Starter
     - ✅ LinkedIn Lead Checker – Pro
     - ✅ LinkedIn Lead Checker – Team

4. **Now safe to run setup:**
   ```powershell
   python setup_stripe_products.py
   ```

---

## 📊 Current State

### Active Products (3):
| Plan | Product Name | Product ID | Price ID |
|------|--------------|------------|----------|
| Starter | LinkedIn Lead Checker – Starter | prod_Str0SFfldpR6lP | price_1StrzhPc1lhDefcvp0TJY0rS |
| Pro | LinkedIn Lead Checker – Pro | prod_Str0YRuJwM7fMy | price_1StrziPc1lhDefcvrfIRB0n0 |
| Team | LinkedIn Lead Checker – Team | prod_Str1KFfB6eBXoU | price_1StrzjPc1lhDefcvgp2rRqh4 |

### Archived Products (8):
- LinkedIn Lead Checker Pro (old)
- LinkedIn Lead Checker Starter (old)
- LinkedIn Lead Checker Team (old)
- LinkedIn Lead Checker Plus
- LinkedIn Lead Checker Base
- LinkedIn Lead Checker – Business
- LinkedIn Lead Checker – Pro (old version)
- LinkedIn Lead Checker – Starter (old version)

---

## 🔒 Security Integration

The duplicate prevention system works with the security whitelist:

### In app/core/stripe_service.py:

```python
# Only these 3 price_ids are accepted
allowed_price_ids = {
    'price_1StrzhPc1lhDefcvp0TJY0rS': 'starter',  # $15/month
    'price_1StrziPc1lhDefcvrfIRB0n0': 'pro',      # $29/month
    'price_1StrzjPc1lhDefcvgp2rRqh4': 'team',     # $79/month
}

def validate_price_id(self, price_id: str):
    """Validates that price_id is in whitelist"""
    if price_id not in self.allowed_price_ids:
        logger.error(f"SECURITY_VIOLATION: Unauthorized price_id: {price_id}")
        raise ValueError(f"Invalid price_id: {price_id}")
```

**This means:**
- Even if someone creates a duplicate product, the backend won't accept its price_id
- Old price_ids are rejected automatically
- Fraud attempts are logged with SECURITY_VIOLATION tag

---

## 🛠️ Maintenance Procedures

### Monthly Audit (Recommended):

1. **Check for new products:**
   ```powershell
   python test_duplicate_prevention.py
   ```

2. **Verify price_ids in .env match STRIPE_IDS.md:**
   ```powershell
   cat .env | Select-String "STRIPE_PRICE"
   ```

3. **Check archived products count:**
   - Should remain at 8 (unless intentionally changed)

4. **Verify security whitelist:**
   ```python
   # In app/core/stripe_service.py
   # Should only contain 3 price_ids
   allowed_price_ids = { ... }
   ```

### If New Duplicates Appear:

1. **Identify source:**
   - Was setup script run incorrectly?
   - Was product created manually in Dashboard?
   - Was API key used elsewhere?

2. **Archive immediately:**
   ```powershell
   python archive_old_stripe_products.py
   ```

3. **Update documentation:**
   - Add to STRIPE_CLEANUP.md
   - Note date and reason for duplicate

4. **Review security:**
   - Check application logs for unauthorized checkout attempts
   - Verify webhook security

---

## 📝 Scripts Reference

### test_duplicate_prevention.py
**Purpose:** Verify no duplicates exist before creating products

**Tests:**
1. ✅ Exact name matches (should be 0 or 3)
2. ✅ Similar product names (should be 0)
3. ✅ Price uniqueness (each product = 1 price)
4. ✅ Archived products count (currently 8)

**Run before:** Any Stripe product creation

### setup_stripe_products.py
**Purpose:** Create/update Stripe products with exact names

**Features:**
- ✅ Pre-flight duplicate detection
- ✅ Validates Stripe state before proceeding
- ✅ Updates existing products instead of creating duplicates
- ✅ Generates STRIPE_IDS.md documentation
- ✅ Clear warnings when creating new products

**Run when:** Initial setup or price updates only

### archive_old_stripe_products.py
**Purpose:** Archive (not delete) old/duplicate products

**Features:**
- ✅ Sets active=False on old products
- ✅ Keeps data for historical reference
- ✅ Generates STRIPE_CLEANUP.md report
- ✅ Verifies final state (3 active, 8 archived)

**Run when:** Duplicates detected or cleanup needed

---

## 🎯 Success Criteria

### ✅ System is Working Correctly When:

1. **Product Count:**
   - Exactly 3 active products
   - All have exact names: "LinkedIn Lead Checker – [Starter/Pro/Team]"
   - Each product has exactly 1 active price

2. **Documentation:**
   - STRIPE_IDS.md exists and is current
   - .env contains correct price_ids
   - STRIPE_CLEANUP.md lists all archived products

3. **Security:**
   - Backend validates all price_ids against whitelist
   - Old price_ids are rejected
   - Tests pass: `python test_stripe_security.py`

4. **Prevention:**
   - `test_duplicate_prevention.py` passes
   - No similar products in active state
   - Setup script validates before creating

### ❌ Action Required If:

- More than 3 active products → Run archive script
- Similar product names exist → Review and archive
- test_duplicate_prevention.py fails → Investigate and clean up
- Backend accepts old price_ids → Update whitelist
- STRIPE_IDS.md is outdated → Regenerate with setup script

---

## 📚 Related Documentation

- [STRIPE_IDS.md](./STRIPE_IDS.md) - Current product and price IDs
- [STRIPE_CLEANUP.md](./STRIPE_CLEANUP.md) - Archive history
- [STRIPE_SECURITY_IMPLEMENTATION.md](./STRIPE_SECURITY_IMPLEMENTATION.md) - Security validation
- [archive_old_stripe_products.py](./archive_old_stripe_products.py) - Cleanup script
- [setup_stripe_products.py](./setup_stripe_products.py) - Product creation script

---

## 🆘 Troubleshooting

### Problem: "Multiple products with same name"

**Diagnosis:**
```powershell
python test_duplicate_prevention.py
```

**Solution:**
```powershell
# 1. Archive duplicates
python archive_old_stripe_products.py

# 2. Verify cleanup
python test_duplicate_prevention.py

# 3. Update documentation
python setup_stripe_products.py
```

### Problem: "Setup script creates duplicate instead of updating"

**Cause:** Product name mismatch (e.g., "Pro" vs "– Pro")

**Solution:**
1. Check PRODUCTS dict in setup_stripe_products.py
2. Verify exact names match Stripe Dashboard
3. Archive incorrect product
4. Re-run setup

### Problem: "Old price_id accepted by backend"

**Cause:** Whitelist not updated

**Solution:**
1. Check app/core/stripe_service.py
2. Update allowed_price_ids dict
3. Restart backend server
4. Test: `python test_stripe_security.py`

---

## 🔐 Security Checklist

Before going to production:

- [ ] Exactly 3 active Stripe products
- [ ] All old products archived (active=False)
- [ ] Backend whitelist updated with 3 price_ids
- [ ] .env contains correct price_ids
- [ ] STRIPE_IDS.md is current
- [ ] test_duplicate_prevention.py passes
- [ ] test_stripe_security.py passes
- [ ] Webhooks configured and tested
- [ ] Archive script available for future cleanup
- [ ] Team trained on duplicate prevention procedures

---

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Version:** 1.0.0
**Status:** ✅ Production Ready
