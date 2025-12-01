#!/usr/bin/env python3
"""
Test Regular Format - FinGPT RunPod Serverless
Comprehensive test using RunPod's native API format (recommended).
Shows full request/response details including timing metrics.
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

print("Testing FinGPT with Regular RunPod Format")
print("=" * 60)

# Test with runsync for synchronous response
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

test_prompt = "Analyze the sentiment of this headline: Tech stocks rally on positive earnings reports."

payload = {
    "input": {
        "prompt": test_prompt,
        "max_tokens": 150,
        "temperature": 0.7
    }
}

print(f"\nEndpoint: {ENDPOINT_ID}")
print(f"URL: {url}")
print(f"Prompt: {test_prompt}")
print("\nSending request (may take 60+ seconds for cold start)...")
print("-" * 60)

try:
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=300
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nFull Response:")
        print(json.dumps(result, indent=2))

        if result.get("status") == "COMPLETED":
            output = result.get("output", {})
            print(f"\n{'='*60}")
            print("MODEL OUTPUT:")
            print(f"{'='*60}")
            print(output.get("output", "No output"))
            print(f"{'='*60}")
            print(f"Model: {output.get('model')}")
            print(f"Execution Time: {result.get('executionTime')}ms")
            print(f"Delay Time: {result.get('delayTime')}ms")
        else:
            print(f"\nJob Status: {result.get('status')}")
            if result.get("error"):
                print(f"Error: {result.get('error')}")
    else:
        print(f"Error Response: {response.text}")

except requests.exceptions.Timeout:
    print("\nTimeout - worker may still be starting up. Try again in a minute.")
except Exception as e:
    print(f"\nError: {e}")
