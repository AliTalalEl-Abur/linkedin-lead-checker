# 🎯 Tracking Rápido - Guía de Uso

## ✅ Ya Está Implementado

Tu sistema de tracking ya funciona. No necesitas hacer nada más.

---

## 🚀 Prueba Rápida (2 minutos)

### 1. Inicia el Backend
```powershell
python start_server.py
```

### 2. Inicia el Frontend (otra terminal)
```powershell
cd web
npm run dev
```

### 3. Abre el Navegador
- Ve a: http://localhost:3000
- Abre DevTools (F12) → Pestaña **Network**
- Click en "Install Chrome Extension"
- Click en "Join Waitlist" (después de ingresar email)

### 4. Verifica los Logs
En la terminal del backend verás:
```
INFO - EVENT_TRACK | install_extension_click | page=landing | ip=127.0.0*** | ...
INFO - EVENT_TRACK | waitlist_join | page=landing | ip=127.0.0*** | ...
```

**✅ Si ves esos logs, el tracking funciona perfectamente.**

---

## 📊 Qué Se Trackea

| Evento | Cuándo | Ubicación |
|--------|--------|-----------|
| `install_extension_click` | Click en botón "Install Extension" | Hero + How It Works |
| `waitlist_join` | Submit del formulario de email | Final CTA |

---

## 🔒 Privacidad

- ❌ Sin cookies
- ❌ Sin Google Analytics  
- ❌ Sin seguimiento de usuario
- ✅ Solo eventos de intención
- ✅ IP parcialmente enmascarada
- ✅ Fire-and-forget (no bloquea UI)

---

## 🧪 Test Manual del Endpoint

```powershell
# Test rápido
./test_tracking.ps1

# O con curl
curl -X POST http://localhost:8000/events/track -H "Content-Type: application/json" -d '{"event":"install_extension_click","page":"landing"}'
```

---

## 📈 Ver Estadísticas

```powershell
# Analizar eventos (si guardas logs en archivo)
python analyze_tracking.py

# Por ahora, los eventos solo van a la consola
# Para guardarlos permanentemente, redirige el output:
python start_server.py > server.log 2>&1
```

---

## 🎯 Objetivo

**Saber si alguien muestra intención real:**
- ✅ Cuántos clicks en "Install Extension"
- ✅ Cuántos se unen al waitlist
- ✅ De dónde vienen (referrer)

**Sistema minimalista y respetuoso.** 🎉

---

## 📖 Documentación Completa

Ver `TRACKING_IMPLEMENTATION.md` para detalles técnicos completos.
