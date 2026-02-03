"""Unit tests for pattern matching utilities."""

import pytest
from app.utils.patterns import (
    ScamPatterns,
    ExtractionPatterns,
    extract_matches,
    is_phishing_url,
)


class TestScamPatterns:
    """Tests for scam detection patterns."""

    def test_urgency_pattern_act_now(self):
        """Test urgency pattern with 'act now'."""
        text = "Act now! This offer expires today."
        matches = extract_matches(text, ScamPatterns.URGENCY_PATTERNS)
        assert len(matches) > 0

    def test_urgency_pattern_immediately(self):
        """Test urgency pattern with 'immediately'."""
        text = "You must respond immediately."
        matches = extract_matches(text, ScamPatterns.URGENCY_PATTERNS)
        assert len(matches) > 0

    def test_financial_pattern_bank_account(self):
        """Test financial pattern with bank account."""
        text = "Please share your bank account number."
        matches = extract_matches(text, ScamPatterns.FINANCIAL_PATTERNS)
        assert len(matches) > 0

    def test_financial_pattern_transfer(self):
        """Test financial pattern with transfer."""
        text = "Transfer Rs. 5000 to claim your prize."
        matches = extract_matches(text, ScamPatterns.FINANCIAL_PATTERNS)
        assert len(matches) > 0

    def test_phishing_pattern_click_here(self):
        """Test phishing pattern with click here."""
        text = "Click here to verify your account."
        matches = extract_matches(text, ScamPatterns.PHISHING_PATTERNS)
        assert len(matches) > 0

    def test_phishing_pattern_login(self):
        """Test phishing pattern with login."""
        text = "Your account will be blocked. Login here: http://fake-bank.com"
        matches = extract_matches(text, ScamPatterns.PHISHING_PATTERNS)
        assert len(matches) > 0

    def test_lottery_pattern_congratulations(self):
        """Test lottery pattern with congratulations."""
        text = "Congratulations! You've won Rs. 50,000!"
        matches = extract_matches(text, ScamPatterns.LOTTERY_PATTERNS)
        assert len(matches) > 0

    def test_lottery_pattern_prize(self):
        """Test lottery pattern with prize."""
        text = "You have been selected for a cash prize."
        matches = extract_matches(text, ScamPatterns.LOTTERY_PATTERNS)
        assert len(matches) > 0

    def test_tech_support_pattern_virus(self):
        """Test tech support pattern with virus."""
        text = "Your computer has a virus. Call us now."
        matches = extract_matches(text, ScamPatterns.TECH_SUPPORT_PATTERNS)
        assert len(matches) > 0

    def test_tech_support_pattern_remote_access(self):
        """Test tech support pattern with remote access."""
        text = "Please allow remote access to fix the issue."
        matches = extract_matches(text, ScamPatterns.TECH_SUPPORT_PATTERNS)
        assert len(matches) > 0

    def test_romance_pattern_money_transfer(self):
        """Test romance pattern with money transfer."""
        text = "Please send money for my hospital bills."
        matches = extract_matches(text, ScamPatterns.ROMANCE_PATTERNS)
        assert len(matches) > 0

    def test_legitimate_message_no_patterns(self):
        """Test that legitimate message has no scam patterns."""
        text = "Hi, how are you doing today? Let's meet for coffee."
        all_patterns = (
            ScamPatterns.URGENCY_PATTERNS +
            ScamPatterns.FINANCIAL_PATTERNS +
            ScamPatterns.PHISHING_PATTERNS +
            ScamPatterns.LOTTERY_PATTERNS +
            ScamPatterns.TECH_SUPPORT_PATTERNS +
            ScamPatterns.ROMANCE_PATTERNS
        )
        matches = extract_matches(text, all_patterns)
        assert len(matches) == 0


class TestExtractionPatterns:
    """Tests for intelligence extraction patterns."""

    def test_upi_pattern_paytm(self):
        """Test UPI pattern with PayTM."""
        text = "Send payment to winner@paytm"
        matches = extract_matches(text, ExtractionPatterns.UPI_PATTERNS)
        assert "winner@paytm" in matches

    def test_upi_pattern_gpay(self):
        """Test UPI pattern with GPay."""
        text = "My UPI is user@gpay"
        matches = extract_matches(text, ExtractionPatterns.UPI_PATTERNS)
        assert "user@gpay" in matches

    def test_bank_account_pattern(self):
        """Test bank account pattern."""
        text = "My account number is 123456789012"
        matches = extract_matches(text, ExtractionPatterns.BANK_ACCOUNT_PATTERNS)
        assert any("123456789012" in match for match in matches)

    def test_ifsc_pattern(self):
        """Test IFSC code pattern."""
        text = "IFSC code is SBIN0001234"
        matches = extract_matches(text, ExtractionPatterns.IFSC_PATTERNS)
        assert "SBIN0001234" in matches

    def test_phone_pattern_indian(self):
        """Test Indian phone number pattern."""
        text = "Call me at +91-9876543210"
        matches = extract_matches(text, ExtractionPatterns.PHONE_PATTERNS)
        assert any("9876543210" in match for match in matches)

    def test_url_pattern_http(self):
        """Test HTTP URL pattern."""
        text = "Visit http://example.com"
        matches = extract_matches(text, ExtractionPatterns.URL_PATTERNS)
        assert "http://example.com" in matches

    def test_url_pattern_https(self):
        """Test HTTPS URL pattern."""
        text = "Visit https://secure-login.com"
        matches = extract_matches(text, ExtractionPatterns.URL_PATTERNS)
        assert "https://secure-login.com" in matches

    def test_url_pattern_bitly(self):
        """Test short URL pattern."""
        text = "Click here: bit.ly/scam123"
        matches = extract_matches(text, ExtractionPatterns.URL_PATTERNS)
        assert "bit.ly/scam123" in matches


class TestPhishingDetection:
    """Tests for phishing URL detection."""

    def test_phishing_url_verify(self):
        """Test phishing detection with 'verify' keyword."""
        assert is_phishing_url("http://secure-verify.com") is True

    def test_phishing_url_login(self):
        """Test phishing detection with 'login' keyword."""
        assert is_phishing_url("http://bank-login.com") is True

    def test_phishing_url_bitly(self):
        """Test phishing detection with bit.ly."""
        assert is_phishing_url("http://bit.ly/scam") is True

    def test_non_phishing_url(self):
        """Test that legitimate URL is not flagged as phishing."""
        assert is_phishing_url("http://example.com") is False

    def test_non_phishing_url_google(self):
        """Test that Google URL is not flagged as phishing."""
        assert is_phishing_url("https://google.com") is False
