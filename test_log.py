"""Test water log endpoint"""
import urllib.request
import urllib.error
import json

url = "http://localhost:8000/api/history/log"
data = {
    "amount_ml": 250,
    "log_date": "2026-04-26",
    "note": ""
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

    
