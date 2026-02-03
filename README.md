# Agentic Honey-Pot System

AI-powered system for detecting scam messages and autonomously engaging scammers to extract actionable intelligence.

## Overview

This system is designed for hackathon participation, providing a complete solution for:

- **Scam Detection**: Multi-layered approach using pattern matching and LLM analysis
- **Autonomous Agent**: AI agent that maintains believable human personas
- **Intelligence Extraction**: Extracts bank accounts, UPI IDs, phishing URLs, and phone numbers
- **Multi-turn Conversations**: Maintains conversation state and context

## Tech Stack

- **Backend**: Python with FastAPI
- **AI/LLM**: LangChain with OpenRouter or Ollama (open-source models)
- **Database**: SQLite with SQLAlchemy
- **Deployment**: Railway (Docker support)

## Features

### Scam Detection

- Pattern-based detection (keywords, regex)
- LLM-based semantic classification
- Multi-layered confidence scoring
- Support for multiple scam categories (financial fraud, phishing, lottery, tech support, romance)

### AI Agent

- Multiple personas (Elderly, Job Seeker, Lottery Winner, Business Owner)
- Context-aware response generation
- Turn-specific conversation guidance
- Natural language generation with human-like behavior

### Intelligence Extraction

- Regex-based extraction
- LLM verification and enhancement
- Confidence scoring
- Structured output format

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama (for local LLM)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd hcl_guvi_hackathon
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Ollama:

```bash
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API key and other settings
```

5. Run the application:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoint

**POST** `/api/v1/conversation/message`

Process incoming scam messages and generate agent responses.

**Request Headers:**

```
Authorization: Bearer <your_api_key>
Content-Type: application/json
```

**Request Body:**

```json
{
  "conversation_id": "uuid",
  "message": "Congratulations! You've won Rs. 50,000...",
  "sender_id": "scammer123",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "conversation_history": []
}
```

**Response:**

```json
{
  "conversation_id": "uuid",
  "response": "Really? That's amazing news!",
  "scam_detected": true,
  "agent_active": true,
  "engagement_metrics": {
    "conversation_turns": 1,
    "engagement_duration_seconds": 5,
    "last_activity": "2024-01-01T00:00:05.000Z"
  },
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": [{ "upi_id": "winner@paytm", "confidence": 0.9 }],
    "phishing_urls": [],
    "phone_numbers": []
  },
  "timestamp": "2024-01-01T00:00:05.000Z"
}
```

## Testing

Run the test script:

```bash
chmod +x scripts/test_endpoint.sh
API_KEY=your_key ./scripts/test_endpoint.sh
```

## Deployment

### Railway Deployment

1. Push code to GitHub
2. Connect repository to Railway
3. Configure environment variables in Railway dashboard
4. Deploy

### Environment Variables for Production

```
API_KEY=your_secure_api_key
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
SCAM_CONFIDENCE_THRESHOLD=0.7
MAX_CONVERSATION_TURNS=20
LOG_LEVEL=INFO
```

## Project Structure

```
hcl_guvi_hackathon/
├── app/
│   ├── agents/          # Agent personas and prompts
│   ├── api/             # API routes and authentication
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic (detection, extraction, Ollama)
│   ├── utils/           # Utilities (logger, patterns)
│   ├── config.py        # Configuration
│   ├── database.py      # Database models
│   └── main.py         # FastAPI application
├── data/               # Sample data
├── scripts/            # Setup and test scripts
├── tests/              # Test suite
├── plans/              # Development plan
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Development Plan

See [`plans/agentic-honeypot-development-plan.md`](plans/agentic-honeypot-development-plan.md) for the complete development plan.

## License

MIT License

## Authors

HCL Guvi Hackathon Team
