# 🚀 GO LIVE CHECKLIST

## ✅ Pre-Launch Technical Checklist

### Backend
- [ ] `.env` en producción (sin test keys)
- [ ] `STRIPE_SECRET_KEY` = production key (sk_live_...)
- [ ] `OPENAI_API_KEY` válida y con crédito
- [ ] `STRIPE_WEBHOOK_SECRET` = production webhook
- [ ] `JWT_SECRET_KEY` = string aleatorio 64+ chars
- [ ] `DATABASE_URL` apunta a DB de producción
- [ ] `CORS_ALLOW_ORIGINS` incluye tu dominio real
- [ ] Backend deployed y responde en `/health`
- [ ] Tabla `feedback` creada (`python migrations/migrate_feedback.py`)

### Stripe
- [ ] Productos creados en modo LIVE (no test)
- [ ] Price IDs actualizados en `.env` (price_live_...)
- [ ] Webhook configurado apuntando a tu backend `/events/stripe-webhook`
- [ ] Webhook secret actualizado en `.env`
- [ ] Test webhook funcionando (Stripe CLI o dashboard)

### Extension
- [ ] `manifest.json`: URL de privacidad añadida
- [ ] `popup.js`: API_CONFIG.baseUrl = tu backend en producción
- [ ] `pricing.html`: Links de Stripe correctos
- [ ] Extensión probada con backend de producción
- [ ] Screenshots + descripción listos para Chrome Web Store

### Landing Page
- [ ] Footer con Privacy Policy + Terms links
- [ ] Botón CTA funciona (abre extensión o pricing)
- [ ] Deployed (Vercel/Netlify)
- [ ] HTTPS funcionando
- [ ] Links de extensión actualizados

### Database
- [ ] Backup automático configurado
- [ ] Todas las tablas creadas (users, usage_event, analysis_cache, feedback)
- [ ] Índices creados correctamente

## ⚖️ Legal Minimum Checklist

- [ ] Privacy Policy publicado en tu web (linkedinleadchecker.com/privacy-policy.html)
- [ ] Terms of Service publicado (linkedinleadchecker.com/terms-of-service.html)
- [ ] Chrome Web Store listing incluye URL de Privacy Policy
- [ ] Email de contacto activo: linkedinleadchecker@gmail.com
- [ ] Checkbox "Acepto términos" en sign-up (si aplica)

## 💰 Cost Control Checklist

### Límites Configurados
- [ ] `SOFT_LAUNCH_MODE=true` (empezar con límite)
- [ ] `DAILY_REGISTRATION_LIMIT=20` o tu límite
- [ ] `usage_limit_free=3` (máx $0.09 por usuario gratis)
- [ ] `DISABLE_FREE_PLAN=false` (disponible, pero watch it)

### Kill Switches Listos
- [ ] `DISABLE_ALL_ANALYSES` funciona (probar en dev)
- [ ] `DISABLE_FREE_PLAN` funciona (probar en dev)
- [ ] Email/Slack de alertas configurado (opcional pero recomendado)

### OpenAI Budget
- [ ] Límite de uso en OpenAI dashboard configurado ($50-100/mes inicial)
- [ ] Email billing alert en OpenAI
- [ ] Calculadora: FREE (3 × $0.03) + STARTER (40 × $0.03) vs revenue

### Stripe Monitoring
- [ ] Webhook logs monitoreados
- [ ] Payment failures → email notification
- [ ] Subscriptions activas < costes AI estimados

## 🔄 Rollback Plan

### Si algo falla HARD:
```bash
# 1. KILL SWITCH inmediato
# Edita .env en producción:
DISABLE_ALL_ANALYSES=true

# 2. Reinicia backend
# Render: redeploy o restart service

# 3. Oculta extensión
# Chrome Web Store: "Unpublish" temporal

# 4. Landing page: banner de mantenimiento
<div style="background:red;color:white;padding:10px;text-align:center">
🔧 Maintenance mode. Back soon!
</div>
```

### Rollback Específico

**Si OpenAI explota en costes:**
```env
DISABLE_FREE_PLAN=true
# Solo paid users pueden analizar
```

**Si Stripe falla:**
- Deshabilita botones de upgrade temporalmente
- FREE plan sigue funcionando (validación sin $)

**Si DB se corrompe:**
- Restaurar último backup
- Perder máximo 24h de datos (si backup diario)

## 📊 Success Signals

### Primeras 48h (Validation)

**🎯 Goals:**
- [ ] 5-10 registros sin errores
- [ ] 1-2 feedbacks recibidos
- [ ] 0 errores 500 en backend
- [ ] 0 subscripciones (esperado, users prueban FREE primero)
- [ ] Email de bienvenida funciona (si tienes)

