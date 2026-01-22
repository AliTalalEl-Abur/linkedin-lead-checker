#!/bin/bash
# Render Free Web Service - Pre-deployment Validation Script
# Run this locally before pushing to Render

set -e

echo "🔍 Render Free Web Service Validation"
echo "====================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
echo "  Python $python_version"

# Check requirements.txt exists
echo "✓ Checking requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "  ❌ ERROR: requirements.txt not found"
    exit 1
fi
echo "  ✓ requirements.txt found"

# Check app/main.py exists
echo "✓ Checking app/main.py..."
if [ ! -f "app/main.py" ]; then
    echo "  ❌ ERROR: app/main.py not found"
    exit 1
fi
echo "  ✓ app/main.py found"

# Check health endpoint exists
echo "✓ Checking health endpoint..."
if grep -q "def healthcheck" app/api/routes/health.py; then
    echo "  ✓ Health check endpoint found"
else
    echo "  ❌ ERROR: Health check endpoint not found"
    exit 1
fi

# Check for app creation
echo "✓ Checking FastAPI app creation..."
if grep -q "app = create_app()" app/main.py; then
    echo "  ✓ FastAPI app properly created"
else
    echo "  ⚠️  WARNING: Check that app is properly created in app/main.py"
fi

# Validate environment setup
echo ""
echo "📋 Environment Variables (Render Dashboard):"
echo "  REQUIRED:"
echo "    □ DATABASE_URL (from Render Postgres)"
echo "    □ JWT_SECRET_KEY (run: openssl rand -hex 32)"
echo "    □ ENV=prod"
echo ""
echo "  RECOMMENDED:"
echo "    □ OPENAI_ENABLED=false"
echo "    □ CORS_ALLOW_ORIGINS=<your-domain>"
echo ""
echo "  OPTIONAL (leave empty if not needed):"
echo "    □ OPENAI_API_KEY"
echo "    □ STRIPE_API_KEY"
echo "    □ STRIPE_WEBHOOK_SECRET"
echo "    □ STRIPE_PRICE_PRO_ID"
echo "    □ STRIPE_PRICE_TEAM_ID"

# Check build command
echo ""
echo "🔨 Build Command:"
echo "  pip install -r requirements.txt"

# Check start command
echo ""
echo "🚀 Start Command:"
echo "  uvicorn app.main:app --host 0.0.0.0 --port \$PORT --proxy-headers"

# Summary
echo ""
echo "✅ Pre-deployment validation complete!"
echo ""
echo "Next steps:"
echo "  1. Push to GitHub"
echo "  2. Go to https://render.com"
echo "  3. Create new Web Service"
echo "  4. Set environment variables (see above)"
echo "  5. Render will deploy automatically"
echo ""
echo "To verify after deploy:"
echo "  curl https://your-service.onrender.com/health"
echo "  Expected: {\"ok\": true, \"env\": \"prod\"}"
