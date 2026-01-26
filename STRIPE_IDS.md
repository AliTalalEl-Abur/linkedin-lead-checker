# Stripe Product & Price IDs

## Configuración Actual

**Fecha de creación:** 2026-01-26 17:14:13

### Nombres Exactos de Productos:
- ✅ LinkedIn Lead Checker – Starter
- ✅ LinkedIn Lead Checker – Pro
- ✅ LinkedIn Lead Checker – Team

---

## Product IDs

| Plan | Product ID | Product Name |
|------|------------|--------------|
| Starter | `prod_TrbCwpZAOl51en` | LinkedIn Lead Checker – Starter |
| Pro | `prod_TrbC03vEy3clly` | LinkedIn Lead Checker – Pro |
| Team | `prod_TrbC7hxhHFQKfg` | LinkedIn Lead Checker – Team |

---

## Price IDs

| Plan | Price ID | Monthly Price | Analyses/Month |
|------|----------|---------------|----------------|
| Starter | `price_1StrzhPc1lhDefcvp0TJY0rS` | $9.00 USD | 40 |
| Pro | `price_1StrziPc1lhDefcvrfIRB0n0` | $19.00 USD | 150 |
| Team | `price_1StrzjPc1lhDefcvgp2rRqh4` | $49.00 USD | 500 |

---

## Variables de Entorno (.env)

```bash
# Stripe Price IDs
STRIPE_PRICE_STARTER_ID=price_1StrzhPc1lhDefcvp0TJY0rS
STRIPE_PRICE_PRO_ID=price_1StrziPc1lhDefcvrfIRB0n0
STRIPE_PRICE_TEAM_ID=price_1StrzjPc1lhDefcvgp2rRqh4
```

---

## Configuración de Productos

### LinkedIn Lead Checker – Starter
- **Precio:** $9.00 USD/mes
- **Análisis:** 40/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

### LinkedIn Lead Checker – Pro
- **Precio:** $19.00 USD/mes
- **Análisis:** 150/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

### LinkedIn Lead Checker – Team
- **Precio:** $49.00 USD/mes
- **Análisis:** 500/mes
- **Facturación:** Mensual recurrente
- **Trial:** No
- **Addons:** No
- **Moneda:** USD

---

## Verificación

✅ Todos los planes creados con nombres exactos especificados
✅ Precio mensual recurrente configurado
✅ Sin períodos de prueba
✅ Sin addons adicionales
✅ Currency: USD

---

## Dashboard Stripe

Ver productos en: https://dashboard.stripe.com/products
Ver precios en: https://dashboard.stripe.com/prices
