# Test Suite for Agentic Honey-Pot System

This directory contains comprehensive tests for the Agentic Honey-Pot System.

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── pytest.ini            # Pytest configuration
├── test_api.py            # API endpoint tests
├── test_agent.py          # Agent service tests
├── test_detection.py       # Scam detection tests
├── test_extraction.py      # Intelligence extraction tests
├── test_integration.py     # Integration tests
├── test_e2e.py           # End-to-end scenario tests
├── test_models.py         # Pydantic model tests
└── test_patterns.py       # Pattern matching tests
```

## Test Categories

### Unit Tests

- **test_patterns.py**: Tests for regex pattern matching
- **test_models.py**: Tests for Pydantic model validation
- **test_agent.py**: Tests for agent service logic
- **test_detection.py**: Tests for scam detection service
- **test_extraction.py**: Tests for intelligence extraction service

### Integration Tests

- **test_integration.py**: Tests for API integration and data flow

### End-to-End Tests

- **test_e2e.py**: Complete scenario tests simulating real-world usage

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_api.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Only E2E Tests

```bash
pytest -m e2e
```

### Run Verbose Output

```bash
pytest -v
```

### Run Specific Test

```bash
pytest tests/test_api.py::TestHealthEndpoint::test_health_check
```

## Test Coverage

The test suite aims for high coverage of:

- API endpoints
- Business logic services
- Pattern matching
- Data models
- Error handling

## Test Scenarios

### Scam Detection

- Lottery scams
- Phishing scams
- Financial fraud
- Tech support scams
- Romance scams
- Legitimate messages

### Intelligence Extraction

- Bank account numbers
- UPI IDs
- Phishing URLs
- Phone numbers
- IFSC codes

### Agent Behavior

- Persona selection
- Response generation
- Conversation state management
- Engagement metrics

### API Functionality

- Authentication
- Request validation
- Response formatting
- Error handling

## Prerequisites

Before running tests:

1. Install test dependencies:

```bash
pip install -r requirements.txt
```

2. Set up test environment variables:

```bash
export API_KEY="test_api_key_12345"
```

3. (Optional) Set up Ollama for integration tests:

```bash
./scripts/setup_ollama.sh
```

## CI/CD Integration

For GitHub Actions or other CI/CD:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail with Database Error

- Ensure test database is not locked
- Check SQLite file permissions

### Async Tests Fail

- Ensure `pytest-asyncio` is installed
- Check `asyncio-mode=auto` in pytest.ini

### Ollama Connection Errors

- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_HOST` environment variable
- Verify models are pulled: `ollama list`

### Import Errors

- Ensure you're running from project root
- Check PYTHONPATH includes project directory
