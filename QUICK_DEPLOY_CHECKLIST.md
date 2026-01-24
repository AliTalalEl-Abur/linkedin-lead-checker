# 🚀 Quick Deployment Checklist

## Before Deployment
- [x] Remove localhost hardcoded references
- [x] Add NEXT_PUBLIC_API_URL environment variable
- [x] Add SEO metadata (title, description, OG tags)
- [x] Create robots.txt
- [x] Create sitemap.xml
- [x] Verify build passes (`npm run build`)
- [x] Create vercel.json configuration
- [x] Vercel compatibility verified

## Deploy to Vercel
```bash
cd web/
vercel
```

## After First Deployment
- [ ] Set environment variable in Vercel:
  ```
  NEXT_PUBLIC_API_URL=https://linkedin-lead-checker-api.onrender.com
  ```
- [ ] Get Vercel deployment URL (e.g., `your-app.vercel.app`)
- [ ] Update `pages/index.js`:
  ```javascript
  const META = {
    url: 'https://your-app.vercel.app', // UPDATE
    ogImage: 'https://your-app.vercel.app/og-image.jpg' // UPDATE
  };
  ```
- [ ] Update `public/robots.txt`:
  ```
  Sitemap: https://your-app.vercel.app/sitemap.xml
  ```
- [ ] Update `public/sitemap.xml`:
  - Replace all `your-domain.com` with `your-app.vercel.app`
- [ ] Commit and push changes (Vercel will auto-redeploy)

## Test Production
- [ ] Visit homepage: https://your-app.vercel.app
- [ ] Test login flow
- [ ] Test upgrade/checkout flow
- [ ] Verify API connection works
- [ ] Check `/robots.txt` loads
- [ ] Check `/sitemap.xml` loads

## Optional: Custom Domain
- [ ] Add domain in Vercel dashboard
- [ ] Configure DNS records
- [ ] Update all URLs with custom domain
- [ ] Redeploy

---

## Environment Variables (Vercel Dashboard)

**Production:**
```
NEXT_PUBLIC_API_URL=https://linkedin-lead-checker-api.onrender.com
```

**Preview (optional):**
```
NEXT_PUBLIC_API_URL=https://your-backend-preview.onrender.com
```

---

## Files Modified

✅ `web/lib/api.js` - Use env var
✅ `web/pages/index.js` - SEO metadata
✅ `web/pages/upgrade.js` - Dynamic URLs
✅ `web/next.config.js` - Production config

## Files Created

✅ `web/.env.example` - Environment template
✅ `web/public/robots.txt` - SEO
✅ `web/public/sitemap.xml` - SEO
✅ `web/vercel.json` - Vercel config
✅ `web/VERCEL_DEPLOYMENT.md` - Full guide

---

**Ready to deploy! 🚀**
