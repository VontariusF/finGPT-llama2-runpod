# FinGPT RunPod Serverless - Usage Guide

Comprehensive guide for using your deployed FinGPT endpoint.

## Table of Contents

- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Request Formats](#request-formats)
- [Response Formats](#response-formats)
- [Python Examples](#python-examples)
- [cURL Examples](#curl-examples)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)

## Authentication

All requests require your RunPod API key in the Authorization header:

```
Authorization: Bearer YOUR_RUNPOD_API_KEY
```

Get your API key from: https://www.runpod.io/console/user/settings

## API Endpoints

### RunPod Native (Recommended)

**Synchronous (waits for result):**
```
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync
```

**Asynchronous (returns job ID):**
```
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/run
GET  https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{JOB_ID}
```

### OpenAI-Compatible (Experimental)

```
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/chat/completions
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/completions
GET  https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/models
```

**Note**: OpenAI endpoints may timeout on cold starts. Use RunPod native format for production.

## Request Formats

### RunPod Native Format

```json
{
  "input": {
    "prompt": "Your question or text here",
    "max_tokens": 200,
    "temperature": 0.7
  }
}
```

**Parameters:**
- `prompt` (string, required): Input text for the model
- `max_tokens` (integer, optional, default: 256): Maximum tokens to generate
- `temperature` (float, optional, default: 0.7): Sampling temperature (0.0-2.0)

### OpenAI Chat Format

```json
{
  "model": "fingpt-mt-llama3-8b-lora-gguf",
  "messages": [
    {"role": "user", "content": "Your message here"}
  ],
  "max_tokens": 150,
  "temperature": 0.7
}
```

### OpenAI Completion Format

```json
{
  "model": "fingpt-mt-llama3-8b-lora-gguf",
  "prompt": "Your prompt here",
  "max_tokens": 150,
  "temperature": 0.7
}
```

## Response Formats

### RunPod Native Response

```json
{
  "id": "job-id-here",
  "status": "COMPLETED",
  "delayTime": 22041,
  "executionTime": 68,
  "output": {
    "status": "success",
    "output": "Generated text here...",
    "model": "fingpt-mt-llama3-8b-lora-gguf"
  },
  "workerId": "worker-id"
}
```

### OpenAI Chat Response

```json
{
  "id": "uuid-here",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "fingpt-mt-llama3-8b-lora-gguf",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Generated text here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {}
}
```

## Python Examples

### Basic Synchronous Request

```python
import requests
import os

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "prompt": "Analyze the sentiment: Tech stocks surge on AI breakthrough.",
            "max_tokens": 200,
            "temperature": 0.7
        }
    },
    timeout=120
)

result = response.json()

if result['status'] == 'COMPLETED':
    print(result['output']['output'])
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

### Asynchronous Request with Status Polling

```python
import requests
import time
import os

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Submit job
response = requests.post(
    f"{BASE_URL}/run",
    headers=headers,
    json={
        "input": {
            "prompt": "What are the key financial metrics for valuation?",
            "max_tokens": 250
        }
    }
)

job_id = response.json()['id']
print(f"Job submitted: {job_id}")

# Poll for result
while True:
    status_response = requests.get(
        f"{BASE_URL}/status/{job_id}",
        headers=headers
    )

    result = status_response.json()
    status = result['status']

    print(f"Status: {status}")

    if status == 'COMPLETED':
        print(f"Output: {result['output']['output']}")
        break
    elif status == 'FAILED':
        print(f"Error: {result.get('error')}")
        break

    time.sleep(2)
```

### Using OpenAI Python Client

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("RUNPOD_API_KEY"),
    base_url=f"https://api.runpod.ai/v2/{os.getenv('ENDPOINT_ID')}/openai/v1"
)

# Note: This may timeout on cold starts
try:
    response = client.chat.completions.create(
        model="fingpt-mt-llama3-8b-lora-gguf",
        messages=[
            {"role": "user", "content": "Explain P/E ratio in simple terms."}
        ],
        max_tokens=150,
        temperature=0.7,
        timeout=120
    )

    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
    print("Try using RunPod native format for more reliable results")
```

### Batch Processing

```python
import requests
import os
from concurrent.futures import ThreadPoolExecutor

ENDPOINT_ID = os.getenv("ENDPOINT_ID")
API_KEY = os.getenv("RUNPOD_API_KEY")

prompts = [
    "Analyze: Market correction underway.",
    "Analyze: Fed signals rate hike.",
    "Analyze: Earnings beat expectations."
]

def process_prompt(prompt):
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"input": {"prompt": prompt, "max_tokens": 100}},
        timeout=120
    )
    return response.json()['output']['output']

# Process in parallel (RunPod will auto-scale workers)
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))

for prompt, result in zip(prompts, results):
    print(f"\nPrompt: {prompt}")
    print(f"Analysis: {result}")
```

## cURL Examples

### Basic Request

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "What is the difference between bull and bear markets?",
      "max_tokens": 200,
      "temperature": 0.7
    }
  }'
```

### With Environment Variables

```bash
export RUNPOD_API_KEY="your_key_here"
export ENDPOINT_ID="your_endpoint_id"

curl -X POST "https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "input": {
    "prompt": "Explain what a stock dividend is.",
    "max_tokens": 150
  }
}
EOF
```

### Check Job Status

```bash
# Submit async job
JOB_ID=$(curl -X POST "https://api.runpod.ai/v2/${ENDPOINT_ID}/run" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Test"}}' | jq -r '.id')

# Check status
curl "https://api.runpod.ai/v2/${ENDPOINT_ID}/status/${JOB_ID}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"
```

## Best Practices

### Prompt Engineering for FinGPT

**Good prompts:**
```
"Analyze the sentiment of this headline: Tech stocks rally 10%."
"What are the key indicators for a recession?"
"Explain the impact of rising interest rates on bonds."
```

**Avoid:**
- Very short prompts (may return empty results)
- Multi-turn conversations without context
- Extremely long prompts (context limit: 4096 tokens)

### Temperature Settings

- **0.1-0.3**: Focused, deterministic (good for factual analysis)
- **0.7-0.9**: Balanced, creative (good for explanations)
- **1.0-2.0**: Very creative, less predictable

### Token Management

- Start with `max_tokens: 150-200` for most queries
- Increase for detailed explanations
- Monitor costs (longer outputs = more tokens = higher cost)

### Timeout Handling

```python
import requests

try:
    response = requests.post(url, json=data, timeout=120)
    # Cold start can take 30-60 seconds
except requests.exceptions.Timeout:
    print("Request timed out - endpoint may be cold starting")
    print("Try again in 30 seconds")
```

## Error Handling

### Common Errors

**Job Status: FAILED**
```json
{
  "status": "FAILED",
  "error": "Cannot connect to llama.cpp server"
}
```
*Solution*: Worker may be restarting. Wait 30s and retry.

**Empty Output**
```json
{
  "output": ""
}
```
*Solution*: Increase `max_tokens` or rephrase prompt.

**Timeout**
```
requests.exceptions.Timeout
```
*Solution*: Increase timeout to 120-300s for cold starts.

### Retry Logic

```python
import requests
import time

def call_endpoint_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=120)
            result = response.json()

            if result['status'] == 'COMPLETED':
                return result['output']['output']
            elif result['status'] == 'FAILED':
                raise Exception(f"Job failed: {result.get('error')}")

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 30
                print(f"Timeout - waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception("Max retries exceeded")
```

## Cost Optimization

1. **Use async endpoints** for batch processing (parallel execution)
2. **Set idle timeout low** (5s) to minimize idle costs
3. **Limit max_tokens** to what you actually need
4. **Cache common responses** in your application
5. **Monitor usage** via RunPod dashboard

## Rate Limits

RunPod Serverless auto-scales based on:
- **Max Workers**: Set in endpoint config (e.g., 1-3)
- **Queue depth**: Jobs queue when all workers busy
- **Account limits**: Check RunPod dashboard

## Support

- Test scripts included in repo
- Check RunPod logs for detailed errors
- Review [README.md](README.md) for troubleshooting
- RunPod Discord: https://discord.gg/runpod
