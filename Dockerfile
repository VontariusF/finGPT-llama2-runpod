FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y \
    git wget curl python3 python3-pip build-essential cmake ca-certificates \
    libgomp1 libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Build llama.cpp with CUDA support
# Note: llama.cpp vendors ggml as a git submodule, so clone recursively.
RUN git clone --depth 1 --recurse-submodules https://github.com/ggerganov/llama.cpp.git && \
    cd llama.cpp && \
    mkdir build && \
    cd build && \
    cmake -DGGML_CUDA=ON .. && \
    cmake --build . --config Release -j$(nproc)

WORKDIR /workspace

# Python deps and app code
WORKDIR /workspace
COPY handler.py .
COPY start.sh .
RUN pip install --no-cache-dir flask waitress requests runpod
RUN chmod +x /workspace/start.sh

# Expose API port (OpenAI-compatible wrapper)
EXPOSE 8001

# Environment defaults
ENV MODEL_URL=""
ENV MODEL_FILENAME="FinGPT-MT-Llama3-Q4_K_M.gguf"
ENV MODEL_DIR="/workspace/models"
ENV MODEL_PATH="/workspace/models/FinGPT-MT-Llama3-Q4_K_M.gguf"
ENV CONTEXT_LENGTH=4096
ENV MODEL_NAME="fingpt-mt-llama3-8b-lora-gguf"

# Entrypoint
CMD ["bash", "start.sh"]
