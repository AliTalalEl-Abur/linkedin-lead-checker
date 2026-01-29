# 🚀 Deploy Landing Next.js a Vercel (Free Tier)

## Configuración Detectada

✅ **Framework**: Next.js 14.0.0  
✅ **Build Command**: `npm run build`  
✅ **Output Directory**: `.next` (auto-detectado)  
✅ **Node Version**: 18.x (compatible)  

---

## Paso 1: Preparar Repositorio

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd C:\Users\LENOVO\Desktop\linkedin-lead-checker

# Commit todos los cambios
git add .
git commit -m "Prepare landing for Vercel deployment"
git push origin main
```

---

## Paso 2: Deploy con Vercel CLI (Recomendado)

### Instalar Vercel CLI
```bash
npm install -g vercel
```

### Login
```bash
vercel login
```

### Deploy desde el directorio web/
```bash
cd web
vercel
```

**Responde las preguntas**:
- `Set up and deploy "~/web"`? → **Yes**
- `Which scope?` → Selecciona tu cuenta
- `Link to existing project?` → **No**
- `What's your project's name?` → `linkedin-lead-checker-web` (o el que prefieras)
- `In which directory is your code located?` → **./** (ya estás en web/)
- `Want to override the settings?` → **No**

🎉 **Deployment completado!** Obtendrás una URL como:
```
https://linkedin-lead-checker-web.vercel.app
```

---

## Paso 3: Deploy desde Vercel Dashboard (Alternativa)

### 3.1 Importar Proyecto
1. Ve a [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Conecta tu cuenta de GitHub/GitLab/Bitbucket
4. Selecciona el repositorio `linkedin-lead-checker`

### 3.2 Configurar Proyecto
**Root Directory**: `web`  
**Framework Preset**: Next.js (auto-detectado)  
**Build Command**: `npm run build` (auto-detectado)  
**Output Directory**: `.next` (auto-detectado)  
**Install Command**: `npm install` (auto-detectado)  

### 3.3 Variables de Entorno (IMPORTANTE)
Click **"Environment Variables"** y agrega:

| Key | Value | Environments |
|-----|-------|--------------|
| `NEXT_PUBLIC_API_URL` | `https://linkedin-lead-checker-api.onrender.com` | Production |

> ⚠️ **Sin esta variable, la landing no podrá conectarse al backend**

### 3.4 Deploy
Click **"Deploy"** y espera ~60 segundos.

---

## Paso 4: Configurar Variables de Entorno

Si desplegaste con CLI, configura las variables:

```bash
# Desde web/
vercel env add NEXT_PUBLIC_API_URL production
# Pega: https://linkedin-lead-checker-api.onrender.com
```

O desde el Dashboard:
1. Ve a tu proyecto en Vercel
2. **Settings** → **Environment Variables**
3. Agrega:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://linkedin-lead-checker-api.onrender.com`
   - **Environments**: Production ✅

---

## Paso 5: Actualizar URLs en el Código

**Tu URL de Vercel será algo como**:
```
https://linkedin-lead-checker-web.vercel.app
```

### Archivos a actualizar (7 URLs):

#### 1. `web/pages/index.js` (líneas 9-13)
```javascript
const META = {
  title: 'LinkedIn Lead Checker - AI-Powered Lead Qualification',
  description: 'Qualify LinkedIn leads in seconds with AI analysis...',
  url: 'https://linkedin-lead-checker-web.vercel.app', // ⬅️ TU URL
  ogImage: 'https://linkedin-lead-checker-web.vercel.app/og-image.jpg' // ⬅️ TU URL
};
```

#### 2. `web/public/robots.txt` (línea 5)
```
Sitemap: https://linkedin-lead-checker-web.vercel.app/sitemap.xml
```

#### 3. `web/public/sitemap.xml` (4 URLs)
Reemplaza todas las instancias de `https://your-domain.com` con tu URL de Vercel:
```xml
<loc>https://linkedin-lead-checker-web.vercel.app/</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/login</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/upgrade</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/dashboard</loc>
```

### Commit y Redeploy
```bash
git add web/pages/index.js web/public/robots.txt web/public/sitemap.xml
git commit -m "Update URLs to Vercel domain"
git push origin main
```

Vercel redeployará automáticamente (~30 segundos).

---

## Verificación Post-Deploy

### ✅ Checklist de Producción

- [ ] **Homepage carga**: `https://tu-url.vercel.app`
- [ ] **API conectada**: Abre DevTools → Network → Debería hacer requests a tu backend de Render
- [ ] **Login funciona**: Click en "Get Started" → Debería mostrar login/magic link
- [ ] **Checkout funciona**: Click en "Subscribe Now" → Debería redirigir a Stripe
- [ ] **robots.txt**: `https://tu-url.vercel.app/robots.txt` carga
- [ ] **sitemap.xml**: `https://tu-url.vercel.app/sitemap.xml` carga
- [ ] **Metadata SEO**: View Page Source → Verifica `<meta property="og:title">` etc.

### 🧪 Test de Integración
```bash
# Verifica que el frontend puede alcanzar el backend
curl https://tu-url.vercel.app/api/health
# Debería hacer proxy o redirigir al backend de Render
```

