# LinkedIn Lead Checker - Landing Page

Professional B2B landing page for the LinkedIn Lead Checker Chrome Extension.

## 🎯 Purpose

Validate interest in the product before full development. No payments, no real AI backend required yet.

## 🚀 Quick Start

### Install Dependencies

```bash
cd web
npm install
```

### Run Development Server

```bash
npm run dev
```

Open NEXT_PUBLIC_SITE_URL to see the landing page.

### Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
web/
├── pages/
│   ├── index.js          # Main landing page
│   └── _app.js           # Next.js app wrapper
├── components/
│   ├── Button.js         # Reusable button component
│   ├── Section.js        # Section wrapper component
│   └── PricingCard.js    # Pricing card component
├── styles/
│   └── globals.css       # Global styles with Tailwind
├── tailwind.config.js    # Tailwind configuration
├── postcss.config.js     # PostCSS configuration
└── package.json          # Dependencies
```

## 🎨 Sections Included

1. **Hero Section** - Main headline, subheadline, and CTAs
2. **Problem Section** - Pain points the product solves
3. **Solution Section** - How the extension helps
4. **How It Works** - 3-step process
5. **Social Proof** - Honest early user statement
6. **Pricing** - Free preview + Pro (coming soon)
7. **Final CTA** - Email capture for early access
8. **Footer** - Simple links and disclaimer

## ✅ What's Working

- ✅ Fully responsive design
- ✅ Tailwind CSS styling
- ✅ Component-based architecture
- ✅ Email capture (logs to console)
- ✅ Smooth scrolling
- ✅ Professional B2B tone
- ✅ No fake testimonials or logos

## 🔧 Customization

### Colors

Edit [tailwind.config.js](tailwind.config.js) to change the primary color scheme:

```javascript
colors: {
  primary: {
    // Your custom colors here
  },
}
```

### Content

All content is in [pages/index.js](pages/index.js). Edit the text, titles, and descriptions directly.

### Email Collection

Currently logs to console. To connect to a real email service:

1. Add your service (e.g., Mailchimp, ConvertKit, custom backend)
2. Update the `handleEarlyAccess` function in `index.js`

Example:

```javascript
const handleEarlyAccess = async (e) => {
  e.preventDefault();
  if (email && email.includes('@')) {
    // Send to your email service
    await fetch('/api/subscribe', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
    setSubmitted(true);
  }
};
```

## 📝 Notes

- No backend required - static page only
- No Stripe integration on this page
- No authentication needed
- Simple email validation (frontend only)
- Ready to deploy to Vercel, Netlify, or any static host

## 🚢 Deployment

### Vercel (Recommended for Next.js)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Upload the .next folder
```

### Static Export

For pure static hosting:

1. Update `next.config.js`:
```javascript
module.exports = {
  output: 'export',
}
```

2. Build:
```bash
npm run build
```

3. Deploy the `out/` folder

## 🎯 Next Steps

Once you validate interest:

1. Connect email capture to a real service
2. Add analytics (Google Analytics, Plausible)
3. Create the actual Chrome extension
4. Build the AI backend
5. Implement Stripe for payments
6. Add the dashboard and authentication

## 📧 Contact

For questions or support, update the footer links with your actual contact information.
