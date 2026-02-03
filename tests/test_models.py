"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
import uuid
from app.models.conversation import (
    Message,
    ConversationRequest,
    ConversationResponse,
    EngagementMetrics,
)
from app.models.intelligence import (
    ExtractedBankAccount,
    ExtractedUPI,
    ExtractedURL,
    ExtractedPhone,
    ExtractedIntelligence,
)


class TestMessage:
    """Tests for Message model."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            role="user",
            message="Hello, world!",
            timestamp=datetime.utcnow(),
        )
        
        assert msg.role == "user"
        assert msg.message == "Hello, world!"
        assert isinstance(msg.timestamp, datetime)

    def test_message_default_timestamp(self):
        """Test message with default timestamp."""
        msg = Message(
            role="assistant",
            message="Hi there!",
        )
        
        assert isinstance(msg.timestamp, datetime)

    def test_message_role_validation_user(self):
        """Test message with user role."""
        msg = Message(role="user", message="Test")
        assert msg.role == "user"

    def test_message_role_validation_assistant(self):
        """Test message with assistant role."""
        msg = Message(role="assistant", message="Test")
        assert msg.role == "assistant"


class TestEngagementMetrics:
    """Tests for EngagementMetrics model."""

    def test_metrics_creation(self):
        """Test creating engagement metrics."""
        metrics = EngagementMetrics(
            conversation_turns=5,
            engagement_duration_seconds=120,
            last_activity=datetime.utcnow(),
        )
        
        assert metrics.conversation_turns == 5
        assert metrics.engagement_duration_seconds == 120
        assert isinstance(metrics.last_activity, datetime)

    def test_metrics_defaults(self):
        """Test metrics with default values."""
        metrics = EngagementMetrics()
        
        assert metrics.conversation_turns == 0
        assert metrics.engagement_duration_seconds == 0
        assert isinstance(metrics.last_activity, datetime)


class TestConversationRequest:
    """Tests for ConversationRequest model."""

    def test_request_creation(self):
        """Test creating a conversation request."""
        conv_id = uuid.uuid4()
        request = ConversationRequest(
            conversation_id=conv_id,
            message="Test message",
            sender_id="user123",
            timestamp=datetime.utcnow(),
            conversation_history=[],
        )
        
        assert request.conversation_id == conv_id
        assert request.message == "Test message"
        assert request.sender_id == "user123"
        assert request.conversation_history == []

    def test_request_with_history(self):
        """Test request with conversation history."""
        conv_id = uuid.uuid4()
        history = [
            Message(role="user", message="Hello"),
            Message(role="assistant", message="Hi!"),
        ]
        
        request = ConversationRequest(
            conversation_id=conv_id,
            message="How are you?",
            sender_id="user123",
            timestamp=datetime.utcnow(),
            conversation_history=history,
        )
        
        assert len(request.conversation_history) == 2


class TestConversationResponse:
    """Tests for ConversationResponse model."""

    def test_response_creation(self):
        """Test creating a conversation response."""
        conv_id = uuid.uuid4()
        response = ConversationResponse(
            conversation_id=conv_id,
            response="I'm fine, thanks!",
            scam_detected=False,
            agent_active=True,
            engagement_metrics=EngagementMetrics(),
            extracted_intelligence=ExtractedIntelligence(),
            timestamp=datetime.utcnow(),
        )
        
        assert response.conversation_id == conv_id
        assert response.response == "I'm fine, thanks!"
        assert response.scam_detected is False
        assert response.agent_active is True


class TestExtractedIntelligence:
    """Tests for ExtractedIntelligence model."""

    def test_empty_intelligence(self):
        """Test empty intelligence object."""
        intel = ExtractedIntelligence()
        
        assert len(intel.bank_accounts) == 0
        assert len(intel.upi_ids) == 0
        assert len(intel.phishing_urls) == 0
        assert len(intel.phone_numbers) == 0

    def test_intelligence_with_data(self):
        """Test intelligence with extracted data."""
        intel = ExtractedIntelligence(
            bank_accounts=[
                ExtractedBankAccount(
                    account_number="123456789012",
                    ifsc_code="SBIN0001234",
                    bank_name="State Bank of India",
                    confidence=0.9,
                )
            ],
            upi_ids=[
                ExtractedUPI(upi_id="user@paytm", confidence=0.95)
            ],
        )
        
        assert len(intel.bank_accounts) == 1
        assert len(intel.upi_ids) == 1
        assert intel.bank_accounts[0].account_number == "123456789012"
        assert intel.upi_ids[0].upi_id == "user@paytm"


class TestExtractedBankAccount:
    """Tests for ExtractedBankAccount model."""

    def test_bank_account_creation(self):
        """Test creating extracted bank account."""
        account = ExtractedBankAccount(
            account_number="123456789012",
            ifsc_code="SBIN0001234",
            bank_name="State Bank of India",
            confidence=0.9,
        )
        
        assert account.account_number == "123456789012"
        assert account.ifsc_code == "SBIN0001234"
        assert account.bank_name == "State Bank of India"
        assert account.confidence == 0.9

    def test_bank_account_defaults(self):
        """Test bank account with optional fields."""
        account = ExtractedBankAccount(
            account_number="123456789012",
        )
        
        assert account.ifsc_code is None
        assert account.bank_name is None
        assert account.confidence == 1.0


class TestExtractedUPI:
    """Tests for ExtractedUPI model."""

    def test_upi_creation(self):
        """Test creating extracted UPI ID."""
        upi = ExtractedUPI(
            upi_id="user@paytm",
            confidence=0.95,
        )
        
        assert upi.upi_id == "user@paytm"
        assert upi.confidence == 0.95


class TestExtractedURL:
    """Tests for ExtractedURL model."""

    def test_url_creation(self):
        """Test creating extracted URL."""
        url = ExtractedURL(
            url="http://example.com/path",
            domain="example.com",
            confidence=0.9,
        )
        
        assert url.url == "http://example.com/path"
        assert url.domain == "example.com"
        assert url.confidence == 0.9


class TestExtractedPhone:
    """Tests for ExtractedPhone model."""

    def test_phone_creation(self):
        """Test creating extracted phone number."""
        phone = ExtractedPhone(
            number="+91-9876543210",
            confidence=0.85,
        )
        
        assert phone.number == "+91-9876543210"
        assert phone.confidence == 0.85