---

## Configuración de vercel.json

**Archivo**: `web/vercel.json`

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

**Features incluidos**:
- ✅ Framework Next.js auto-detectado
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Build optimizado para producción
- ✅ Compatible con Free Tier

---

## Variables de Entorno Necesarias

| Variable | Requerida | Valor Producción | Valor Desarrollo |
|----------|-----------|------------------|------------------|
| `NEXT_PUBLIC_API_URL` | ✅ Sí | `https://linkedin-lead-checker-api.onrender.com` | `NEXT_PUBLIC_API_URL` |
| `NEXT_PUBLIC_CHECKOUT_RETURN_URL` | ❌ Opcional | Auto-generado desde `window.location.origin` | N/A |

> 💡 **Nota**: Las variables que empiezan con `NEXT_PUBLIC_` son expuestas al navegador.

---

## Free Tier Limits (Vercel Hobby)

✅ **Incluido GRATIS**:
- 100 GB bandwidth/mes
- Unlimited deployments
- Automatic HTTPS
- Global CDN
- Preview deployments (branches)
- Analytics básico

⚠️ **Límites**:
- 1 miembro del equipo
- 100 GB bandwidth (suficiente para ~500K page views/mes)
- Sin custom auth/middleware en Edge

**Conclusión**: El Free Tier es suficiente para lanzamiento y primeros usuarios. 🎉

---

## Dominios Personalizados (Opcional)

### Agregar tu dominio
1. **Vercel Dashboard** → Tu proyecto → **Settings** → **Domains**
2. Click **"Add"**
3. Ingresa tu dominio: `linkedinleadchecker.com`
4. Vercel te dará las DNS records:
   ```
   A     @       76.76.21.21
   CNAME www     cname.vercel-dns.com
   ```
5. Configura esos records en tu proveedor de DNS (GoDaddy, Namecheap, etc.)
6. Espera 5-30 minutos para propagación
7. Actualiza las 7 URLs en el código con tu dominio custom
8. Commit y push

---

## Troubleshooting

### ❌ "API request failed"
**Causa**: Variable `NEXT_PUBLIC_API_URL` no configurada  
**Fix**: Ve a Settings → Environment Variables → Agrega la variable → Redeploy

### ❌ Build falla con "Module not found"
**Causa**: Dependencias faltantes  
**Fix**: 
```bash
cd web
npm install
npm run build  # Verifica localmente
git add package-lock.json
git commit -m "Fix dependencies"
git push
```

### ❌ "This page could not be found"
**Causa**: Root directory incorrecta  
**Fix**: Vercel Settings → General → Root Directory → Cambiar a `web`

### ❌ Stripe checkout falla
**Causa**: CORS o backend no acepta requests del frontend  
**Fix**: En tu backend (Render), asegúrate de que `CORS_ALLOW_ORIGINS` incluye tu URL de Vercel

---

## Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs

# Ver lista de deployments
vercel ls

# Rollback a deployment anterior
vercel rollback [deployment-url]

# Ver variables de entorno
vercel env ls

# Remover proyecto
vercel remove [project-name]
```

---

## Estructura del Deploy

```
web/
├── .next/                    # Build output (generado)
├── pages/                    # Rutas Next.js
├── components/              # Componentes React
├── lib/                     # Utilidades (api.js)
├── public/                  # Assets estáticos
│   ├── robots.txt          # SEO
│   └── sitemap.xml         # SEO
├── styles/                  # CSS
├── package.json            # Dependencias
├── next.config.js          # Config Next.js
├── vercel.json             # Config Vercel
└── .env.example            # Template de env vars
```

---

## Next Steps Después del Deploy

1. ✅ **Monitorea analytics**: Vercel Dashboard → Tu proyecto → Analytics
2. ✅ **Configura alertas**: Settings → Notifications
3. ✅ **Habilita Web Vitals**: Para ver performance metrics
4. ✅ **Test en móvil**: Verifica responsive design
5. ✅ **Submit a Google**: Search Console → Submit sitemap
6. ✅ **Test de carga**: Usa Lighthouse o PageSpeed Insights

---

## Soporte y Recursos

- 📚 [Vercel Docs](https://vercel.com/docs)
- 💬 [Vercel Discord](https://vercel.com/discord)
- 🐛 [Vercel Support](https://vercel.com/support)
- 📖 [Next.js Docs](https://nextjs.org/docs)

---

## Resumen Rápido

```bash
# 1. Deploy
cd web && vercel

# 2. Configurar env var
vercel env add NEXT_PUBLIC_API_URL production
# Pega: https://linkedin-lead-checker-api.onrender.com

# 3. Obtener URL
# Ejemplo: https://linkedin-lead-checker-web.vercel.app

# 4. Actualizar código (7 URLs)
# - pages/index.js (2)
# - public/robots.txt (1)
# - public/sitemap.xml (4)

# 5. Redeploy
git add . && git commit -m "Update URLs" && git push
```

**Tiempo estimado: 5-10 minutos** ⚡

---

✅ **Landing lista para deploy en Vercel Free Tier**
