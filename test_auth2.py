"""Test register endpoint and print body"""
import urllib.request
import urllib.error
import json

url = "https://backend-hydrocare.vercel.app/api/auth/register"
data = {
    "username": "test1234",
    "password": "password123",
    "name": "Test User",
    "age": 25,
    "gender": "male",
    "weight_kg": 70,
    "height_cm": 170,
    "activity": "moderate",
    "city": "Bandar Lampung"
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Status: {resp.status}")
        print(f"Response: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Response: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
