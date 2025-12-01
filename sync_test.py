#!/usr/bin/env python3
"""
Sync Test - FinGPT RunPod Serverless
Test synchronous execution with /runsync endpoint.
Waits for result (may take 60+ seconds on cold start).
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

print(f"Testing endpoint: {ENDPOINT_ID} with RUNSYNC")
print("This will wait for the worker to start and process the job...")
print("-" * 60)

url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
payload = {
    "input": {
        "test": "hello from runsync"
    }
}

print(f"Sending request to: {url}")
print("This may take 60+ seconds for cold start...")

try:
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=300  # 5 minute timeout for cold start
    )

    print(f"\nStatus: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

except requests.exceptions.Timeout:
    print("\nTimeout after 5 minutes - worker may be stuck starting up")
except Exception as e:
    print(f"\nError: {e}")
