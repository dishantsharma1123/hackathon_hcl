#!/bin/bash

# Setup script for Ollama

echo "Setting up Ollama for Agentic Honey-Pot System..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# Start Ollama service (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
else
    echo "Ollama service is already running."
fi

# Pull models
echo "Pulling models..."
ollama pull llama3.1
ollama pull mistral

echo "Ollama setup complete!"
echo "Available models:"
ollama list
