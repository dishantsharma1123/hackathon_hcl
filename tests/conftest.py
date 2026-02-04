"""Pytest configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.llm import llm_service

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def api_key_headers():
    """Return headers with API key."""
    return {"Authorization": "Bearer test_api_key_12345"}

@pytest.fixture
def sample_scam_message():
    """Return a sample scam message."""
    return {
        "conversation_id": "00000000-0000-0000-0000-000000000001",
        "message": "Congratulations! You've won Rs. 50,000 in our lottery. Send Rs. 500 to winner@paytm to claim.",
        "sender_id": "scammer123",
        "timestamp": "2024-01-01T00:00:00.000Z",
        "conversation_history": []
    }

# --- NEW MOCK FIXTURE ---
@pytest.fixture(autouse=True)
def mock_llm_service(monkeypatch):
    """
    Automatically mock the LLM service for ALL tests.
    This prevents 429 errors and speeds up testing.
    """
    # 1. Mock Generate (General Chat)
    async def mock_generate(*args, **kwargs):
        return "This is a mocked response from the AI agent."

    # 2. Mock JSON Extraction (Intelligence)
    # We return dummy data so extraction tests pass
    async def mock_extract_json(*args, **kwargs):
        return {
            "upi_ids": ["winner@paytm"],
            "phone_numbers": ["9876543210"],
            "bank_accounts": ["1234567890"],
            "phishing_urls": ["http://scam-site.com"],
            "risk_score": 0.9
        }
    
    # 3. Mock Classification
    async def mock_classify(*args, **kwargs):
        return ("lottery_prize", 0.95)

    # Apply the mocks
    monkeypatch.setattr("app.services.llm.llm_service.generate", mock_generate)
    monkeypatch.setattr("app.services.llm.llm_service.extract_json", mock_extract_json)
    monkeypatch.setattr("app.services.llm.llm_service.classify", mock_classify)
    monkeypatch.setattr("app.services.llm.llm_service.check_connection", AsyncMock(return_value=True))