#!/usr/bin/env python3
"""
Test pipeline through API to reproduce the error
"""
import sys
import requests
import time
import json

sys.path.insert(0, '.')

# Create a test token
from app.auth.jwt_utils import create_access_token

token = create_access_token({"sub": "admin"})
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("="*70)
print("TESTING PIPELINE VIA API")
print("="*70)

# Test 1: Check if server is responding
print("\n[1] Testing server health...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Get current pipeline status
print("\n[2] Getting current pipeline status...")
try:
    response = requests.get("http://localhost:8000/admin/pipeline/status", headers=headers)
    print(f"    Status: {response.status_code}")
    status = response.json()
    print(f"    Current state: {status.get('state')}")
    print(f"    Error message: {status.get('error_message')}")
    print(f"    Full status: {json.dumps(status, indent=2)}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Try to start the pipeline
print("\n[3] Starting pipeline...")
try:
    payload = {
        "urls": ["https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"]
    }
    response = requests.post(
        "http://localhost:8000/admin/pipeline/run",
        headers=headers,
        json=payload
    )
    print(f"    Status: {response.status_code}")
    print(f"    Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Monitor pipeline status
print("\n[4] Monitoring pipeline status...")
for i in range(10):
    time.sleep(2)
    try:
        response = requests.get("http://localhost:8000/admin/pipeline/status", headers=headers)
        status = response.json()
        state = status.get('state')
        step = status.get('current_step')
        progress = status.get('progress', 0)
        error = status.get('error_message')

        print(f"    [{i+1}] State: {state}, Step: {step}, Progress: {progress}%")

        if error:
            print(f"    ERROR MESSAGE: {error}")
            break

        if state in ['completed', 'error']:
            print(f"    Final state: {state}")
            if state == 'error':
                print(f"    Error: {error}")
            break
    except Exception as e:
        print(f"    ERROR: {e}")
        break

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
