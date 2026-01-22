"""Test rápido de API sin librerías externas"""
import http.client
import json

def test_health():
    conn = http.client.HTTPConnection("127.0.0.1", 8001)
    try:
        conn.request("GET", "/health")
        response = conn.getresponse()
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode()}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_health()
