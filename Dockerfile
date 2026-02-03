# Multi-stage Dockerfile for Agentic Honey-Pot System

# Stage 1: Base image with Ollama
FROM ollama/ollama:latest as ollama-base

# Stage 2: Python application
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://localhost:11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start script
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
