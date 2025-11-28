#!/bin/bash
# Entrypoint for Runpod vLLM Serverless worker
# It launches the default vLLM handler to serve the model API.
python -u /workspace/handler.py   # Execute the worker's handler (vLLM server)
