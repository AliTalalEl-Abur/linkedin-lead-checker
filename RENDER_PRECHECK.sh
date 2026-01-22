#!/bin/bash
# Quick Render Deployment Checklist
# Run this before pushing to GitHub

echo "🔍 Render Free Deployment Pre-Check"
echo "===================================="
echo ""

# Check Python
echo "✓ Python version"
python --version

# Check requirements.txt
echo "✓ requirements.txt exists"
if [ ! -f "requirements.txt" ]; then
    echo "  ❌ NOT FOUND"
    exit 1
fi
echo "  ✓ Found"

# Check FastAPI app
echo "✓ app/main.py exists"
if [ ! -f "app/main.py" ]; then
    echo "  ❌ NOT FOUND"
    exit 1
fi
echo "  ✓ Found"

# Check health endpoint
echo "✓ health endpoint exists"
if [ ! -f "app/api/routes/health.py" ]; then
    echo "  ❌ NOT FOUND"
    exit 1
fi
echo "  ✓ Found"

# Check create_app function
echo "✓ create_app() exists in main.py"
if ! grep -q "def create_app" app/main.py; then
    echo "  ❌ NOT FOUND"
    exit 1
fi
echo "  ✓ Found"

# Check app instance
echo "✓ app instance created"
if ! grep -q "app = create_app" app/main.py; then
    echo "  ❌ NOT FOUND - app must be: app = create_app()"
    exit 1
fi
echo "  ✓ Found"

echo ""
echo "📋 Render Configuration:"
echo "  Build Command: pip install -r requirements.txt"
echo "  Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT --proxy-headers"
echo "  Health Check: GET /health"

echo ""
echo "🔐 Required Environment Variables (set in Render Dashboard):"
echo "  1. DATABASE_URL (copy from Render Postgres)"
echo "  2. JWT_SECRET_KEY (generate: openssl rand -hex 32)"
echo "  3. ENV=prod"

echo ""
echo "🧪 Testing (local):"
echo "  1. Install: pip install -r requirements.txt"
echo "  2. Run: python -c 'from app.main import create_app; app = create_app()'"
echo "  3. Start: uvicorn app.main:app --reload"
echo "  4. Test health: curl http://localhost:8000/health"

echo ""
echo "✅ All checks passed!"
echo ""
echo "Next: Push to GitHub → Render auto-deploys"
