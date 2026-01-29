"""Test login with server output visible."""
import subprocess
import time
import os
import requests
import sys
import threading

def tail_output(proc):
    """Print server output in real-time."""
    for line in iter(proc.stdout.readline, ''):
        print(line, end='')

# Start server
print("Starting server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:application", 
     "--host", "0.0.0.0", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Start thread to print output
output_thread = threading.Thread(target=tail_output, args=(server_process,), daemon=True)
output_thread.start()

# Wait for server
print("\nWaiting for server to start...")
time.sleep(5)

try:
    print("\n" + "="*70)
    print("Testing login endpoint...")
    print("="*70)
    
    data = {
        "email": "test_with_logs@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    base_url = os.getenv("BACKEND_URL", "")
    response = requests.post(f"{base_url}/auth/login", json=data, timeout=30)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response: {response.text}")
    
    time.sleep(2)  # Give time to see logs
    
except Exception as e:
    print(f"\nException: {e}")
finally:
    print("\n" + "="*70)
    print("Stopping server...")
    print("="*70)
    server_process.terminate()
    server_process.wait()
