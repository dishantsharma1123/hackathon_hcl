#!/bin/bash

# Start script for Agentic Honey-Pot System

set -e

echo "Starting Agentic Honey-Pot System..."

# Start FastAPI application
echo "Starting FastAPI server..."

# Use PORT provided by Railway, default to 8000 if not set
PORT="${PORT:-8000}"

# Handle Log Level
# 1. Default to INFO if not set
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# 2. Ensure LOG_LEVEL is UPPERCASE for the Python app (Loguru needs 'INFO')
# We export this so the Python application (app.config) picks up the uppercase version
export LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')

# 3. Create a lowercase version specifically for Uvicorn (Uvicorn needs 'info')
UVICORN_LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level $UVICORN_LOG_LEVEL