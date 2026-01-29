# 📊 Sistema de Tracking Mínimo y Respetuoso

## ✅ Implementación Completa

El sistema de tracking está **completamente implementado y funcionando**. Es minimalista, respetuoso de la privacidad y cumple con todas tus especificaciones.

---

## 🎯 Eventos Trackeados

### 1. Click en "Install Extension"
- **Evento:** `install_extension_click`
- **Ubicaciones:**
  - Botón principal del Hero (`landing`)
  - Sección "How it works" (`how-it-works`)

### 2. Click en "Join Waitlist"
- **Evento:** `waitlist_join`
- **Ubicación:** Formulario de email (`landing`)

---

## 🔒 Características de Privacidad

### ✅ Lo que SÍ hacemos:
- Log de evento (tipo de acción)
- Página donde ocurrió
- Referrer (si existe, para saber de dónde vienen)
- IP parcialmente enmascarada (`192.168.***`)
- User agent truncado (primeros 50 caracteres)

### ❌ Lo que NO hacemos:
- ❌ No cookies persistentes
- ❌ No Google Analytics
- ❌ No pixel tracking
- ❌ No fingerprinting de usuario
- ❌ No IDs persistentes
- ❌ No seguimiento entre sesiones
- ❌ No venta de datos

---

## 📁 Archivos Involucrados

### Frontend
**`web/lib/tracking.ts`**
```typescript
export async function trackEvent(
  event: 'install_extension_click' | 'waitlist_join',
  page: string = 'landing'
)
```
- Fire-and-forget (no bloquea UI)
- Falla silenciosamente si hay error
- Solo envía evento, página y referrer

**`web/pages/index.js`**
- Línea 60: `trackEvent('waitlist_join', 'landing')`
- Línea 73: `trackEvent('install_extension_click', 'landing')`
- Línea 243: `trackEvent('install_extension_click', 'how-it-works')`

### Backend
**`app/api/routes/events.py`**
```python
@router.post("/track")
async def track_event(event_data: TrackEvent, request: Request)
```
- Solo logs en servidor
- IP parcialmente enmascarada
- Sin base de datos persistente (solo logs)
- Respuesta inmediata

**`app/main.py`**
- Línea 9: Import del router
- Línea 54: `app.include_router(events_router)`

---

## 🧪 Cómo Verificar

### 1. Verificar en el Frontend (Navegador)

```bash
# Iniciar el frontend
cd web
npm run dev
```

Abre el navegador en NEXT_PUBLIC_SITE_URL y:

1. **Abre DevTools (F12) → Pestaña Network**
2. **Click en "Install Chrome Extension"**
   - Verás una petición POST a `/events/track`
   - Payload: `{"event": "install_extension_click", "page": "landing", "referrer": null}`
   - Status: 200 OK

3. **Scroll hasta el formulario final**
4. **Ingresa un email y click en "Join Waitlist"**
   - Verás otra petición POST a `/events/track`
   - Payload: `{"event": "waitlist_join", "page": "landing", "referrer": null}`
   - Status: 200 OK

### 2. Verificar en el Backend (Logs)

```bash
# Iniciar el backend
cd ..
python start_server.py
```

En la consola del servidor verás logs como:

```
INFO - EVENT_TRACK | install_extension_click | page=landing | ip=127.0.0*** | ua=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebM | referrer=direct
INFO - EVENT_TRACK | waitlist_join | page=landing | ip=127.0.0*** | ua=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebM | referrer=direct
```

### 3. Verificar con cURL (Directo al Backend)

```bash
# Test evento de instalación
curl -X POST BACKEND_URL/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "event": "install_extension_click",
    "page": "landing",
    "referrer": "https://google.com"
  }'

# Test evento de waitlist
curl -X POST BACKEND_URL/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "event": "waitlist_join",
    "page": "landing"
  }'
```

Respuesta esperada:
```json
{
  "status": "tracked",
  "event": "install_extension_click",
  "timestamp": "2026-01-25T10:30:45.123456"
}
```

---

## 📊 Análisis de Datos

### Dónde se almacenan los eventos
**Actualmente:** Solo en logs del servidor
- Ubicación: Consola/stdout donde corre el backend
- Formato: Texto estructurado (fácil de parsear)

### Opciones Futuras (Sin invasión de privacidad)

