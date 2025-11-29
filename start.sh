#!/bin/bash
set -euo pipefail

MODEL_DIR="${MODEL_DIR:-/workspace/models}"
MODEL_FILENAME="${MODEL_FILENAME:-FinGPT-MT-Llama3-Q4_K_M.gguf}"
MODEL_PATH="${MODEL_PATH:-${MODEL_DIR}/${MODEL_FILENAME}}"
MODEL_URL="${MODEL_URL:-}"
CONTEXT_LENGTH="${CONTEXT_LENGTH:-4096}"
LLAMA_SERVER_PORT="${LLAMA_SERVER_PORT:-8000}"
API_PORT="${API_PORT:-8001}"
LLAMA_BIN="${LLAMA_BIN:-/workspace/llama.cpp/build/bin/llama-server}"

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
  --host 0.0.0.0 &
LLAMA_PID=$!

echo "Starting OpenAI-compatible API wrapper on port ${API_PORT} ..."
python3 /workspace/handler.py

wait "${LLAMA_PID}"
