#!/bin/bash

# Railway Deployment Script for Agentic Honey-Pot System
# This script helps deploy the project to Railway using OpenRouter

set -e

echo "======================================"
echo "Agentic Honey-Pot - Railway Deployment"
echo "======================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Run: git init"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env from .env.example"
    echo "⚠️  Please edit .env with your API keys before deploying!"
fi

# Check if .env is in .gitignore
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "⚠️  Warning: .env not in .gitignore. Adding it..."
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "----------------------------------------"
echo "1. ✅ Push code to GitHub repository"
echo "2. ✅ Get OpenRouter API key from: https://openrouter.ai/keys"
echo "3. ✅ Create Railway account: https://railway.app"
echo "4. ✅ Configure environment variables in Railway dashboard"
echo ""
echo "📝 Required Environment Variables for Railway:"
echo "----------------------------------------"
cat << 'EOF'
API_KEY=your_secure_api_key_here
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
OPENROUTER_FALLBACK_MODEL=google/gemma-2-9b-it:free
SCAM_CONFIDENCE_THRESHOLD=0.7
HIGH_CONFIDENCE_THRESHOLD=0.9
MAX_CONVERSATION_TURNS=20
RESPONSE_DELAY_MIN=1.0
RESPONSE_DELAY_MAX=3.0
DATABASE_URL=sqlite:///./honeypot.db
LOG_LEVEL=INFO
EOF

echo ""
echo "🚀 Next Steps:"
echo "----------------------------------------"
echo "1. Go to https://railway.app"
echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "3. Select your repository"
echo "4. Add the environment variables listed above"
echo "5. Click 'Deploy'"
echo ""
echo "✅ Your app will be available at: https://your-app-name.up.railway.app"
echo ""
echo "📚 For more details, see: DEPLOYMENT.md"