#### Opción 1: Base de datos simple (SQLite local)
```python
# Crear tabla simple
CREATE TABLE event_logs (
    id INTEGER PRIMARY KEY,
    event_type TEXT,
    page TEXT,
    timestamp DATETIME,
    referrer TEXT
);
```

#### Opción 2: Archivo de texto (append-only)
```python
# En events.py
with open("events.log", "a") as f:
    f.write(f"{timestamp}|{event}|{page}|{referrer}\n")
```

#### Opción 3: Servicio de analytics respetuoso
- **Plausible Analytics** (open source, GDPR compliant)
- **Umami** (self-hosted, sin cookies)
- **Fathom** (privacy-first analytics)

---

## 📈 Métricas que Puedes Obtener

Con este sistema simple puedes responder:

1. **¿Cuántas personas hacen click en "Install Extension"?**
   - Cuenta: `grep "install_extension_click" events.log | wc -l`

2. **¿Cuántas personas se unen al waitlist?**
   - Cuenta: `grep "waitlist_join" events.log | wc -l`

3. **¿De dónde vienen los usuarios?**
   - Analiza el campo `referrer`

4. **¿Qué sección genera más clicks?**
   - Compara `page=landing` vs `page=how-it-works`

5. **Tasa de conversión aproximada**
   - Installs / Visitas totales (puedes trackear `page_view` si quieres)

---

## 🔧 Mejoras Opcionales (Sin Romper Privacidad)

### 1. Agregar tracking de page views (opcional)
```typescript
// En tracking.ts
export async function trackPageView(page: string) {
  trackEvent('page_view', page);
}

// En index.js
useEffect(() => {
  trackPageView('landing');
}, []);
```

### 2. Guardar en archivo local (backend)
```python
# En events.py
import json
from pathlib import Path

@router.post("/track")
async def track_event(event_data: TrackEvent, request: Request):
    # ... código actual ...
    
    # Guardar en archivo
    log_file = Path("data/events.jsonl")
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps({
            "event": event_data.event,
            "page": event_data.page,
            "referrer": event_data.referrer,
            "timestamp": datetime.utcnow().isoformat()
        }) + "\n")
```

### 3. Dashboard simple (Python script)
```python
# analyze_events.py
import json
from collections import Counter

events = []
with open("data/events.jsonl") as f:
    for line in f:
        events.append(json.loads(line))

print(f"Total eventos: {len(events)}")
print(f"Installs: {sum(1 for e in events if e['event'] == 'install_extension_click')}")
print(f"Waitlist: {sum(1 for e in events if e['event'] == 'waitlist_join')}")

referrers = Counter(e.get('referrer', 'direct') for e in events)
print("\nTop referrers:")
for ref, count in referrers.most_common(5):
    print(f"  {ref}: {count}")
```

---

## ✅ Checklist de Cumplimiento

- ✅ Solo trackea 2 eventos específicos
- ✅ No cookies invasivas
- ✅ Sin Google Analytics
- ✅ Fire-and-forget (no bloquea UI)
- ✅ Falla silenciosamente (no rompe la experiencia)
- ✅ IP parcialmente enmascarada
- ✅ Solución simple (logs propios)
- ✅ Cumple con el objetivo: saber intención real

---

## 🚀 Estado Actual

**✅ TODO FUNCIONANDO**

El sistema está listo y operativo. No requiere configuración adicional.

### Para probarlo ahora mismo:

```bash
# Terminal 1: Backend
python start_server.py

# Terminal 2: Frontend
cd web
npm run dev

# Navega a NEXT_PUBLIC_SITE_URL
# Haz click en los botones
# Mira los logs en la Terminal 1
```

---

## 📝 Notas Importantes

1. **Producción:** Asegúrate de que `NEXT_PUBLIC_API_URL` apunte a tu backend en producción
2. **CORS:** El endpoint `/events/track` ya está habilitado en CORS
3. **Rate Limiting:** Considera agregar rate limiting básico para evitar spam
4. **GDPR:** Este sistema es GDPR-compliant (no PII, sin persistencia obligatoria)

---

## 🎯 Objetivo Cumplido

> ✅ **"Saber si alguien muestra intención real"**

Con estos 2 eventos puedes:
- Medir interés en la extensión (clicks en Install)
- Capturar leads calificados (waitlist signups)
- Sin invadir privacidad
- Sin romper la experiencia de usuario
- Con datos accionables

**Sistema minimalista, respetuoso y efectivo.** 🎉
