# FinGPT-MT Llama-3 8B LoRA (GGUF) - RunPod Serverless

Deploy [FinGPT-MT-Llama-3-8B-LoRA-GGUF](https://huggingface.co/second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF) on RunPod Serverless using llama.cpp with CUDA acceleration. Provides both RunPod native and OpenAI-compatible API endpoints.

## Features

- ✅ **CUDA-accelerated** inference using llama.cpp
- ✅ **Auto-scaling** from zero (pay only when used)
- ✅ **GitHub auto-build** - no Docker Hub needed
- ✅ **Dual API formats** - RunPod native + OpenAI-compatible
- ✅ **Q4_K_M quantization** - fits on T4/A10 GPUs (8-10GB VRAM)
- ✅ **Fast cold starts** - ~22-60 seconds (caches model after first run)

## Architecture

- **Base**: `nvidia/cuda:12.1.0-devel-ubuntu22.04`
- **Inference Engine**: llama.cpp (built from source with CUDA support)
- **Handler**: RunPod Serverless SDK (Python)
- **Model**: FinGPT-MT-Llama-3-8B-LoRA Q4_K_M GGUF (~5GB)

## Quick Start

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/finGPT-llama2-runpod.git
cd finGPT-llama2-runpod
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

Default model is FinGPT-MT-Llama-3-8B-LoRA-GGUF Q4_K_M. To use a different model, edit `MODEL_URL` in `.env`.

### 3. Deploy to RunPod Serverless

1. Go to [RunPod Serverless Console](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Configure:
   - **Name**: `FinGPT-Llama3-8B`
   - **Endpoint Type**: **Serverless** (Queue)
   - **GPU**: T4 (16GB) or A10G (24GB)
   - **Build Method**: **Build from GitHub**
   - **Repository**: `https://github.com/YOUR_USERNAME/finGPT-llama2-runpod`
   - **Branch**: `master`
   - **Dockerfile Path**: `Dockerfile`

4. **Environment Variables** (in Raw Editor):
   ```bash
   MODEL_URL=https://huggingface.co/second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF/resolve/main/FinGPT-MT-Llama-3-8B-LoRA-Q4_K_M.gguf
   MODEL_FILENAME=FinGPT-MT-Llama3-Q4_K_M.gguf
   CONTEXT_LENGTH=4096
   MODEL_NAME=fingpt-mt-llama3-8b-lora-gguf
   ```

5. **Advanced Settings**:
   - **Container Disk**: 20 GB minimum
   - **Max Workers**: 1-3
   - **Idle Timeout**: 5 seconds (for cost savings)

6. Click **"Deploy"**
7. Wait ~10-15 minutes for build (downloads CUDA, compiles llama.cpp)
8. Copy your **Endpoint ID** when ready

### 4. Test Your Endpoint

```bash
# Install dependencies
pip install requests python-dotenv

# Set your credentials in .env
echo "RUNPOD_API_KEY=your_api_key_here" >> .env
echo "ENDPOINT_ID=your_endpoint_id_here" >> .env

# Run test
python simple_test.py
```

## API Usage

### RunPod Native Format (Recommended)

**Python:**
```python
import requests

url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"
response = requests.post(
    url,
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "input": {
            "prompt": "Analyze this financial headline: Tech stocks rally on earnings.",
            "max_tokens": 200,
            "temperature": 0.7
        }
    },
    timeout=120
)

result = response.json()
print(result['output']['output'])
```

**cURL:**
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "What is financial sentiment analysis?",
      "max_tokens": 150,
      "temperature": 0.7
    }
  }'
```

### OpenAI-Compatible Format (Experimental)

**Note**: OpenAI format at `/openai/v1/*` is experimental and may timeout. Use RunPod native format for production.

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_RUNPOD_API_KEY",
    base_url="https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/openai/v1"
)

response = client.chat.completions.create(
    model="fingpt-mt-llama3-8b-lora-gguf",
    messages=[{"role": "user", "content": "Analyze: Market drops 5%."}],
    max_tokens=150
)

print(response.choices[0].message.content)
```

## Environment Variables

Configure these in RunPod endpoint settings or in `.env` for local testing:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_URL` | (see above) | GGUF download URL from Hugging Face |
| `MODEL_FILENAME` | `FinGPT-MT-Llama3-Q4_K_M.gguf` | Saved model filename |
| `MODEL_DIR` | `/workspace/models` | Model cache directory |
| `CONTEXT_LENGTH` | `4096` | llama.cpp context window |
| `MODEL_NAME` | `fingpt-mt-llama3-8b-lora-gguf` | Model ID in responses |
| `LLAMA_SERVER_PORT` | `8000` | llama.cpp internal port |
| `HF_TOKEN` | (optional) | Hugging Face token for gated models |

## GPU Recommendations

| Quantization | VRAM Needed | Recommended GPU |
|--------------|-------------|-----------------|
| Q4_K_M (~5GB) | 8-10 GB | T4 (16GB), A10G (24GB) |
| Q5_K_M (~6GB) | 10-12 GB | A10G (24GB) |
| Q8_0 (~8GB) | 12-16 GB | RTX 3090, A100 |

**Best balance**: A10G + Q4_K_M with context 4096

## Test Scripts

- `simple_test.py` - Quick test with basic prompt
- `test_regular.py` - Full test with RunPod format
- `test_endpoint.py` - Test OpenAI-compatible endpoints
- `check_job.py` - Check job status by ID
- `sync_test.py` - Test with synchronous execution

## Project Structure

```
.
├── Dockerfile                      # CUDA + llama.cpp build
├── handler.py                      # RunPod Serverless handler
├── start.sh                        # Startup script (downloads model, starts llama.cpp)
├── runpod.serverless.config.json  # RunPod deployment config reference
├── .env.example                    # Environment variable template
├── README.md                       # This file
├── USAGE.md                        # Detailed usage guide
└── *.py                            # Test scripts
```

## Troubleshooting

### Jobs Fail or Timeout

- **Check logs** in RunPod console for error messages
- **Increase timeout** in your requests (cold start takes 30-60s)
- **Verify GPU** is allocated (check worker logs)

### Empty Model Output

- **Increase max_tokens** (try 150-200)
- **Adjust temperature** (0.7-0.9 for financial text)
- **Check prompt format** - model expects clear questions

### Build Fails

- **Check CUDA architectures** in Dockerfile (lines 18-20)
- **Verify GitHub repo** is public or RunPod has access
- **Check container disk** size (need >=20GB)

## Performance

- **Cold Start**: 22-60 seconds (first request after idle)
- **Warm Inference**: 50-150ms per request
- **Model Size**: ~5GB (Q4_K_M)
- **Cost**: Pay only for execution time (serverless)

## Notes

- llama.cpp runs internally on port 8000
- Handler waits for llama.cpp to be ready before accepting requests
- Model is cached after first download (~5GB)
- For longer contexts, increase `CONTEXT_LENGTH` (requires more VRAM)

## License

This deployment template is MIT licensed. The FinGPT model follows its own license from [second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF](https://huggingface.co/second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF).

## Contributing

PRs welcome! Please ensure:
- `.env` is in `.gitignore` (credentials)
- Test scripts work
- README stays up to date

## Support

- [RunPod Documentation](https://docs.runpod.io/)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [FinGPT Model Card](https://huggingface.co/second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF)
