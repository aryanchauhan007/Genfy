import requests
import json

try:
    print("Testing Root...")
    r = requests.get("http://127.0.0.1:8000/")
    print(f"Root Status: {r.status_code}")
    print(r.text)

    print("\nTesting Signup Endpoint...")
    payload = {"email": "test_debug@example.com", "password": "password123"}
    headers = {"Content-Type": "application/json"}
    r = requests.post("http://127.0.0.1:8000/api/auth/signup", json=payload, headers=headers)
    print(f"Signup Status: {r.status_code}")
    print(r.text)

except Exception as e:
    print(f"Connection Failed: {e}")
