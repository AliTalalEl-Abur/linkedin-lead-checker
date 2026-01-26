# ✅ Plan Standardization Complete

**Fecha:** 2025-01-26  
**Objetivo:** Definir una única fuente de verdad para los planes de precios

---

## 📋 Planes Definitivos

| Plan | Precio | Límite | Público Objetivo |
|------|--------|--------|------------------|
| **Starter** | $9/mes | 40 análisis/mes | Individuals & freelancers |
| **Pro** | $19/mes | 150 análisis/mes | Active professionals |
| **Team** | $49/mes | 500 análisis/mes | Teams & agencies |

---

## 🔄 Cambios Realizados

### 1. Backend (Python/FastAPI)

#### Core Configuration
- ✅ `app/core/config.py`
  - `stripe_price_business_id` → `stripe_price_team_id`
  - `usage_limit_business` → `usage_limit_team` (500)
  - `revenue_per_business_user` → `revenue_per_team_user` ($15/mes)

#### Services
- ✅ `app/core/stripe_service.py`
  - Constructor parameter: `business_price_id` → `team_price_id`
  - Plan validation: `"business"` → `"team"`
  - Docstrings actualizados

- ✅ `app/core/usage.py`
  - Query filters: `plan == "business"` → `plan == "team"`
  - Budget calculations: `usage_limit_business` → `usage_limit_team`
  - Function `get_active_subscriber_counts()` actualizada

#### API Routes
- ✅ `app/api/routes/billing.py`
  - `get_stripe_service()` pasa `team_price_id`
  - Plan validation acepta `"team"` en lugar de `"business"`

#### Application
- ✅ `app/main.py`
  - Startup logs: `has_business_price` → `has_team_price`
  - Log output: `business_price_id` → `team_price_id`

---

### 2. Frontend (Next.js)

#### Landing Page
- ✅ `web/pages/index.js`
  - Plan validation: `['starter', 'pro', 'team']`
  - Pricing card title: `"Business"` → `"Team"`
  - CTA functions: `getPricingCTA('team')`

#### Legal Pages
- ✅ `web/pages/support.js` → "Team: $49/month - 500 AI analyses"
- ✅ `web/pages/terms.js` → "Team: $49/month - 500 AI analyses per month"
- ✅ `web/terms-of-service.html` → "Team ($49/month): 500 AI analyses/month"

---

### 3. Extension (Chrome)

- ✅ `extension/pricing.html`
  - Comment: `<!-- TEAM PLAN -->`
  - Card name: `"Business"` → `"Team"`
  - Button: `onclick="selectPlan('team')"`, text `"Get Team"`

---

### 4. Configuration Files

- ✅ `.env`
  ```bash
  # Business: $49/mes → Team: $49/mes
  STRIPE_PRICE_BUSINESS_ID → STRIPE_PRICE_TEAM_ID=price_1Ssu7LPc1lhDefcv6NzhAtgz
  ```

- ✅ `.env.example`
  ```bash
  # STRIPE_PRICE_BUSINESS_ID → STRIPE_PRICE_TEAM_ID
  ```

- ✅ `setup_stripe_products.py`
  - PRODUCTS dict: `"business"` → `"team"`
  - Product name: `"Business"` → `"Team"`
  - Print output: `STRIPE_PRICE_TEAM_ID`

---

### 5. Testing & Validation Scripts

- ✅ `test_ai_activation.py` → Cuenta `team` subscribers
- ✅ `test_subscription_system.py` → Valida plan `"team"`
- ✅ `test_usage_limits.py` → Test case `("team", 500)`
- ✅ `test_stripe_webhooks.py` → Downgrade "Team → Pro"
- ✅ `verify_subscription_config.py` → Verifica `STRIPE_PRICE_TEAM_ID`
- ✅ `audit_stripe.py` → Lee `STRIPE_PRICE_TEAM_ID` desde .env

---

## 🔍 Verificación

```bash
# ✅ Config cargada correctamente
python -c "from app.core.config import get_settings; s=get_settings(); \
print(f'Team Plan:\n  Price ID: {s.stripe_price_team_id}\n  Limit: {s.usage_limit_team}\n  Revenue: \${s.revenue_per_team_user}/mes')"
```

**Output esperado:**
```
Team Plan:
  Price ID: price_1Ssu7LPc1lhDefcv6NzhAtgz
  Limit: 500
  Revenue: $15.0/mes
```

---

## 📊 Stripe Price IDs Definitivos

```bash
STRIPE_PRICE_STARTER_ID=price_1Ssu7IPc1lhDefcvGhmgzOoZ  # $9/mo - 40 analyses
STRIPE_PRICE_PRO_ID=price_1Ssu7KPc1lhDefcvgbL0z62T      # $19/mo - 150 analyses
STRIPE_PRICE_TEAM_ID=price_1Ssu7LPc1lhDefcv6NzhAtgz     # $49/mo - 500 analyses
```

---

## 🎯 Consistency Check

### Archivos de código (Python/JS/HTML)
- ✅ **Backend:** Todos los archivos `.py` actualizados
- ✅ **Frontend:** Todos los archivos `.js`/`.html` actualizados
- ✅ **Extension:** `pricing.html` actualizado

### Archivos de configuración
- ✅ `.env` → `STRIPE_PRICE_TEAM_ID`
- ✅ `.env.example` → `STRIPE_PRICE_TEAM_ID`
- ✅ `setup_stripe_products.py` → Crea producto "Team"

### Scripts de testing
- ✅ Todos los tests usan `"team"` en lugar de `"business"`

---

## 📝 Notas Importantes

1. **Naming Convention:**
   - Variable name: `team` (lowercase)
   - Display name: "Team" (capitalized)
   - Price ID: `STRIPE_PRICE_TEAM_ID`

2. **No Backwards Compatibility:**
   - Este cambio NO es compatible con bases de datos que tengan users con `plan="business"`
   - Si hay usuarios existentes, ejecutar migration:
   ```sql
   UPDATE users SET plan = 'team' WHERE plan = 'business';
   ```

3. **Documentation Files:**
   - Los archivos `.md` de documentación contienen referencias históricas a "business"
   - Se mantienen para trazabilidad, pero **NO** deben usarse como referencia de código actual

---

## ✅ Estado Final

**Todos los archivos de código activo usan consistentemente:**

- Plan name: `"team"`
- Display name: `"Team"`
- Price: `$49/month`
- Limit: `500 analyses/month`
- Target: `"Teams & agencies"`

**Única fuente de verdad establecida. ✅**
