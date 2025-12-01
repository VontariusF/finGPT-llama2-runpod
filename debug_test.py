#!/usr/bin/env python3
"""
Debug Test - FinGPT RunPod Serverless
Debug tool to inspect endpoint responses and routing.
Tests both direct API and OpenAI paths.
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

# Test 1: Direct RunPod API (non-OpenAI path)
print("Test 1: Direct RunPod Serverless API")
print("-" * 60)
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
payload = {
    "input": {
        "test": "hello"
    }
}

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=120
)

print(f"URL: {url}")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: OpenAI path
print("\n\nTest 2: OpenAI-compatible path")
print("-" * 60)
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/models"

response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
    },
    timeout=60
)

print(f"URL: {url}")
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
