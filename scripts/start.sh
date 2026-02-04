#!/bin/bash

# Start script for Agentic Honey-Pot System (Hobby Plan Optimized)

set -e

echo "Starting Agentic Honey-Pot System..."

# -----------------------------------------------------
# 1. Start Ollama in the background
# -----------------------------------------------------
echo "Starting Ollama service..."
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 1
done
echo "Ollama is active!"

# -----------------------------------------------------
# 2. Pull the "Tiny" Model
# -----------------------------------------------------
# Default to 'tinyllama' if not set. It is small (~600MB) and safe for Hobby plans.
# Alternative: 'qwen2:0.5b' is even smaller (~350MB).
OLLAMA_MODEL="${OLLAMA_MODEL:-tinyllama}"

echo "Checking/Pulling model: $OLLAMA_MODEL..."
ollama pull $OLLAMA_MODEL
echo "Model $OLLAMA_MODEL ready."

# -----------------------------------------------------
# 3. Start FastAPI server
# -----------------------------------------------------
echo "Starting FastAPI server..."

PORT="${PORT:-8000}"

# Ensure Loguru uses UPPERCASE 'INFO' and Uvicorn uses lowercase 'info'
LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')
UVICORN_LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level $UVICORN_LOG_LEVEL