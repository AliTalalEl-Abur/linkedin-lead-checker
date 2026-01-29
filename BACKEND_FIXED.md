# ✅ BACKEND CRASH RESUELTO

## 🔍 Problema Identificado

El backend se cerraba inmediatamente al recibir peticiones HTTP debido a un problema de Windows con la ejecución interactiva de uvicorn en la terminal de VS Code. Cuando se ejecutaba `uvicorn` y luego se hacía una petición HTTP desde la misma sesión, Windows cerraba el proceso.

## ✅ Solución

El servidor **funciona correctamente** cuando se ejecuta mediante:
- `python -m uvicorn app.main:application --host 0.0.0.0 --port 8001`
- O usando subprocess desde un script Python separado

## 🧪 Pruebas Realizadas

1. ✅ Endpoint /health responde correctamente (200 OK)
2. ✅ Base de datos SQLite se crea correctamente con todas las tablas
3. ✅ Nuevas columnas agregadas: `lifetime_analyses_count`, `last_analysis_at`
4. ✅ Configuración de CORS funcional (tipo List[str] | str)

## 🎯 Sistema de Precios Implementado

### FREE Plan
- **Límite**: 3 análisis TOTALES (lifetime, no se resetea)
- **Costo máximo**: $0.09 (3 × $0.03 por análisis)
- **Sin tarjeta de crédito**

### PRO Plan  
- **Precio**: $19/mes
- **Límite**: 100 análisis por semana (se resetea cada lunes)
- **Texto UI**: "Unlimited (fair use)"
- **Costo máximo**: $12/mes (100 análisis/semana × 4 semanas × $0.03)

### TEAM Plan
- **Precio**: $39/mes
- **Límite**: 300 análisis por semana para 3-5 usuarios
- **Costo máximo**: $36/mes (300 × 4 × $0.03)

### Rate Limiting
- **30 segundos** mínimo entre análisis por usuario
- Previene spam y reduce costos

### Kill Switches (Env Vars)
- `DISABLE_FREE_PLAN=true` → Deshabilita análisis FREE (retorna 402)
- `DISABLE_ALL_ANALYSES=true` → Deshabilita TODOS los análisis (retorna 503)

## 📊 Arquitectura de Control de Costos

Todas las validaciones se ejecutan **ANTES** de llamar a la API de OpenAI:

```python
# En app/core/usage.py - check_usage_limit()
1. ✅ Kill switch global (disable_all_analyses)
2. ✅ Kill switch FREE (disable_free_plan)
3. ✅ Rate limit (30 segundos desde last_analysis_at)
4. ✅ FREE lifetime limit (lifetime_analyses_count >= 3)
5. ✅ PRO/TEAM weekly limit (UsageEvent.count >= 100/300)
```

## 🚀 Cómo Iniciar el Sistema

### Opción 1: Script de desarrollo (recomendado)
```powershell
python start_dev.py
```

### Opción 2: Manual
```powershell
# Terminal 1: Backend
python -m uvicorn app.main:application --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Stripe CLI
stripe listen --forward-to BACKEND_URL/billing/webhook
```

### Opción 3: Probar sin Stripe
```powershell
python -m uvicorn app.main:application --host 0.0.0.0 --port 8001
```

## 🧪 Testing E2E Pendiente

### Test 1: FREE Plan - 3 Análisis Lifetime
1. Abrir `web/dashboard.html` en Chrome
2. Login con email nuevo (se crea usuario FREE)
3. Configurar ICP en dashboard
4. Instalar extensión de Chrome
5. Ir a perfil de LinkedIn → Click "Analyze Profile"
6. Repetir 2 veces más (total 3 análisis)
7. **Verificar**: 4to análisis muestra error 402 "You've used all 3 free lead checks"
8. **Verificar**: NO se realizó llamada a OpenAI

