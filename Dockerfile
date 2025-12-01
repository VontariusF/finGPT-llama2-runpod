FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

WORKDIR /workspace

# System dependencies
RUN apt-get update && apt-get install -y \
    git wget curl python3 python3-pip build-essential cmake ca-certificates \
    libgomp1 libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Build llama.cpp with CUDA support
# Note: llama.cpp vendors ggml as a git submodule, so clone recursively.
# Using official llama.cpp CUDA Dockerfile configuration
# Specify common CUDA architectures: 60,61(P100), 70(V100), 75(T4), 80(A100), 86(A10/RTX30), 89(L40/RTX40), 90(H100)
RUN git clone --depth 1 --recurse-submodules https://github.com/ggerganov/llama.cpp.git && \
    cd llama.cpp && \
    cmake -B build \
          -DGGML_NATIVE=OFF \
          -DGGML_CUDA=ON \
          -DCMAKE_CUDA_ARCHITECTURES="60;61;70;75;80;86;89;90" \
          -DLLAMA_BUILD_TESTS=OFF \
          -DCMAKE_EXE_LINKER_FLAGS=-Wl,--allow-shlib-undefined \
          . && \
    cmake --build build --config Release -j$(nproc)

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
