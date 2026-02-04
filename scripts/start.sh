#!/bin/bash

# Start script for Agentic Honey-Pot System

set -e

echo "Starting Agentic Honey-Pot System..."

# Start FastAPI application
echo "Starting FastAPI server..."
# Use LOG_LEVEL if set, default to INFO (lowercase)
LOG_LEVEL="${LOG_LEVEL:-info}"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level $LOG_LEVEL
