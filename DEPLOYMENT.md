# Deployment Guide - Agentic Honey-Pot System

This guide covers deploying the Agentic Honey-Pot System to Railway.

## Prerequisites

- GitHub account
- Railway account (free tier available)
- Either: Ollama service OR OpenRouter API key

## Option 1: Railway with OpenRouter (Recommended for low-power systems)

This option uses OpenRouter's cloud-based LLM API - no local model downloads needed.

### Step 1: Prepare GitHub Repository

1. Push your code to GitHub
2. Ensure `.env` is NOT committed (it's in `.gitignore`)

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will detect the Python project automatically

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

```
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
```

**Important:**

- Replace `your_openrouter_api_key_here` with your OpenRouter API key
- The free models may have rate limits - consider upgrading for production

### Step 4: Deploy

Click "Deploy" and wait for Railway to build and deploy.

### Step 5: Get Your API URL

After deployment, Railway will provide a URL like:

```
https://your-app-name.up.railway.app
```

Your API endpoint will be:

```
https://your-app-name.up.railway.app/api/v1/conversation/message
```

## Option 2: Railway with External Ollama

This option uses an external Ollama service (your local machine or another server).

### Step 1: Prepare GitHub Repository

1. Push your code to GitHub
2. Ensure `.env` is NOT committed (it's in `.gitignore`)

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will detect the Python project automatically

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

```
API_KEY=your_secure_api_key_here
OLLAMA_HOST=http://your-ollama-server:11434
OLLAMA_MODEL=llama3.1
OLLAMA_FALLBACK_MODEL=mistral
SCAM_CONFIDENCE_THRESHOLD=0.7
HIGH_CONFIDENCE_THRESHOLD=0.9
MAX_CONVERSATION_TURNS=20
RESPONSE_DELAY_MIN=1.0
RESPONSE_DELAY_MAX=3.0
DATABASE_URL=sqlite:///./honeypot.db
LOG_LEVEL=INFO
```

**Important:** Replace `your-ollama-server` with your actual Ollama server address.

### Step 4: Deploy

Click "Deploy" and wait for Railway to build and deploy.

### Step 5: Get Your API URL

After deployment, Railway will provide a URL like:

```
https://your-app-name.up.railway.app
```

Your API endpoint will be:

```
https://your-app-name.up.railway.app/api/v1/conversation/message
```

## Option 2: Railway with Docker Compose (Advanced)

This option runs Ollama and the app together on Railway.

### Step 1: Create docker-compose.yml

```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: ollama serve

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - API_KEY=${API_KEY}
    depends_on:
      - ollama

volumes:
  ollama_data:
```

### Step 2: Update Dockerfile

The existing Dockerfile should work, but you may need to adjust for Railway.

### Step 3: Deploy

Follow the same steps as Option 1, but Railway will use docker-compose.yml.

## Testing the Deployment

### 1. Health Check

```bash
curl https://your-app-name.up.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "agentic-honeypot",
  "ollama_connected": true
}
```

### 2. Test with Sample Message

```bash
curl -X POST \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test-123",
    "message": "Congratulations! You won Rs. 50,000!",
    "sender_id": "scammer",
    "timestamp": "2024-01-01T00:00:00.000Z",
    "conversation_history": []
  }' \
  https://your-app-name.up.railway.app/api/v1/conversation/message
```

## Troubleshooting

### Ollama Connection Failed

- Check `OLLAMA_HOST` environment variable
- Ensure Ollama service is running
- Check firewall/network settings

### Build Failures

- Check `requirements.txt` for correct versions
- Ensure all files are committed to GitHub
- Check Railway build logs

### API Returns 500 Error

- Check Railway logs for error details
- Verify all environment variables are set
- Check Ollama connection

## Railway-Specific Notes

- Free tier has 500 hours/month limit
- Database is ephemeral on free tier (use Railway Postgres for persistence)
- Automatic deployments on git push
- Built-in monitoring and logging

## Alternative: Local Deployment

For testing locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Setup Ollama
./scripts/setup_ollama.sh

# Set environment variables
export API_KEY="your_key"

# Run the app
python -m app.main
```

## Submission Checklist

Before submitting to the hackathon:

- [ ] API is publicly accessible
- [ ] API key authentication is working
- [ ] Health check endpoint returns 200
- [ ] Scam detection is working
- [ ] Agent engages in conversations
- [ ] Intelligence extraction returns data
- [ ] Response time is under 2 seconds
- [ ] Documentation is complete
- [ ] Demo video/walkthrough prepared
