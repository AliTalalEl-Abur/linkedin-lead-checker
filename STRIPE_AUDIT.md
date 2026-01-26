# 🔍 Stripe Configuration Audit Report

**Generated**: 2026-01-26 16:53:57
**API Key**: sk_test_51SQUv5Pc1lh...
**Mode**: Test

## 📋 Backend Configuration (.env)

| Plan | Price ID | Status |
|------|----------|--------|
| **Starter** | `price_1StrzhPc1lhDefcvp0TJY0rS` | ✅ Set |
| **Pro** | `price_1StrziPc1lhDefcvrfIRB0n0` | ✅ Set |
| **Team** | `price_1StrzjPc1lhDefcvgp2rRqh4` | ✅ Set |

## 📦 All Products in Stripe

**Summary**:
- Total Products: 11 (3 active, 8 archived)
- Total Prices: 11 (3 active, 8 inactive)

### LinkedIn Lead Checker – Team

- **Product ID**: `prod_TrbC7hxhHFQKfg`
- **Status**: ✅ Active
- **Created**: 2026-01-26
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1StrzjPc1lhDefcvgp2rRqh4` | $49.00 USD | month | ✅ Active | **TEAM** | 2026-01-26 |

### LinkedIn Lead Checker – Pro

- **Product ID**: `prod_TrbC03vEy3clly`
- **Status**: ✅ Active
- **Created**: 2026-01-26
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1StrziPc1lhDefcvrfIRB0n0` | $19.00 USD | month | ✅ Active | **PRO** | 2026-01-26 |

### LinkedIn Lead Checker – Starter

- **Product ID**: `prod_TrbCwpZAOl51en`
- **Status**: ✅ Active
- **Created**: 2026-01-26
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1StrzhPc1lhDefcvp0TJY0rS` | $9.00 USD | month | ✅ Active | **STARTER** | 2026-01-26 |

### Business

- **Product ID**: `prod_TqbJa2wQ4Qjmgm`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-24
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1Ssu7LPc1lhDefcv6NzhAtgz` | $49.00 USD | month | ❌ Inactive | - | 2026-01-24 |

### Pro

- **Product ID**: `prod_TqbJYLYD8MREkV`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-24
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1Ssu7KPc1lhDefcvgbL0z62T` | $19.00 USD | month | ❌ Inactive | - | 2026-01-24 |

### Starter

- **Product ID**: `prod_TqbJAfH3a41rRV`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-24
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1Ssu7IPc1lhDefcvGhmgzOoZ` | $9.00 USD | month | ❌ Inactive | - | 2026-01-24 |

### LinkedIn Lead Checker Team

- **Product ID**: `prod_TpR4ZHx2Pb6msa`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-20
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1SrmCwPc1lhDefcvdBqLWlbL` | $39.00 USD | month | ❌ Inactive | - | 2026-01-20 |

### LinkedIn Lead Checker Pro

- **Product ID**: `prod_TpR448WfnbT0hL`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-20
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1SrmCdPc1lhDefcvkdws7hwi` | $19.00 USD | month | ❌ Inactive | - | 2026-01-20 |

### LinkedIn Lead Checker Pro

- **Product ID**: `prod_TpPm4gaOqWjLaB`
- **Status**: ⚠️ Archived
- **Created**: 2026-01-20
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1SrkwsPc1lhDefcv1sbYqMeG` | $9.99 USD | month | ❌ Inactive | - | 2026-01-20 |

### Plus

- **Product ID**: `prod_TOmo7E2Ylc7L8e`
- **Status**: ⚠️ Archived
- **Created**: 2025-11-10
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1SRzEpPc1lhDefcvbT1byOEA` | $12.00 USD | month | ❌ Inactive | - | 2025-11-10 |

### Base

- **Product ID**: `prod_TOmoE8Z4H10sUs`
- **Status**: ⚠️ Archived
- **Created**: 2025-11-10
- **Prices**: 1

| Price ID | Amount | Interval | Status | Backend | Created |
|----------|--------|----------|--------|---------|---------|
| `price_1SRzEoPc1lhDefcvXD8Swmh1` | $8.00 USD | month | ❌ Inactive | - | 2025-11-10 |

## 🔎 Analysis

### ✅ All Active Prices are Configured

No unused active prices found.

### 🔍 Duplicate Products (Same Name)

**LinkedIn Lead Checker Pro**: 2 products found
- `prod_TpR448WfnbT0hL` - ⚠️ Archived - 1 prices - Created: 2026-01-20
- `prod_TpPm4gaOqWjLaB` - ⚠️ Archived - 1 prices - Created: 2026-01-20

### 🚨 Configuration Issues

✅ All configured prices are active and valid.

## 💡 Recommendations

1. **Keep**: Products/prices that are configured in backend and active
2. **Archive**: Old products/prices that are no longer used
3. **Review**: Active prices not configured in backend
4. **Clean**: Inactive prices can be safely ignored (Stripe keeps them for history)

## 🛠️ Next Steps

- [ ] Review unused active prices
- [ ] Archive duplicate products if not needed
- [ ] Verify all backend price IDs are correct
- [ ] Update .env if any price IDs need to change

---

*Audit completed successfully* ✅