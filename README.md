# FinGPT LLaMA2-13B Serverless Deployment (Runpod vLLM)

Deploy the FinGPT LLaMA2-13B sentiment analysis model on Runpod's Serverless vLLM platform with an OpenAI-compatible API.

## Overview

This repository provides a ready-to-deploy configuration for running the [sgzsh269/fingpt-sentiment_llama2-13b_merged](https://huggingface.co/sgzsh269/fingpt-sentiment_llama2-13b_merged) model on Runpod Serverless using vLLM. The deployment creates an OpenAI-compatible REST API endpoint for financial sentiment analysis.

**Key Features:**
- OpenAI-compatible API (chat completions, text completions, model listing)
- Serverless autoscaling with GPU acceleration
- Direct model loading from Hugging Face (no manual conversion needed)
- Optimized vLLM inference engine for high throughput
- Financial sentiment analysis fine-tuned on LLaMA2-13B

## Prerequisites

Before deploying, ensure you have:

1. **Runpod Account**: Sign up at [runpod.io](https://runpod.io)
2. **Runpod API Key**: Generate from your Runpod dashboard (for client-side API calls)
3. **Hugging Face Account & Token**:
   - Create an account at [huggingface.co](https://huggingface.co)
   - Generate an access token with read permissions
   - Accept the LLaMA2 license agreement (required for gated models)
4. **GPU Resources**: Access to Runpod GPU instances (A10G 24GB minimum, A100 40GB recommended)

## Repository Structure

```
finGPT-llama2-runpod/
├── start.sh                # Entrypoint script for the Runpod serverless worker
├── runpod.template.json    # Runpod Serverless template definition (using vLLM)
├── .env.example            # Example environment variables (for secrets like HF token)
└── README.md               # This file
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/finGPT-llama2-runpod.git
cd finGPT-llama2-runpod
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
```env
HF_TOKEN=hf_your_actual_token_here
RUNPOD_API_KEY=your_runpod_api_key_here
```

### 3. Deploy on Runpod

#### Option A: Deploy via Runpod Web Console

1. Log in to your [Runpod Dashboard](https://www.runpod.io/console/serverless)
2. Navigate to **Serverless** → **New Endpoint**
3. Select **Custom** template
4. Configure the endpoint:
   - **Name**: FinGPT-13B-vLLM
   - **Container Image**: `runpod/worker-v1-vllm:v2.2.0stable-cuda12.1.0`
   - **GPU Type**: NVIDIA A10G (24GB) or A100 (40GB recommended)
   - **Container Disk**: 20 GB
   - **Environment Variables**:
     - `MODEL_NAME`: `sgzsh269/fingpt-sentiment_llama2-13b_merged`
     - `HF_TOKEN`: Your Hugging Face token
     - `MAX_MODEL_LEN`: `4096`
     - `GPU_MEMORY_UTILIZATION`: `0.95`
     - `DTYPE`: `float16`
5. Click **Deploy**

#### Option B: Deploy via Runpod CLI

```bash
runpodctl create endpoint \
  --name "FinGPT-13B-vLLM" \
  --image "runpod/worker-v1-vllm:v2.2.0stable-cuda12.1.0" \
  --gpu-type "NVIDIA A10G" \
  --env MODEL_NAME=sgzsh269/fingpt-sentiment_llama2-13b_merged \
  --env HF_TOKEN=$HF_TOKEN \
  --env MAX_MODEL_LEN=4096 \
  --env GPU_MEMORY_UTILIZATION=0.95 \
  --env DTYPE=float16
```

### 4. Wait for Initialization

The first startup will take **5-10 minutes** as Runpod:
- Pulls the vLLM container image
- Downloads the 13B model from Hugging Face (~26 GB)
- Loads the model into GPU memory

Monitor the status in the Runpod dashboard. Once the endpoint shows **Running**, it's ready to accept requests.

### 5. Get Your Endpoint ID

After deployment, note your **Endpoint ID** from the Runpod dashboard. Your API base URL will be:

```
https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1
```

## API Usage

The deployed endpoint provides an OpenAI-compatible API. All requests require your Runpod API key in the `Authorization` header.

### Authentication

Include your Runpod API key in all requests:

```bash
Authorization: Bearer YOUR_RUNPOD_API_KEY
```

### Supported Endpoints

#### 1. Chat Completions (Recommended)

**POST** `/v1/chat/completions`

Generate responses using the chat format. Best for conversational sentiment analysis.

**Example Request (curl):**

```bash
curl https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <RUNPOD_API_KEY>" \
  -d '{
    "model": "sgzsh269/fingpt-sentiment_llama2-13b_merged",
    "messages": [
      {"role": "system", "content": "You are a financial sentiment analysis AI. Classify the sentiment as positive, neutral, or negative."},
      {"role": "user", "content": "Instruction: What is the sentiment of this news? Please choose an answer from {strong negative/moderately negative/mildly negative/neutral/mildly positive/moderately positive/strong positive}.\nInput: Tesla stock surges 15% after record quarterly earnings beat expectations.\nAnswer:"}
    ],
    "temperature": 0.1,
    "max_tokens": 50
  }'
```

**Example Response:**

```json
{
  "id": "cmpl-abc123",
  "object": "chat.completion",
  "created": 1698512345,
  "model": "sgzsh269/fingpt-sentiment_llama2-13b_merged",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "strong positive"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 65,
    "completion_tokens": 3,
    "total_tokens": 68
  }
}
```

**Python Example:**

```python
import openai
import os

# Configure OpenAI client to use Runpod endpoint
openai.api_key = os.getenv("RUNPOD_API_KEY")
openai.api_base = f"https://api.runpod.ai/v2/{os.getenv('ENDPOINT_ID')}/openai/v1"

response = openai.ChatCompletion.create(
    model="sgzsh269/fingpt-sentiment_llama2-13b_merged",
    messages=[
        {"role": "system", "content": "You are a financial sentiment analysis AI."},
        {"role": "user", "content": "Instruction: What is the sentiment of this news? Please choose an answer from {strong negative/moderately negative/mildly negative/neutral/mildly positive/moderately positive/strong positive}.\nInput: Fed announces interest rate hike to combat inflation.\nAnswer:"}
    ],
    temperature=0.1,
    max_tokens=50
)

print(response.choices[0].message.content)
```

#### 2. Text Completions

**POST** `/v1/completions`

Generate completions from a single prompt string.

**Example Request:**

```bash
curl https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <RUNPOD_API_KEY>" \
  -d '{
    "model": "sgzsh269/fingpt-sentiment_llama2-13b_merged",
    "prompt": "Instruction: What is the sentiment of this tweet? Please choose an answer from {negative/neutral/positive}.\nInput: Just bought more $AAPL on the dip. Love this company!\nAnswer:",
    "max_tokens": 10,
    "temperature": 0.0
  }'
