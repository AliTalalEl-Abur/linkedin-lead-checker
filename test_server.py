"""Run server and test it in separate processes."""
import subprocess
import time
import requests
import sys

# Start server in background
print("Starting server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:application", 
     "--host", "127.0.0.1", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for server to start
time.sleep(3)

try:
    print("\nTesting /health endpoint...")
    response = requests.get("http://127.0.0.1:8001/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("\n✅ Server is working!")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    print("\nStopping server...")
    server_process.terminate()
    server_process.wait()
