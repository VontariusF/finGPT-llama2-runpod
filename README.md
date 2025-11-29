# FinGPT-MT Llama-3 8B LoRA (GGUF) - Runpod Serverless (llama.cpp, OpenAI-compatible)

OpenAI-style API for `second-state/FinGPT-MT-Llama-3-8B-LoRA-GGUF` running on Runpod Serverless using `llama.cpp` and a lightweight Flask proxy.

## What's inside
- `Dockerfile` - CUDA runtime + llama.cpp build + app
- `start.sh` - downloads GGUF and starts llama.cpp + API proxy
- `handler.py` - OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/completions`, `/v1/models`)
- `runpod.serverless.config.json` - template for Runpod Serverless
- `.env.example` - model URL and tunables

## Requirements
- Runpod Serverless GPU (A10G 24GB recommended; Q4_K_M fits on 8-10GB)
- Docker to build/push your image
- (Optional) `HF_TOKEN` if the model becomes gated

## Environment variables
- `MODEL_URL` (required): GGUF download URL.
- `MODEL_FILENAME` (default `FinGPT-MT-Llama3-Q4_K_M.gguf`): saved filename.
- `MODEL_DIR` (default `/workspace/models`): download/cache dir.
- `MODEL_PATH` (default `MODEL_DIR/MODEL_FILENAME`): resolved path.
- `CONTEXT_LENGTH` (default `4096`): llama.cpp context tokens.
- `MODEL_NAME` (default `fingpt-mt-llama3-8b-lora-gguf`): reported model id.
- `LLAMA_SERVER_PORT` (default `8000`): llama.cpp REST port.
- `API_PORT` (default `8001`): OpenAI-compatible proxy port.
- `HF_TOKEN` (optional): injected as Bearer header for gated models.

Ports exposed:
- llama.cpp: `8000` (internal)
- OpenAI proxy: `8001` (exposed)

## Build & publish
```bash
cp .env.example .env   # edit MODEL_URL/HF_TOKEN if needed

# build (set your repo/tag)
docker build -t your-dockerhub-username/fingpt-llama3-gguf:latest .

# push
docker push your-dockerhub-username/fingpt-llama3-gguf:latest
```

## Deploy on Runpod Serverless
1) Open `runpod.serverless.config.json` and set `image` to your pushed image. Adjust `MODEL_URL`, `CONTEXT_LENGTH`, etc., if needed.

2) In Runpod console, create a Serverless endpoint:
   - Image: `your-dockerhub-username/fingpt-llama3-gguf:latest`
   - GPU: A10G (24GB) recommended; Q4_K_M also works on T4/16GB with lower context.
   - Container disk: >=20 GB (model cache + binaries).
   - Allowed port: 8001.
   - Env vars: `MODEL_URL`, `MODEL_FILENAME`, `CONTEXT_LENGTH`, optional `HF_TOKEN`.

3) Deploy. First cold start downloads the GGUF; subsequent inits reuse the cached file.

## API usage (OpenAI-compatible)
Base URL: `https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1`

Chat:
```bash
export RUNPOD_API_KEY=your_runpod_api_key
export ENDPOINT_ID=your_endpoint_id

curl https://api.runpod.ai/v2/${ENDPOINT_ID}/openai/v1/chat/completions \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "fingpt-mt-llama3-8b-lora-gguf",
    "messages": [{"role": "user", "content": "Analyze this financial headline: Market drops 5%."}]
  }'
```

Completion:
```bash
curl https://api.runpod.ai/v2/${ENDPOINT_ID}/openai/v1/completions \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "fingpt-mt-llama3-8b-lora-gguf",
    "prompt": "Sentiment of: Market drops 5%?",
    "max_tokens": 50
  }'
```

## GPU guidance (GGUF)
- Q4_K_M (~5 GB): fits 8-10 GB VRAM (T4/16GB, A10G/24GB).
- Q5_*: 6-8 GB VRAM (A10G).
- Q8_*: 12-16 GB VRAM (3090/A100).
Best balance: A10G + Q4_K_M, context 4096.

## Notes
- llama.cpp runs on 8000 internally; only 8001 is exposed.
- If you change quant/model file, update `MODEL_URL`, `MODEL_FILENAME`, and rebuild or override via env at deploy time.
- For longer contexts, raise `CONTEXT_LENGTH` and ensure VRAM headroom.
