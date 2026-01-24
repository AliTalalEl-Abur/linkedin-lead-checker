# Deployment Guide: Next.js Landing to Vercel

## ✅ Production Readiness Checklist

### Configuration Files
- ✅ `.env.example` - Environment variables template
- ✅ `vercel.json` - Vercel deployment configuration
- ✅ `next.config.js` - Next.js production settings
- ✅ `public/robots.txt` - SEO robots configuration
- ✅ `public/sitemap.xml` - Sitemap for search engines

### Code Changes
- ✅ Removed hardcoded localhost references
- ✅ Uses `NEXT_PUBLIC_API_URL` from environment
- ✅ Dynamic checkout return URL (uses `window.location.origin`)
- ✅ SEO metadata (title, description, Open Graph, Twitter Cards)
- ✅ Security headers configured in vercel.json

---

## 🚀 Deployment Steps

### 1. Prerequisites
- GitHub/GitLab repository with the `web/` folder
- Vercel account (free tier works)
- Backend deployed on Render

### 2. Push to Git Repository
```bash
cd web/
git add .
git commit -m "Prepare Next.js for production"
git push origin main
```

### 3. Deploy to Vercel

#### Option A: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from web/ directory
cd web/
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set project name: linkedin-lead-checker-web
# - Select root directory: ./
# - Override build settings? No
```

#### Option B: Vercel Dashboard
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. **Root Directory**: Select `web` folder
4. **Framework Preset**: Next.js (auto-detected)
5. Click "Deploy"

### 4. Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

**Production:**
```
NEXT_PUBLIC_API_URL=https://linkedin-lead-checker-api.onrender.com
NEXT_PUBLIC_CHECKOUT_RETURN_URL=https://your-vercel-domain.vercel.app/checkout-result?session_id={CHECKOUT_SESSION_ID}
```

**Preview (optional):**
```
NEXT_PUBLIC_API_URL=https://linkedin-lead-checker-api-preview.onrender.com
```

**Development:**
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 5. Update Domain-Specific Files

After deployment, update these files with your actual domain:

**`web/pages/index.js`** (line 9-13):
```javascript
const META = {
  title: 'LinkedIn Lead Checker - AI-Powered Lead Qualification',
  description: 'Qualify LinkedIn leads in seconds with AI analysis...',
  url: 'https://your-vercel-domain.vercel.app', // UPDATE THIS
  ogImage: 'https://your-vercel-domain.vercel.app/og-image.jpg' // UPDATE THIS
};
```

**`web/public/robots.txt`**:
```
Sitemap: https://your-vercel-domain.vercel.app/sitemap.xml
```

**`web/public/sitemap.xml`**:
Replace all `https://your-domain.com` with your actual Vercel domain.

### 6. Trigger Redeployment
After updating domain references:
```bash
git add .
git commit -m "Update production domain"
git push origin main
```
Vercel will auto-deploy on push.

---

## 🔧 Vercel Configuration Details

### Build Settings (Auto-configured)
- **Framework**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`
- **Development Command**: `npm run dev`

### Custom Configuration (`vercel.json`)
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, etc.
- **Static Files**: robots.txt, sitemap.xml
- **Region**: iad1 (US East)

### Performance Features (Automatic)
- ✅ Edge Network (CDN)
- ✅ Automatic HTTPS
- ✅ Image Optimization
- ✅ Incremental Static Regeneration (ISR)
- ✅ Serverless Functions

---

## 📋 Post-Deployment Checklist

### 1. Test Core Functionality
- [ ] Homepage loads correctly
- [ ] Pricing cards display properly
- [ ] CTA buttons work (Install Extension, Login, Upgrade)
- [ ] Authentication flow (login → dashboard)
- [ ] Checkout flow (upgrade → Stripe → callback)

### 2. Verify API Integration
```bash
# Check API connection
curl https://your-vercel-domain.vercel.app/api/health
```

Expected: Should reach backend at `NEXT_PUBLIC_API_URL`

### 3. Test SEO
- [ ] View page source → check `<meta>` tags
- [ ] Visit `/robots.txt` → should load
- [ ] Visit `/sitemap.xml` → should load
- [ ] Use [Google Rich Results Test](https://search.google.com/test/rich-results)

### 4. Performance Testing
- [ ] [PageSpeed Insights](https://pagespeed.web.dev/)
- [ ] [GTmetrix](https://gtmetrix.com/)
- Target: >90 Performance Score

### 5. Cross-Browser Testing
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + mobile)
- [ ] Firefox
- [ ] Edge

---

## 🔍 Troubleshooting

### Issue: "API request failed"
**Cause**: NEXT_PUBLIC_API_URL not set or backend down
**Fix**: 
1. Check Vercel env vars
2. Test backend: `curl https://linkedin-lead-checker-api.onrender.com/health`

### Issue: Stripe checkout redirect fails
**Cause**: NEXT_PUBLIC_CHECKOUT_RETURN_URL incorrect
**Fix**: Update env var with correct Vercel domain

### Issue: Meta tags not showing
**Cause**: Server-side rendering issue
**Fix**: Check Next.js build logs for errors

### Issue: 404 on static files
**Cause**: Files not in `public/` directory
**Fix**: Ensure robots.txt and sitemap.xml are in `web/public/`

---

## 📊 Monitoring

### Vercel Dashboard
- **Analytics**: View page views, unique visitors
- **Logs**: Real-time function logs
- **Deployments**: View history, rollback if needed

### Recommended Tools
- **Sentry**: Error tracking
- **Google Analytics**: User behavior
- **Hotjar**: Heatmaps and session recordings

---

## 🔄 CI/CD Pipeline

Vercel provides automatic deployments:

**Production (main branch)**:
```bash
git push origin main  # Auto-deploys to production
```

**Preview (feature branches)**:
```bash
git checkout -b feature/new-pricing
git push origin feature/new-pricing  # Creates preview deployment
```

Each push generates a unique preview URL for testing.

---

## 🎯 Custom Domain Setup

### 1. Add Domain in Vercel
1. Go to Project Settings → Domains
2. Add your custom domain (e.g., `linkedinleadchecker.com`)
3. Configure DNS (provided by Vercel)

### 2. Update DNS Records
**With Vercel Nameservers** (Recommended):
Point your domain's nameservers to Vercel

**With Custom DNS**:
```
A     @     76.76.21.21
CNAME www   cname.vercel-dns.com
```

### 3. Update Environment Variables
After custom domain is active, update:
- `META.url` in index.js
- robots.txt Sitemap URL
- sitemap.xml URLs

---

## ✅ Production Deployment Complete

Your Next.js landing page is now:
- ✅ Deployed on Vercel's global CDN
- ✅ Automatically scaling
- ✅ HTTPS enabled
- ✅ Connected to your Render backend
- ✅ SEO optimized
- ✅ Ready for custom domain

**Next Steps:**
1. Configure custom domain (optional)
2. Set up analytics (Google Analytics, Plausible)
3. Monitor performance and errors
4. A/B test pricing and CTAs

---

## 📚 Additional Resources

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Custom Domains](https://vercel.com/docs/concepts/projects/domains)
