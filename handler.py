import os
import time
import uuid
import requests
from flask import Flask, request, jsonify
from waitress import serve

LLAMA_SERVER = f"http://127.0.0.1:{os.getenv('LLAMA_SERVER_PORT', '8000')}"
MODEL_NAME = os.getenv("MODEL_NAME", "fingpt-mt-llama3-8b-lora-gguf")
API_PORT = int(os.getenv("API_PORT", "8001"))

app = Flask(__name__)


def llama_completion(prompt: str, max_tokens: int = 256, temperature: float = 0.7):
    """Send a completion request to llama.cpp and return text."""
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


@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify({"object": "list", "data": [{"id": MODEL_NAME, "object": "model"}]})


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    payload = request.get_json(force=True, silent=True) or {}
    messages = payload.get("messages", [])
    prompt = "\n".join(m.get("content", "") for m in messages)
    max_tokens = payload.get("max_tokens", 256)
    temperature = payload.get("temperature", 0.7)

    output = llama_completion(prompt, max_tokens=max_tokens, temperature=temperature)

    return jsonify(
        {
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
    )


@app.route("/v1/completions", methods=["POST"])
def completions():
    payload = request.get_json(force=True, silent=True) or {}
    prompt = payload.get("prompt", "")
    max_tokens = payload.get("max_tokens", 256)
    temperature = payload.get("temperature", 0.7)

    output = llama_completion(prompt, max_tokens=max_tokens, temperature=temperature)

    return jsonify(
        {
            "id": str(uuid.uuid4()),
            "object": "text_completion",
            "created": int(time.time()),
            "model": MODEL_NAME,
            "choices": [{"index": 0, "text": output, "finish_reason": "stop"}],
            "usage": {},
        }
    )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=API_PORT)
