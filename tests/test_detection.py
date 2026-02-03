"""Tests for scam detection service."""

import pytest
from app.services.scam_detection import ScamDetectionService


class TestScamDetection:
    """Tests for scam detection."""

    @pytest.fixture
    def detection_service(self):
        """Create scam detection service instance."""
        return ScamDetectionService()

    @pytest.mark.asyncio
    async def test_detect_lottery_scam(self, detection_service):
        """Test detection of lottery scam."""
        message = "Congratulations! You've won Rs. 50,000 in our lottery."
        is_scam, confidence, scam_type = await detection_service.detect_scam(message)
        
        assert is_scam is True
        assert confidence > 0.5
        assert scam_type == "lottery_prize"

    @pytest.mark.asyncio
    async def test_detect_phishing_scam(self, detection_service):
        """Test detection of phishing scam."""
        message = "Your account will be blocked. Click here to verify: http://secure-bank.com"
        is_scam, confidence, scam_type = await detection_service.detect_scam(message)
        
        assert is_scam is True
        assert confidence > 0.5
        assert scam_type == "phishing"

    @pytest.mark.asyncio
    async def test_detect_legitimate_message(self, detection_service):
        """Test detection of legitimate message."""
        message = "Hi, how are you doing today?"
        is_scam, confidence, scam_type = await detection_service.detect_scam(message)
        
        assert is_scam is False
        assert scam_type == "legitimate"

    @pytest.mark.asyncio
    async def test_detect_financial_fraud(self, detection_service):
        """Test detection of financial fraud."""
        message = "Send Rs. 5000 to account 1234567890 for guaranteed returns."
        is_scam, confidence, scam_type = await detection_service.detect_scam(message)
        
        assert is_scam is True
        assert confidence > 0.5
        assert scam_type == "financial_fraud"

    def test_pattern_detection_urgency(self, detection_service):
        """Test pattern detection for urgency indicators."""
        message = "Act now! This offer expires today!"
        score, scam_type = detection_service._pattern_detection(message)
        
        assert score > 0

    def test_pattern_detection_financial(self, detection_service):
        """Test pattern detection for financial indicators."""
        message = "Transfer money to this bank account immediately."
        score, scam_type = detection_service._pattern_detection(message)
        
        assert score > 0

    def test_is_high_confidence(self, detection_service):
        """Test high confidence threshold check."""
        assert detection_service.is_high_confidence(0.95) is True
        assert detection_service.is_high_confidence(0.7) is False
