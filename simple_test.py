#!/usr/bin/env python3
"""
Simple Test - FinGPT RunPod Serverless
Quick test with a basic prompt to verify endpoint is working.
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

payload = {
    "input": {
        "prompt": "Question: What is financial sentiment analysis?\nAnswer:",
        "max_tokens": 200,
        "temperature": 0.8
    }
}

print("Sending simple prompt with more tokens...")
print(f"Prompt: {payload['input']['prompt']}")

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=120
)

result = response.json()
print(f"\nStatus: {result.get('status')}")
print(f"Output: {result.get('output')}")

if result.get('output'):
    print(f"\nGenerated text:\n{result['output'].get('output')}")
