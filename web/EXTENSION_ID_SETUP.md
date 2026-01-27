# Configuración del Extension ID

## 🔧 Paso Importante: Configurar el Extension ID

Para que la detección de extensión funcione, necesitas actualizar el Extension ID en el código.

### 📋 Obtener el Extension ID

#### Durante Desarrollo (Extensión No Empaquetada):

1. **Cargar la extensión en Chrome:**
   - Abre `chrome://extensions/`
   - Activa "Modo de desarrollador" (arriba a la derecha)
   - Click en "Cargar extensión sin empaquetar"
   - Selecciona la carpeta `extension/`

2. **Copiar el Extension ID:**
   - En la tarjeta de la extensión, verás un ID como: `abcdefghijklmnopqrstuvwxyz123456`
   - Copia este ID

3. **Actualizar el código web:**
   ```javascript
   // En web/lib/extension.js
   const EXTENSION_IDS = [
     'abcdefghijklmnopqrstuvwxyz123456', // <-- Pega tu ID aquí
   ];
   ```

#### Para Producción (Publicada en Chrome Web Store):

1. **Después de publicar en Chrome Web Store**, obtendrás un ID permanente

2. **Actualizar ambos archivos:**
   
   **En `web/lib/extension.js`:**
   ```javascript
   const EXTENSION_IDS = [
     'production-extension-id-here', // ID de producción (permanente)
     'dev-extension-id-here',        // ID de desarrollo (opcional)
   ];
   ```
   
   **También actualizar:**
   ```javascript
   export function getChromeWebStoreUrl() {
     return `https://chrome.google.com/webstore/detail/YOUR_EXTENSION_ID_HERE`;
   }
   ```

---

## 🧪 Testing Local

### 1. Obtener tu Development Extension ID

```bash
# Abrir Chrome
chrome://extensions/

# Activar "Modo de desarrollador"
# Cargar extensión sin empaquetar desde la carpeta extension/
# Copiar el ID mostrado
```

### 2. Actualizar el código

```javascript
// web/lib/extension.js
const EXTENSION_IDS = [
  'YOUR_DEV_EXTENSION_ID_HERE', // Reemplazar con el ID real
];
```

### 3. Probar la detección

```bash
# Terminal 1: Backend
cd linkedin-lead-checker
python run.py

# Terminal 2: Frontend  
cd web
npm run dev

# Navegador:
# 1. Cargar extensión en chrome://extensions/
# 2. Abrir http://localhost:3000/billing/success?session_id=test
# 3. Verificar que detecta la extensión
```

---

## 🔍 Verificar que Funciona

### Indicators de que está funcionando:

✅ **Extensión Detectada:**
- Botón dice "Back to Extension" (no "Open Extension")
- NO muestra "Extension Not Detected"
- Click en botón intenta abrir la extensión

❌ **Extensión NO Detectada:**
- Botón dice "Open Extension"
- Muestra banner amarillo "Extension Not Detected"
- Click en botón muestra instrucciones manuales

### Testing Checklist:

- [ ] Extension ID actualizado en `web/lib/extension.js`
- [ ] Extensión cargada en Chrome
- [ ] `externally_connectable` configurado en manifest.json
- [ ] Background service worker escucha mensajes externos
- [ ] Abrir página de billing detecta extensión correctamente
- [ ] Click en "Back to Extension" funciona
- [ ] Modal de instrucciones aparece si falla
- [ ] Funciona en Chrome/Edge/Brave

---

## 📝 Actualizar Manifest de Extensión

El `manifest.json` ya está configurado para permitir comunicación desde:
- `http://localhost:3000/*` (desarrollo)
- `https://linkedin-lead-checker.vercel.app/*` (producción)
- `https://*.vercel.app/*` (preview deployments)

Si cambias el dominio de producción, actualiza:

```json
// extension/manifest.json
"externally_connectable": {
  "matches": [
    "http://localhost:3000/*",
    "https://tu-dominio.com/*"
  ]
}
```

---

## 🚀 Deploy a Producción

### 1. Publicar Extensión en Chrome Web Store

Sigue la guía oficial: https://developer.chrome.com/docs/webstore/publish/

### 2. Obtener Extension ID Permanente

Una vez publicada, Chrome Web Store te dará un ID permanente.

### 3. Actualizar Variables

```javascript
// web/lib/extension.js
const EXTENSION_IDS = [
  'chrome-web-store-extension-id', // ID de producción
];

export function getChromeWebStoreUrl() {
  return `https://chrome.google.com/webstore/detail/chrome-web-store-extension-id`;
}
```

### 4. Deploy Frontend

```bash
cd web
vercel --prod
```

### 5. Verificar

- Abrir página de producción
- Verificar que detecta extensión instalada desde Chrome Web Store
- Verificar que botón "Back to Extension" funciona

---

## ⚠️ Troubleshooting

### "Extension not detected" aunque está instalada

**Causa:** Extension ID incorrecto en el código

**Solución:**
1. Verificar el ID en `chrome://extensions/`
2. Verificar que coincida con `EXTENSION_IDS` en `extension.js`
3. Recargar la página web

### Click en "Back to Extension" no hace nada

**Causa:** `externally_connectable` no configurado o mal configurado

**Solución:**
1. Verificar `manifest.json` tiene `externally_connectable`
2. Verificar que el dominio web está en la lista `matches`
3. Recargar la extensión en `chrome://extensions/`

### Console error: "Could not establish connection"

**Causa:** Background service worker no está escuchando mensajes externos

**Solución:**
1. Verificar `background.js` tiene `onMessageExternal` listener
2. Recargar la extensión
3. Verificar logs en `chrome://extensions/` → Inspect service worker

### Works in development but not production

**Causa:** Dominio de producción no está en `externally_connectable`

**Solución:**
1. Añadir dominio de producción a `manifest.json`
2. Recompilar y republicar la extensión
3. Usuarios necesitarán actualizar la extensión

---

## 📚 Referencias

- [Chrome Extension Messaging](https://developer.chrome.com/docs/extensions/mv3/messaging/)
- [Externally Connectable](https://developer.chrome.com/docs/extensions/mv3/manifest/externally_connectable/)
- [Chrome Web Store Publishing](https://developer.chrome.com/docs/webstore/publish/)