### Test 2: PRO Plan - 100 Análisis/Semana
1. Desde dashboard, click "Pro $19/mo" button
2. Completar checkout con `4242 4242 4242 4242`
3. Verificar webhook recibido → plan actualizado a "pro"
4. Verificar badge cambia a "⭐ PRO"
5. Realizar 100 análisis esta semana
6. **Verificar**: Análisis 101 retorna 429 "Weekly limit reached"
7. Esperar al lunes siguiente
8. **Verificar**: Límite se resetea a 0/100

### Test 3: Rate Limiting - 30 Segundos
1. Realizar 1 análisis
2. Inmediatamente intentar otro análisis
3. **Verificar**: Retorna 429 "Please wait 30 seconds between analyses"
4. Esperar 30 segundos
5. **Verificar**: Siguiente análisis funciona

### Test 4: Kill Switches
```powershell
# Test disable_free_plan
$env:DISABLE_FREE_PLAN="true"
python -m uvicorn app.main:application --host 0.0.0.0 --port 8001
# Usuario FREE intenta análisis → 402 "Free analyses are temporarily disabled"

# Test disable_all_analyses
$env:DISABLE_ALL_ANALYSES="true"
python -m uvicorn app.main:application --host 0.0.0.0 --port 8001
# Cualquier usuario intenta análisis → 503 "Analysis service temporarily unavailable"
```

### Test 5: TEAM Plan - 300 Análisis/Semana
1. Click "Team $39/mo" button
2. Completar checkout
3. Verificar badge "👥 TEAM"
4. Verificar límite 300/semana

## 📝 Cambios Realizados

### Backend
- ✅ `app/core/config.py`: Nuevos límites y kill switches
- ✅ `app/models/user.py`: Columnas `lifetime_analyses_count`, `last_analysis_at`
- ✅ `app/core/usage.py`: Sistema completo de control de uso
- ✅ `app/api/routes/analyze.py`: Integración con `check_usage_limit()`
- ✅ `app/api/routes/billing.py`: Soporte para planes PRO y TEAM
- ✅ `app/core/stripe_service.py`: Multi-plan checkout
- ✅ `app/main.py`: Tipo CORS corregido

### Frontend
- ✅ `web/dashboard.html`: Dual upgrade buttons, nuevo copy
- ✅ `web/dashboard.js`: Plan-specific usage notes
- ✅ `extension/popup.html`: Dual buttons, nuevo copy
- ✅ `extension/popup.js`: Plan badges, upgrade flow

### Database
- ✅ Columnas añadidas a tabla `users`
- ✅ Base de datos recreada con esquema actualizado

### Stripe
- ✅ Producto PRO creado: $19/mo (`price_1SrmCdPc1lhDefcvkdws7hwi`)
- ✅ Producto TEAM creado: $39/mo (`price_1SrmCwPc1lhDefcvdBqLWlbL`)

## 🎉 Estado Actual

**✅ BACKEND FUNCIONANDO CORRECTAMENTE**

- El servidor arranca sin errores
- Endpoint /health responde
- Base de datos operativa
- Todos los routers cargados
- CORS configurado
- Nuevo sistema de límites implementado
- Control de costos activo

**⏳ Pendiente: Testing E2E completo del flujo de usuario**

## 🔗 URLs Importantes

- Backend API: BACKEND_URL
- API Docs (Swagger): BACKEND_URL/docs
- Health Check: BACKEND_URL/health
- Dashboard: `file:///C:/Users/LENOVO/Desktop/linkedin-lead-checker/web/dashboard.html`

## 💡 Próximos Pasos

1. Ejecutar `python start_dev.py` para iniciar el backend
2. Abrir dashboard en Chrome
3. Seguir los tests E2E descritos arriba
4. Verificar todos los límites funcionan correctamente
5. Probar flujo de upgrade Stripe con ambos planes

## 🐛 Debugging

Si encuentras problemas:

```powershell
# Ver logs detallados
python -m uvicorn app.main:application --host 0.0.0.0 --port 8001 --log-level debug

# Verificar database
sqlite3 linkedin_lead_checker.db ".schema users"

# Test rápido de health
curl BACKEND_URL/health

# Ver productos Stripe
stripe products list
stripe prices list
```
