#!/bin/bash
set -euo pipefail

MODEL_DIR="${MODEL_DIR:-/workspace/models}"
MODEL_FILENAME="${MODEL_FILENAME:-FinGPT-MT-Llama3-Q4_K_M.gguf}"
MODEL_PATH="${MODEL_PATH:-${MODEL_DIR}/${MODEL_FILENAME}}"
MODEL_URL="${MODEL_URL:-}"
CONTEXT_LENGTH="${CONTEXT_LENGTH:-4096}"
LLAMA_SERVER_PORT="${LLAMA_SERVER_PORT:-8000}"
API_PORT="${API_PORT:-8001}"

# Find llama-server binary (location varies by llama.cpp version)
if [[ -f "/workspace/llama.cpp/build/bin/llama-server" ]]; then
  LLAMA_BIN="/workspace/llama.cpp/build/bin/llama-server"
elif [[ -f "/workspace/llama.cpp/build/bin/server" ]]; then
  LLAMA_BIN="/workspace/llama.cpp/build/bin/server"
elif [[ -f "/workspace/llama.cpp/build/llama-server" ]]; then
  LLAMA_BIN="/workspace/llama.cpp/build/llama-server"
else
  echo "ERROR: Could not find llama-server binary" >&2
  exit 1
fi

echo "Using llama-server binary: ${LLAMA_BIN}"

mkdir -p "${MODEL_DIR}"

if [[ ! -f "${MODEL_PATH}" ]]; then
  if [[ -z "${MODEL_URL}" ]]; then
    echo "MODEL_URL is required to download the GGUF file." >&2
    exit 1
  fi
  echo "Downloading model from ${MODEL_URL} ..."
  AUTH_HEADER=()
  if [[ -n "${HF_TOKEN:-}" ]]; then
    AUTH_HEADER=(--header "Authorization: Bearer ${HF_TOKEN}")
  fi
  wget -O "${MODEL_PATH}" "${AUTH_HEADER[@]}" "${MODEL_URL}"
else
  echo "Using cached model at ${MODEL_PATH}"
fi

echo "Starting llama.cpp server on port ${LLAMA_SERVER_PORT} ..."
"${LLAMA_BIN}" \
  -m "${MODEL_PATH}" \
  -c "${CONTEXT_LENGTH}" \
  --port "${LLAMA_SERVER_PORT}" \
  --host 127.0.0.1 &
LLAMA_PID=$!

# Wait for llama.cpp to be ready
echo "Waiting for llama.cpp server to be ready..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:${LLAMA_SERVER_PORT}/health > /dev/null 2>&1; then
    echo "llama.cpp server is ready!"
    break
  fi
  sleep 2
done

echo "Starting RunPod Serverless handler..."
python3 /workspace/handler.py
