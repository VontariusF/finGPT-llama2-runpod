#!/usr/bin/env python3
"""
Test OpenAI Format - FinGPT RunPod Serverless
Tests OpenAI-compatible endpoints (/openai/v1/*).
Note: These endpoints are experimental and may timeout.
Use test_regular.py for production testing.
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
MODEL_NAME = os.getenv("MODEL_NAME", "fingpt-mt-llama3-8b-lora-gguf")

if not RUNPOD_API_KEY or not ENDPOINT_ID:
    print("Error: RUNPOD_API_KEY and ENDPOINT_ID must be set in .env file")
    exit(1)

# RunPod serverless endpoint URL
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1"

print(f"Testing FinGPT endpoint: {ENDPOINT_ID}")
print(f"Base URL: {BASE_URL}")
print("-" * 60)

# Test 1: List models
print("\n1. Testing /v1/models endpoint...")
try:
    response = requests.get(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Chat completion
print("\n2. Testing /v1/chat/completions endpoint...")
print("Prompt: 'Analyze this financial headline: Tesla stock rises 5% on strong earnings.'")
print("\nNote: First request will have cold start (~30-60 seconds)...")

try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze this financial headline: Tesla stock rises 5% on strong earnings."
                }
            ],
            "max_tokens": 150,
            "temperature": 0.7
        },
        timeout=120  # Allow time for cold start
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nModel: {result.get('model')}")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"Error Response: {response.text}")

except requests.exceptions.Timeout:
    print("Request timed out. The endpoint might still be starting up (cold start).")
    print("Try running the script again in a minute.")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Text completion
print("\n3. Testing /v1/completions endpoint...")
print("Prompt: 'The market outlook for 2025 is'")

try:
    response = requests.post(
        f"{BASE_URL}/completions",
        headers={
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_NAME,
            "prompt": "The market outlook for 2025 is",
            "max_tokens": 100,
            "temperature": 0.7
        },
        timeout=60
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nModel: {result.get('model')}")
        print(f"Completion: {result['choices'][0]['text']}")
    else:
        print(f"Error Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "-" * 60)
print("Testing complete!")
