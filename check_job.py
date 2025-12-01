#!/usr/bin/env python3
"""
Check Job Status - FinGPT RunPod Serverless
Check status of a specific job by ID, or submit a test job.
Usage: python check_job.py [job_id]
Requires: ENDPOINT_ID and RUNPOD_API_KEY in .env file
"""

import os
import requests
from dotenv import load_dotenv
import json
import sys

load_dotenv()

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

if len(sys.argv) > 1:
    job_id = sys.argv[1]
else:
    print("Usage: python check_job.py <job_id>")
    print("Or run without args to submit a test job and check it")

    # Submit a test job
    print("Submitting test job...")
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={"input": {"test": "hello"}},
        timeout=30
    )

    result = response.json()
    job_id = result.get("id")
    print(f"Job ID: {job_id}")
    print()

# Check job status
print(f"Checking status for job: {job_id}")
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"

response = requests.get(
    url,
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=30
)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
