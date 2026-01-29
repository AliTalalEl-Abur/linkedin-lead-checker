# ✅ Checklist de Verificación del Tracking

## 🎯 Verificación Rápida (2 minutos)

### Paso 1: Iniciar Servicios
```powershell
# Terminal 1: Backend
python start_server.py

# Terminal 2: Frontend
cd web
npm run dev
```

**✅ Verifica:** Ambos servicios inician sin errores

---

### Paso 2: Abrir Navegador
1. Abre NEXT_PUBLIC_SITE_URL
2. Abre DevTools (F12)
3. Ve a la pestaña **Network**
4. Filtra por: `/events`

**✅ Verifica:** DevTools está abierto y configurado

---

### Paso 3: Test de Evento 1 - Install Extension
1. En la página, click en **"Install Chrome Extension"** (Hero)
2. En DevTools → Network, busca:
   - Request: `POST /events/track`
   - Status: `200`
   - Response: `{"status": "tracked", "event": "install_extension_click", ...}`

**✅ Verifica:**
- [ ] Request aparece en Network
- [ ] Status es 200
- [ ] Response contiene "install_extension_click"

---

### Paso 4: Test de Evento 2 - Join Waitlist
1. Scroll hasta el final de la página
2. Ingresa tu email: `test@example.com`
3. Click en **"Join Waitlist"**
4. En DevTools → Network, busca:
   - Request: `POST /events/track`
   - Status: `200`
   - Response: `{"status": "tracked", "event": "waitlist_join", ...}`

**✅ Verifica:**
- [ ] Request aparece en Network
- [ ] Status es 200
- [ ] Response contiene "waitlist_join"

---

### Paso 5: Verificar Logs del Backend
En la terminal donde corre el backend, busca:

```
INFO - EVENT_TRACK | install_extension_click | page=landing | ip=127.0.0*** | ...
INFO - EVENT_TRACK | waitlist_join | page=landing | ip=127.0.0*** | ...
```

**✅ Verifica:**
- [ ] Aparecen 2 líneas de log
- [ ] Primera con `install_extension_click`
- [ ] Segunda con `waitlist_join`
- [ ] IP está parcialmente enmascarada (`***`)

---

## 🧪 Test Automatizado del Endpoint

```powershell
./test_tracking.ps1
```

**✅ Verifica:**
- [ ] Test 1: Install Extension Click → ✅ Success
- [ ] Test 2: Join Waitlist Event → ✅ Success
- [ ] Test 3: Install from How-It-Works → ✅ Success
- [ ] Sin errores en output

---

## 🔍 Verificación de Código

### Frontend: tracking.ts
```powershell
# Abrir archivo
code web/lib/tracking.ts
```

**✅ Verifica:**
- [ ] Función `trackEvent` existe
- [ ] Acepta eventos: `install_extension_click` y `waitlist_join`
- [ ] Usa `fetch` con `keepalive: true`
- [ ] Tiene `catch` para fallos silenciosos

### Frontend: index.js
```powershell
# Buscar llamadas a trackEvent
grep -n "trackEvent" web/pages/index.js
```

**✅ Verifica:**
- [ ] Línea ~60: `trackEvent('waitlist_join', 'landing')`
- [ ] Línea ~73: `trackEvent('install_extension_click', 'landing')`
- [ ] Línea ~243: `trackEvent('install_extension_click', 'how-it-works')`

### Backend: events.py
```powershell
# Abrir archivo
code app/api/routes/events.py
```

**✅ Verifica:**
- [ ] Endpoint `POST /track` existe
- [ ] Acepta `TrackEvent` model
- [ ] Logea con `logger.info`
- [ ] IP está enmascarada (solo primeros 8 chars + `***`)
- [ ] Retorna JSON con status "tracked"

### Backend: main.py
```powershell
# Verificar que el router está registrado
grep -n "events_router" app/main.py
```

**✅ Verifica:**
- [ ] Import en línea ~9: `from app.api.routes.events import router as events_router`
- [ ] Registro en línea ~54: `app.include_router(events_router)`

---

## 🌐 Verificación de Producción

### Variables de Entorno
```powershell
# En Vercel, verifica que existe:
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

**✅ Verifica:**
- [ ] Variable configurada en Vercel
- [ ] Apunta a tu backend de producción
- [ ] Sin trailing slash

### CORS en Backend
```python
# En app/main.py, verifica CORS
allow_origins = settings.cors_allow_origins
```

**✅ Verifica:**
- [ ] Frontend URL está en `cors_allow_origins`
- [ ] O `cors_allow_origin_regex` permite tu dominio
- [ ] Métodos incluyen POST

### Endpoint Accesible
```bash
# Test desde fuera (reemplaza URL)
curl -X POST https://your-backend.com/events/track \
  -H "Content-Type: application/json" \
  -d '{"event":"install_extension_click","page":"landing"}'
