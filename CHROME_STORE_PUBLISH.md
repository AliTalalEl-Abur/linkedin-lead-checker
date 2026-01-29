# Chrome Web Store Publish Steps

## 1) Subir el ZIP
1. Abre Chrome Web Store Developer Dashboard.
2. Selecciona la extensión existente o crea un nuevo ítem.
3. Sube el archivo [dist/extension.zip](dist/extension.zip).

## 2) Rellenar el listing
1. Nombre y descripción:
   - Usa el texto de [extension/CHROME_STORE_LISTING.md](extension/CHROME_STORE_LISTING.md).
2. Categoría:
   - Productivity (o la que corresponda al producto).
3. Idioma principal:
   - Español o Inglés (según el listing).

## 3) Privacy Policy (Vercel)
Usa esta URL pública:
- https://linkedinleadchecker.com/privacy

## 4) Assets requeridos
- Ícono de tienda 128x128: usa [extension/public/icon-128.png](extension/public/icon-128.png).
- Screenshots: mínimo 1, recomendado 3–5.
  - Tamaño permitido: 1280x800 o 640x400.
  - Peso: < 5MB cada una.

## 5) Enviar a revisión
1. Revisa advertencias en el dashboard.
2. Envía para revisión.
3. Espera el review de Google (puede tardar horas o días).

## Nota
No publicar automáticamente. Dejar listo y esperar la aprobación.