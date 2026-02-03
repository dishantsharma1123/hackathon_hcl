"""Tests for intelligence extraction service."""

import pytest
from app.services.extraction import IntelligenceExtractionService


class TestIntelligenceExtraction:
    """Tests for intelligence extraction."""

    @pytest.fixture
    def extraction_service(self):
        """Create extraction service instance."""
        return IntelligenceExtractionService()

    @pytest.mark.asyncio
    async def test_extract_upi_id(self, extraction_service):
        """Test UPI ID extraction."""
        message = "Send payment to winner@paytm"
        intelligence = await extraction_service.extract_intelligence(message)
        
        assert len(intelligence.upi_ids) > 0
        assert "winner@paytm" in [upi.upi_id for upi in intelligence.upi_ids]

    @pytest.mark.asyncio
    async def test_extract_bank_account(self, extraction_service):
        """Test bank account extraction."""
        message = "Transfer to account number 123456789012"
        intelligence = await extraction_service.extract_intelligence(message)
        
        assert len(intelligence.bank_accounts) > 0
        assert any(acc.account_number == "123456789012" for acc in intelligence.bank_accounts)

    @pytest.mark.asyncio
    async def test_extract_phishing_url(self, extraction_service):
        """Test phishing URL extraction."""
        message = "Click here: http://secure-bank-verify.com/login"
        intelligence = await extraction_service.extract_intelligence(message)
        
        assert len(intelligence.phishing_urls) > 0
        assert any("secure-bank-verify.com" in url.domain for url in intelligence.phishing_urls)

    @pytest.mark.asyncio
    async def test_extract_phone_number(self, extraction_service):
        """Test phone number extraction."""
        message = "Call me at +91-9876543210"
        intelligence = await extraction_service.extract_intelligence(message)
        
        assert len(intelligence.phone_numbers) > 0

    @pytest.mark.asyncio
    async def test_extract_multiple_types(self, extraction_service):
        """Test extraction of multiple intelligence types."""
        message = "Send Rs. 500 to winner@paytm or call +91-9876543210"
        intelligence = await extraction_service.extract_intelligence(message)
        
        assert len(intelligence.upi_ids) > 0 or len(intelligence.phone_numbers) > 0

    @pytest.mark.asyncio
    async def test_no_intelligence_in_legitimate_message(self, extraction_service):
        """Test that legitimate messages have no extracted intelligence."""
        message = "Hi, how are you today?"
        intelligence = await extraction_service.extract_intelligence(message)
        
        total_intel = (
            len(intelligence.bank_accounts) +
            len(intelligence.upi_ids) +
            len(intelligence.phishing_urls) +
            len(intelligence.phone_numbers)
        )
        assert total_intel == 0

    def test_extract_domain_from_url(self, extraction_service):
        """Test domain extraction from URL."""
        url = "https://example.com/path"
        domain = extraction_service._extract_domain(url)
        assert domain == "example.com"

    def test_get_bank_name_from_ifsc(self, extraction_service):
        """Test bank name extraction from IFSC."""
        assert extraction_service._get_bank_name_from_ifsc("HDFC0001234") == "HDFC Bank"
        assert extraction_service._get_bank_name_from_ifsc("SBIN0001234") == "State Bank of India"
        assert extraction_service._get_bank_name_from_ifsc("ICIC0001234") == "ICICI Bank"
