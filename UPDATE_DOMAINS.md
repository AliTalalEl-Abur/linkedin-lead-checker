# 🔧 Post-Deployment: Update Domain Placeholders

After deploying to Vercel, you'll receive a URL like:
```
https://linkedin-lead-checker-web.vercel.app
```

**You MUST update these placeholders with your actual domain:**

---

## 1. Update SEO Metadata

**File**: `web/pages/index.js`

**Find** (lines 9-13):
```javascript
const META = {
  title: 'LinkedIn Lead Checker - AI-Powered Lead Qualification',
  description: 'Qualify LinkedIn leads in seconds with AI analysis...',
  url: 'https://your-domain.com', // ⚠️ CHANGE THIS
  ogImage: 'https://your-domain.com/og-image.jpg' // ⚠️ CHANGE THIS
};
```

**Replace with**:
```javascript
const META = {
  title: 'LinkedIn Lead Checker - AI-Powered Lead Qualification',
  description: 'Qualify LinkedIn leads in seconds with AI analysis...',
  url: 'https://linkedin-lead-checker-web.vercel.app', // ✅ YOUR VERCEL URL
  ogImage: 'https://linkedin-lead-checker-web.vercel.app/og-image.jpg' // ✅ YOUR VERCEL URL
};
```

---

## 2. Update Robots.txt

**File**: `web/public/robots.txt`

**Find**:
```
Sitemap: https://your-domain.com/sitemap.xml
```

**Replace with**:
```
Sitemap: https://linkedin-lead-checker-web.vercel.app/sitemap.xml
```

---

## 3. Update Sitemap.xml

**File**: `web/public/sitemap.xml`

**Find and replace ALL occurrences** (4 total):
```xml
<loc>https://your-domain.com/</loc>
<loc>https://your-domain.com/login</loc>
<loc>https://your-domain.com/upgrade</loc>
<loc>https://your-domain.com/dashboard</loc>
```

**Replace with**:
```xml
<loc>https://linkedin-lead-checker-web.vercel.app/</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/login</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/upgrade</loc>
<loc>https://linkedin-lead-checker-web.vercel.app/dashboard</loc>
```

---

## 4. Commit and Redeploy

```bash
cd web/
git add pages/index.js public/robots.txt public/sitemap.xml
git commit -m "Update domain URLs to Vercel deployment"
git push origin main
```

Vercel will automatically redeploy with the updated URLs.

---

## 5. Verify Changes

After redeployment:

✅ Visit homepage → View page source → Check `<meta property="og:url">`
✅ Visit `/robots.txt` → Check sitemap URL
✅ Visit `/sitemap.xml` → Check all URLs
✅ Test social sharing (Facebook/LinkedIn) → Check preview image

---

## Optional: Add Custom Domain

If you have a custom domain (e.g., `linkedinleadchecker.com`):

1. **Add domain in Vercel**:
   - Go to Project Settings → Domains
   - Add `linkedinleadchecker.com` and `www.linkedinleadchecker.com`

2. **Configure DNS** (provided by your domain registrar):
   ```
   A     @     76.76.21.21
   CNAME www   cname.vercel-dns.com
   ```

3. **Wait for DNS propagation** (5-30 minutes)

4. **Update all URLs again**:
   - Replace `linkedin-lead-checker-web.vercel.app`
   - With `linkedinleadchecker.com`
   - In: index.js, robots.txt, sitemap.xml

5. **Commit and push**

---

## Need to Update Later?

Use this search/replace pattern:

**Old domain**:
```
linkedin-lead-checker-web.vercel.app
```

**New domain**:
```
your-custom-domain.com
```

**Files to update**:
- `web/pages/index.js` (2 occurrences)
- `web/public/robots.txt` (1 occurrence)
- `web/public/sitemap.xml` (4 occurrences)

---

**Total: 7 URLs to update** ✅
