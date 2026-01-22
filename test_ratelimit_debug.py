"""Debug rate limiting with server logs."""
import subprocess
import time
import requests
import sys
import threading
import os

# Remove DATABASE_URL
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

def tail_output(proc):
    """Print server output in real-time."""
    for line in iter(proc.stdout.readline, ''):
        print(line, end='')

# Start server
print("Starting server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:application", 
     "--host", "127.0.0.1", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    env={**os.environ, 'DATABASE_URL': ''}
)

# Start thread to print output
output_thread = threading.Thread(target=tail_output, args=(server_process,), daemon=True)
output_thread.start()

# Wait for server
time.sleep(5)

try:
    print("\n" + "="*70)
    print("Creating user...")
    data = {"email": "test_ratelimit_debug@example.com", "password": "pass", "full_name": "Test"}
    response = requests.post("http://127.0.0.1:8001/auth/login", json=data, timeout=30)
    token = response.json()["access_token"]
    print(f"✓ User created, token: {token[:20]}...")
    
    print("\n" + "="*70)
    print("First analysis...")
    profile = {"profile_extract": {
        "name": "Test", "headline": "Test", "about": "Test",
        "current_company": "Test", "current_position": "Test", "location": "Test"
    }}
    response = requests.post(
        "http://127.0.0.1:8001/analyze/linkedin",
        headers={"Authorization": f"Bearer {token}"},
        json=profile,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    
    print("\n" + "="*70)
    print("Second analysis immediately (should fail with 429)...")
    response = requests.post(
        "http://127.0.0.1:8001/analyze/linkedin",
        headers={"Authorization": f"Bearer {token}"},
        json=profile,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    time.sleep(2)  # Give time to see logs
    
except Exception as e:
    print(f"\nException: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n" + "="*70)
    print("Stopping server...")
    server_process.terminate()
    server_process.wait()
