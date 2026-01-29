"""Start backend and Stripe CLI for development."""
import subprocess
import sys
import time

print("=" * 60)
print("LinkedIn Lead Checker - Development Environment")
print("=" * 60)

# Start backend server
print("\n🚀 Starting FastAPI backend on BACKEND_URL...")
backend_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", 
     "--host", "0.0.0.0", "--port", "8001", "--reload"],
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
)

time.sleep(2)

print("\n✅ Backend started successfully!")
print("   URL: BACKEND_URL")
print("   Docs: BACKEND_URL/docs")
print("   Health: BACKEND_URL/health")

print("\n" + "=" * 60)
print("📋 Next Steps:")
print("=" * 60)
print("\n1. Open the dashboard:")
print("   → Open web/dashboard.html in your browser")
print("\n2. Start Stripe CLI (in another terminal):")
print("   → stripe listen --forward-to BACKEND_URL/billing/webhook")
print("\n3. Test the new pricing system:")
print("   → FREE: 3 analyses lifetime (no reset)")
print("   → PRO: $19/mo with 100 analyses/week")
print("   → TEAM: $39/mo with 300 analyses/week")
print("   → Rate limit: 30 seconds between analyses")
print("\n4. Test Stripe checkout:")
print("   → Use test card: 4242 4242 4242 4242")
print("\n5. Press CTRL+C to stop the server")
print("=" * 60)

try:
    backend_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Shutting down...")
    backend_process.terminate()
    backend_process.wait()
    print("   ✅ Server stopped.")