```

**✅ Verifica:**
- [ ] Status 200
- [ ] Response JSON válido
- [ ] Sin error de CORS

---

## 📊 Verificación de Datos

### Logs del Servidor
```powershell
# Si guardas logs en archivo
cat server.log | grep "EVENT_TRACK"
```

**✅ Verifica:**
- [ ] Logs aparecen en formato esperado
- [ ] Contienen evento, page, ip, referrer
- [ ] IP está enmascarada

### Análisis de Eventos
```powershell
python analyze_tracking.py
```

**✅ Verifica:**
- [ ] Script corre sin errores
- [ ] Muestra conteo de eventos
- [ ] Calcula tasa de conversión
- [ ] Lista top referrers

---

## 🔒 Verificación de Privacidad

### Sin Cookies
1. Abre DevTools → Application → Cookies
2. Visita tu landing page
3. Click en botones CTA

**✅ Verifica:**
- [ ] No se crean cookies relacionadas con tracking
- [ ] Solo cookies técnicas necesarias (autenticación, etc.)

### Sin IDs Persistentes
```powershell
# Buscar en código que no haya localStorage para tracking
grep -r "localStorage" web/lib/tracking.ts
```

**✅ Verifica:**
- [ ] No hay uso de `localStorage` en tracking.ts
- [ ] No hay `sessionStorage` para IDs de usuario
- [ ] No hay fingerprinting

### IP Enmascarada
```powershell
# Ver logs
cat server.log | grep "EVENT_TRACK"
```

**✅ Verifica:**
- [ ] IPs terminan en `***`
- [ ] Solo primeros 8 caracteres visibles
- [ ] Ejemplo: `192.168.***` o `127.0.0***`

---

## ✅ Checklist Final

### Funcionalidad
- [ ] ✅ Tracking de Install Extension funciona
- [ ] ✅ Tracking de Waitlist Join funciona
- [ ] ✅ Logs aparecen en backend
- [ ] ✅ No bloquea UI (fire-and-forget)
- [ ] ✅ Falla silenciosamente si hay error

### Privacidad
- [ ] ✅ Sin cookies invasivas
- [ ] ✅ Sin Google Analytics
- [ ] ✅ Sin IDs persistentes
- [ ] ✅ IP enmascarada
- [ ] ✅ Sin fingerprinting
- [ ] ✅ Solo eventos de intención

### Código
- [ ] ✅ Frontend: tracking.ts implementado
- [ ] ✅ Frontend: index.js llama a trackEvent
- [ ] ✅ Backend: events.py implementado
- [ ] ✅ Backend: router registrado en main.py
- [ ] ✅ Sin errores de lint/tipos

### Producción
- [ ] ✅ NEXT_PUBLIC_API_URL configurado
- [ ] ✅ CORS habilitado en backend
- [ ] ✅ Endpoint accesible públicamente
- [ ] ✅ Logs configurados (opcional)

### Documentación
- [ ] ✅ TRACKING_INDEX.md (índice maestro)
- [ ] ✅ TRACKING_QUICKSTART.md (guía rápida)
- [ ] ✅ TRACKING_SUMMARY.md (resumen ejecutivo)
- [ ] ✅ TRACKING_IMPLEMENTATION.md (detalles técnicos)
- [ ] ✅ TRACKING_EXAMPLE_DATA.md (ejemplos)
- [ ] ✅ Scripts de test y análisis

---

## 🎉 Resultado Esperado

Si todos los checkboxes están marcados:

```
✅✅✅ SISTEMA DE TRACKING COMPLETAMENTE FUNCIONAL ✅✅✅

- Eventos trackeados correctamente
- Privacidad respetada
- Código sin errores
- Documentación completa
- Listo para producción
```

**🚀 Sistema minimalista, respetuoso y efectivo.**

---

## 🆘 Troubleshooting

### Problema: Eventos no aparecen en Network
**Solución:**
1. Verifica que el frontend esté corriendo
2. Limpia cache del navegador (Ctrl + Shift + Delete)
3. Revisa NEXT_PUBLIC_API_URL en `.env.local`

### Problema: Error 404 en /events/track
**Solución:**
1. Verifica que el backend esté corriendo
2. Revisa que `events_router` esté registrado en `main.py`
3. Comprueba CORS settings

### Problema: Logs no aparecen en backend
**Solución:**
1. Verifica nivel de logging (debe ser INFO o DEBUG)
2. Busca línea: `logging.basicConfig(level=logging.INFO)`
3. Redirige output si es necesario: `python start_server.py > server.log 2>&1`

### Problema: Error de CORS
**Solución:**
1. Añade tu frontend URL a `cors_allow_origins` en backend
2. O configura `cors_allow_origin_regex` en settings
3. Reinicia el backend

---

## 📞 Ayuda

Para más detalles, consulta:
- [TRACKING_IMPLEMENTATION.md](TRACKING_IMPLEMENTATION.md) → Sección "Cómo Verificar"
- [TRACKING_QUICKSTART.md](TRACKING_QUICKSTART.md) → Prueba en 2 minutos
- [TRACKING_INDEX.md](TRACKING_INDEX.md) → Índice maestro