```

**Example Response:**

```json
{
  "id": "cmpl-def456",
  "object": "text_completion",
  "created": 1698512400,
  "model": "sgzsh269/fingpt-sentiment_llama2-13b_merged",
  "choices": [
    {
      "text": " positive",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 35,
    "completion_tokens": 1,
    "total_tokens": 36
  }
}
```

#### 3. List Models

**GET** `/v1/models`

List available models on the endpoint.

**Example Request:**

```bash
curl https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1/models \
  -H "Authorization: Bearer <RUNPOD_API_KEY>"
```

**Example Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "sgzsh269/fingpt-sentiment_llama2-13b_merged",
      "object": "model",
      "created": 1698512300,
      "owned_by": "runpod"
    }
  ]
}
```

### Streaming Responses

Both chat and text completion endpoints support streaming. Add `"stream": true` to your request:

```python
response = openai.ChatCompletion.create(
    model="sgzsh269/fingpt-sentiment_llama2-13b_merged",
    messages=[{"role": "user", "content": "Your prompt here"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="")
```

## FinGPT Prompt Format

The FinGPT model is fine-tuned for financial sentiment analysis. For best results, use the following prompt format:

**For News Sentiment:**
```
Instruction: What is the sentiment of this news? Please choose an answer from {strong negative/moderately negative/mildly negative/neutral/mildly positive/moderately positive/strong positive}.
Input: [Your news text here]
Answer:
```

**For Tweet Sentiment:**
```
Instruction: What is the sentiment of this tweet? Please choose an answer from {negative/neutral/positive}.
Input: [Your tweet text here]
Answer:
```

## Configuration & Tuning

### Environment Variables

Customize the deployment by modifying these environment variables in `runpod.template.json`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `sgzsh269/fingpt-sentiment_llama2-13b_merged` | Hugging Face model repository |
| `HF_TOKEN` | (required) | Hugging Face access token for gated models |
| `MAX_MODEL_LEN` | `4096` | Maximum context length in tokens (2048-8192) |
| `GPU_MEMORY_UTILIZATION` | `0.95` | Fraction of GPU VRAM to use (0.8-0.98) |
| `DTYPE` | `float16` | Model precision (`float16` or `bfloat16`) |
| `MAX_NUM_SEQS` | `256` | Max sequences batched together |
| `MAX_CONCURRENCY` | `300` | Max parallel requests in queue |

### GPU Requirements

**Minimum Configuration:**
- **GPU**: NVIDIA A10G (24 GB VRAM)
- **Context Length**: 4096 tokens
- **Note**: Will be near VRAM capacity; may experience OOM with high concurrency

**Recommended Configuration:**
- **GPU**: NVIDIA A100 (40 GB VRAM)
- **Context Length**: 4096-8192 tokens
- **Benefits**: Headroom for batching, longer contexts, higher throughput

**Memory Estimates:**
- **Model Weights (FP16)**: ~26 GB
- **KV Cache (4096 ctx)**: ~2-4 GB per request
- **Batching Overhead**: ~2-6 GB

### Performance Tuning Tips

1. **Reduce Context Length**: If hitting OOM, lower `MAX_MODEL_LEN` to 2048 or 3072
2. **Limit Concurrency**: Set `MAX_CONCURRENCY=10` for memory-constrained deployments
3. **Adjust GPU Utilization**: Lower `GPU_MEMORY_UTILIZATION` to 0.85 if experiencing instability
4. **Use Streaming**: Enable streaming for long-running requests to improve perceived latency
5. **Batch Requests**: vLLM automatically batches; send multiple requests to maximize throughput

## Troubleshooting

### Issue: Endpoint fails to initialize

**Symptoms**: Endpoint stuck in "Initializing" or fails with OOM error

**Solutions**:
- Verify Hugging Face token is valid and has LLaMA2 access
- Upgrade to larger GPU (A100 40GB or A100 80GB)
- Reduce `MAX_MODEL_LEN` to 2048
- Lower `GPU_MEMORY_UTILIZATION` to 0.85

### Issue: Slow response times

**Symptoms**: High latency per request

**Solutions**:
- Check if endpoint is in the correct region (minimize network latency)
- Enable response streaming for better UX
- Reduce `max_tokens` in requests if generating long outputs
- Consider deploying multiple endpoints for load balancing

### Issue: Model outputs incorrect format

**Symptoms**: Model doesn't return expected sentiment labels

**Solutions**:
- Verify you're using the correct prompt format (see FinGPT Prompt Format section)
- Lower temperature to 0.0-0.1 for more deterministic outputs
- Add explicit instructions in the system message
- Check that `max_tokens` is sufficient (minimum 10-20 tokens)

### Issue: 401 Authentication Error

**Symptoms**: API returns "Unauthorized" or 401 error

**Solutions**:
- Verify Runpod API key is correct
- Check that `Authorization: Bearer <KEY>` header is properly formatted
- Ensure API key has permissions for serverless endpoints

## Cost Estimation

Runpod Serverless pricing is usage-based (pay per second of GPU time):

**Example Costs** (as of 2024, check Runpod for current pricing):
- **A10G (24GB)**: ~$0.00045/sec (~$1.62/hr)
- **A100 (40GB)**: ~$0.00090/sec (~$3.24/hr)

**Cost Optimization Tips**:
- Enable autoscaling: Serverless workers scale to zero when idle
- Use smaller context lengths to reduce memory/compute
- Batch multiple requests together
- Set idle timeout to minimize idle costs

## Advanced: Custom Deployment

### Using Docker Compose (Local Testing)

For local testing with a GPU, you can run the vLLM worker directly:

```yaml
version: '3.8'
services:
  fingpt-vllm:
    image: runpod/worker-v1-vllm:v2.2.0stable-cuda12.1.0
    environment:
      - MODEL_NAME=sgzsh269/fingpt-sentiment_llama2-13b_merged
      - HF_TOKEN=${HF_TOKEN}
      - MAX_MODEL_LEN=4096
      - GPU_MEMORY_UTILIZATION=0.95
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Run with: `docker-compose up`

### Multi-GPU Deployment

For tensor parallelism across multiple GPUs, add:

```json
{
  "key": "TENSOR_PARALLEL_SIZE",
  "value": "2",
  "description": "Number of GPUs to split model across"
}
```

**Note**: Requires multi-GPU instance types (e.g., 2x A10G, 2x A100)

## Model Information

**Model**: [sgzsh269/fingpt-sentiment_llama2-13b_merged](https://huggingface.co/sgzsh269/fingpt-sentiment_llama2-13b_merged)

**Base Model**: LLaMA2-13B

**Fine-tuning**: Financial sentiment analysis on news articles and social media

**Use Cases**:
- Financial news sentiment classification
- Social media (Twitter/Reddit) sentiment analysis
- Market sentiment monitoring
- Trading signal generation

**Capabilities**:
- Multi-class sentiment (strong negative to strong positive)
- Binary sentiment (positive/negative)
- Financial domain-specific understanding

**Limitations**:
- Optimized for English financial text
- May require prompt engineering for best results
- Not suitable for general-purpose chat

## License

This deployment configuration is provided as-is. The FinGPT model follows the LLaMA2 Community License Agreement. Please review:
- [LLaMA2 License](https://ai.meta.com/llama/license/)
- [FinGPT Model Card](https://huggingface.co/sgzsh269/fingpt-sentiment_llama2-13b_merged)

## Support & Resources

- **Runpod Documentation**: [docs.runpod.io](https://docs.runpod.io)
- **vLLM Documentation**: [docs.vllm.ai](https://docs.vllm.ai)
- **FinGPT Research**: [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT)
- **Issues**: Report bugs via GitHub Issues

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for:
- Bug fixes
- Documentation improvements
- Performance optimizations
- Additional examples

## Acknowledgments

- **FinGPT Team**: For fine-tuning and releasing the model
- **Meta AI**: For the LLaMA2 base model
- **Runpod**: For serverless GPU infrastructure
- **vLLM Team**: For the high-performance inference engine

---

**Note**: Always ensure you comply with the model licenses and Runpod's terms of service. Keep your API keys and tokens secure.
