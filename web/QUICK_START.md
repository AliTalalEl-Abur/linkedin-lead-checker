# Quick Start Commands

## 🚀 First Time Setup

# Navigate to web folder
cd web

# Install all dependencies
npm install

# Start development server
npm run dev

# Open NEXT_PUBLIC_SITE_URL in your browser

## 🔧 Daily Development

# Start dev server
npm run dev

# Build for production
npm run build

# Run production build locally
npm start

# Check for linting issues
npm run lint

## 📦 Deployment

# Deploy to Vercel
npm install -g vercel
vercel

# Build static export
npm run build

## 🧹 Cleanup

# Remove node_modules and .next
rm -rf node_modules .next

# Fresh install
npm install

# Clear Next.js cache
rm -rf .next

## 💡 Quick Tips

# Check if port 3000 is in use
netstat -ano | findstr :3000

# Run on different port
$env:PORT=3001; npm run dev

# Open in default browser after starting
start NEXT_PUBLIC_SITE_URL
