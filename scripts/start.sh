#!/bin/bash

# Start script for Agentic Honey-Pot System

set -e

echo "Starting Agentic Honey-Pot System..."

# Start FastAPI application
echo "Starting FastAPI server..."

# Use LOG_LEVEL if set, default to info. 
# Convert to lowercase because uvicorn requires 'info', 'debug' etc. (not 'INFO')
LOG_LEVEL="${LOG_LEVEL:-info}"
LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

# Use PORT provided by Railway, default to 8000 if not set
PORT="${PORT:-8000}"

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level $LOG_LEVEL