#!/bin/bash

# Start script for Agentic Honey-Pot System

set -e

echo "Starting Agentic Honey-Pot System..."

# Wait for Ollama to be ready (if running locally)
if [ -n "$OLLAMA_HOST" ]; then
    echo "Waiting for Ollama service at $OLLAMA_HOST..."
    for i in {1..30}; do
        if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
            echo "Ollama service is ready!"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
fi

# Pull models if not already present
if [ -n "$OLLAMA_MODEL" ]; then
    echo "Pulling Ollama model: $OLLAMA_MODEL"
    ollama pull "$OLLAMA_MODEL" || echo "Model pull failed, may already exist"
fi

if [ -n "$OLLAMA_FALLBACK_MODEL" ]; then
    echo "Pulling fallback Ollama model: $OLLAMA_FALLBACK_MODEL"
    ollama pull "$OLLAMA_FALLBACK_MODEL" || echo "Fallback model pull failed, may already exist"
fi

# Start the FastAPI application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level $LOG_LEVEL