**🚨 Red Flags:**
- Registros fallan (429, 500) → revisar logs
- OpenAI errors → check API key/crédito
- Nadie llega al análisis → UX roto
- Costes AI > $1 → revisar límites

### Primera Semana (Product-Market Fit)

**🎯 Goals:**
- [ ] 20-50 usuarios registrados
- [ ] 3-5 usuarios activos diarios (usan análisis)
- [ ] 5+ feedbacks cualitativos
- [ ] 1-3 conversiones paid (Starter/Pro)
- [ ] Tasa de retención > 30% (vuelven día 2)
- [ ] NPS informal > 7/10 (de feedbacks)

**🚨 Red Flags:**
- 0 conversiones → precio muy alto o FREE muy generoso
- Churn 100% → producto no resuelve problema
- Quejas de "no sirve" → IA da malos resultados
- Costes > revenue → ajustar límites FREE urgente

### KPIs Clave (7 días)

```
Daily Active Users (DAU): ___
Conversiones FREE → Paid: ___
MRR (Monthly Recurring Revenue): $___
Coste AI total: $___
Margen bruto: MRR - Coste AI = $___

Feedback Score: ___ / 10
Bounce Rate: ___% (registran pero no usan)
```

## 📈 Quick Win Metrics

**Lo que SÍ importa ahora:**
1. ¿La gente ENTIENDE el valor? (feedback)
2. ¿Usan el FREE plan? (engagement)
3. ¿Alguien paga? (validación económica)
4. ¿Los costes son sostenibles? (unit economics)

**Lo que NO importa aún:**
- Viral growth (no optimizas para esto hasta PMF)
- SEO rankings (toma meses)
- Revenue absoluto (estás en soft launch)

## 🎯 Decision Points

### Después de 48h:
- ✅ Todo funciona → aumentar `DAILY_REGISTRATION_LIMIT` a 50
- ⚠️ Errores menores → fix y continuar
- 🚨 Errores graves → rollback y revisar

### Después de 7 días:
- ✅ 1+ conversión paid → desactivar soft launch (`SOFT_LAUNCH_MODE=false`)
- ✅ Feedback positivo → invertir en marketing
- ⚠️ 0 conversiones → revisar pricing o free limits
- 🚨 Costes > revenue → activar `DISABLE_FREE_PLAN` temporalmente

## 🔐 Security Check

- [ ] No hay API keys hardcodeadas en código
- [ ] HTTPS en todos los endpoints
- [ ] JWT expiration configurado (30 días OK)
- [ ] Passwords no se guardan en plain text (crypto)
- [ ] Rate limiting básico funciona

## 📱 Chrome Web Store Submission

- [ ] Extensión empaquetada (.zip)
- [ ] Screenshots (1280x800 o 640x400) - mínimo 1
- [ ] Descripción < 132 chars
- [ ] Privacy policy URL en manifest
- [ ] Categoría: Productivity
- [ ] Justificación de permisos (activeTab, storage)
- [ ] Cuenta de desarrollador verificada ($5 fee)

**Timeline esperado:** 1-5 días de revisión

## 🚦 Go / No-Go Decision

### ✅ GO if:
- Backend responde correctamente
- Stripe webhooks funcionan
- Extension conecta con backend
- Privacy/Terms publicados
- Kill switches probados
- Backup DB configurado

### 🛑 NO-GO if:
- Errores críticos sin resolver
- OpenAI API key inválida
- Stripe no configurado
- No tienes backup DB
- Documentos legales faltantes

---

## 🎉 Launch Day Protocol

```bash
# T-1h: Final checks
curl https://your-backend.com/health
# Should return 200 OK

# T-0: Enable production
SOFT_LAUNCH_MODE=true
DAILY_REGISTRATION_LIMIT=20

# Deploy backend
git push render main  # or your deployment

# Submit extension
# Chrome Web Store → Upload

# Launch landing
git push vercel main  # or your deployment

# T+1h: Monitor
# - Backend logs
# - Stripe dashboard
# - OpenAI usage

# T+24h: Review
# - Check feedback table
# - Review costs
# - Adjust limits if needed
```

## 📞 Emergency Contacts

- **Backend logs**: Render dashboard
- **Stripe issues**: dashboard.stripe.com/test/webhooks
- **OpenAI issues**: platform.openai.com/usage
- **Email**: linkedinleadchecker@gmail.com

---

**Status**: [ ] Pre-launch | [ ] Launched | [ ] Validated

**Launch Date**: ___________
