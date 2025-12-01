"""
RunPod Serverless handler for FinGPT with llama.cpp backend
Provides OpenAI-compatible API endpoints
"""

import os
import time
import uuid
import json
import requests
import runpod

LLAMA_SERVER = f"http://127.0.0.1:{os.getenv('LLAMA_SERVER_PORT', '8000')}"
MODEL_NAME = os.getenv("MODEL_NAME", "fingpt-mt-llama3-8b-lora-gguf")


def wait_for_llama_server(max_attempts=30, delay=2):
    """Wait for llama.cpp server to be ready"""
    print(f"Waiting for llama.cpp server at {LLAMA_SERVER}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{LLAMA_SERVER}/health", timeout=5)
            if response.status_code == 200:
                print(f"llama.cpp server is ready after {attempt + 1} attempts!")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: {e}")
            time.sleep(delay)

    print("ERROR: llama.cpp server failed to start!")
    return False


def llama_completion(prompt: str, max_tokens: int = 256, temperature: float = 0.7):
    """Send a completion request to llama.cpp and return text."""
    try:
        resp = requests.post(
            f"{LLAMA_SERVER}/completion",
            json={
                "prompt": prompt,
                "n_predict": max_tokens,
                "temperature": temperature,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        # llama.cpp returns either `content` or a list under `choices`; handle both.
        if "content" in data:
            return data["content"]
        choices = data.get("choices", [])
        if choices and "text" in choices[0]:
            return choices[0]["text"]
        raise RuntimeError(f"Unexpected llama.cpp response: {data}")
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Cannot connect to llama.cpp server at {LLAMA_SERVER}: {e}")
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"llama.cpp server timeout: {e}")
    except Exception as e:
        raise RuntimeError(f"llama.cpp error: {e}")


def handle_openai_request(event):
    """
    Handle both OpenAI-compatible and regular requests via RunPod Serverless.
    - OpenAI routes: received via /openai/* path with openai_route and openai_input
    - Regular input: received via /run or /runsync with standard input field
    """
    try:
        # Normalize event fields for OpenAI-style requests
        # RunPod may wrap values under event["input"].
        input_section = event.get("input") if isinstance(event.get("input"), dict) else {}
        openai_input = event.get("openai_input") or input_section.get("openai_input") or input_section.get("body")
        openai_route = (
            event.get("openai_route")
            or input_section.get("openai_route")
            or event.get("path", "")
        )

        # If payload arrived as JSON string, parse it.
        if isinstance(openai_input, str):
            try:
                openai_input = json.loads(openai_input)
            except Exception:
                pass

        # If not OpenAI route, treat as regular input
        if openai_input is None:
            # Regular RunPod input format
            regular_input = event.get("input", {})

            # Extract prompt from various possible input formats
            prompt = regular_input.get("prompt") or regular_input.get("text") or str(regular_input.get("test", ""))
            if not prompt:
                return {
                    "status": "error",
                    "message": "No prompt provided. Use 'prompt' or 'text' field, or use OpenAI-compatible endpoints at /openai/v1/*"
                }

            max_tokens = regular_input.get("max_tokens", 256)
            temperature = regular_input.get("temperature", 0.7)

            # Run completion
            output = llama_completion(prompt, max_tokens=max_tokens, temperature=temperature)

            return {
                "status": "success",
                "output": output,
                "model": MODEL_NAME
            }

        # Handle OpenAI-compatible routes
        # /v1/models
        if "/v1/models" in openai_route or openai_route == "/models":
            return {
                "object": "list",
                "data": [{"id": MODEL_NAME, "object": "model"}]
            }

        # /v1/chat/completions
        if "/v1/chat/completions" in openai_route or "/chat/completions" in openai_route:
            messages = openai_input.get("messages", [])
            prompt = "\n".join(m.get("content", "") for m in messages)
            max_tokens = openai_input.get("max_tokens", 256)
            temperature = openai_input.get("temperature", 0.7)

            output = llama_completion(prompt, max_tokens=max_tokens, temperature=temperature)

            return {
                "id": str(uuid.uuid4()),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": MODEL_NAME,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": output},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {},
            }

        # /v1/completions
        if "/v1/completions" in openai_route or "/completions" in openai_route:
            prompt = openai_input.get("prompt", "")
            max_tokens = openai_input.get("max_tokens", 256)
            temperature = openai_input.get("temperature", 0.7)

            output = llama_completion(prompt, max_tokens=max_tokens, temperature=temperature)

            return {
                "id": str(uuid.uuid4()),
                "object": "text_completion",
                "created": int(time.time()),
                "model": MODEL_NAME,
                "choices": [{"index": 0, "text": output, "finish_reason": "stop"}],
                "usage": {},
            }

        # Unknown OpenAI route
        return {
            "error": f"Unknown OpenAI route: {openai_route}",
            "available_routes": ["/v1/models", "/v1/chat/completions", "/v1/completions"]
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("Starting RunPod Serverless handler...")
    print("Handler will wait for llama.cpp to be ready before processing requests")

    # Wait for llama.cpp server to be ready before starting handler
    if not wait_for_llama_server():
        print("FATAL: Cannot start handler - llama.cpp server is not available")
        exit(1)

    print("Starting handler - ready to process requests!")
    runpod.serverless.start({"handler": handle_openai_request})
