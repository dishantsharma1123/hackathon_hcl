"""Pytest configuration and fixtures."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
