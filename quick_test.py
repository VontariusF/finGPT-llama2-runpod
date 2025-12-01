#!/usr/bin/env python3
"""
Quick Test - FinGPT RunPod Serverless
Minimal single-request test for quick verification.
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")
URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/chat/completions"

print(f"Testing endpoint: {ENDPOINT_ID}")
print("Sending request... (first request may take 30-60s for cold start)\n")

response = requests.post(
    URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "fingpt-mt-llama3-8b-lora-gguf",
        "messages": [{"role": "user", "content": "What is sentiment analysis in finance?"}],
        "max_tokens": 100
    },
    timeout=120
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()['choices'][0]['message']['content']}")
else:
    print(f"Error: {response.text}")
