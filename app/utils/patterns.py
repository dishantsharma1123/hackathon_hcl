"""Regex patterns for scam detection and intelligence extraction."""

import re
from typing import List, Pattern


class ScamPatterns:
    """Regex patterns for detecting scam messages."""

    # Urgency indicators
    URGENCY_PATTERNS: List[Pattern] = [
        re.compile(r"\b(urgent|immediately|right now|asap|today only|limited time|act now|don't wait|hurry)\b", re.IGNORECASE),
        re.compile(r"\b(expiring|expires soon|last chance|final notice|deadline|time is running out)\b", re.IGNORECASE),
    ]

    # Financial scam indicators
    FINANCIAL_PATTERNS: List[Pattern] = [
        re.compile(r"\b(bank account|account number|ifsc code|transfer|wire|deposit|payment|money|cash|rupees|rs\.|₹)\b", re.IGNORECASE),
        re.compile(r"\b(investment|profit|return|double|triple|guaranteed|risk-free|scheme)\b", re.IGNORECASE),
        re.compile(r"\b(advance fee|registration fee|processing fee|security deposit)\b", re.IGNORECASE),
    ]

    # Phishing indicators
    PHISHING_PATTERNS: List[Pattern] = [
        re.compile(r"\b(click here|verify|confirm|update|login|sign in|account suspended|security alert)\b", re.IGNORECASE),
        re.compile(r"\b(password|otp|pin|cvv|card number|credit card|debit card)\b", re.IGNORECASE),
        re.compile(r"https?://[^\s]+(verify|secure|login|account|bank|update)[^\s]*", re.IGNORECASE),
    ]

    # Lottery/Prize scam indicators
    LOTTERY_PATTERNS: List[Pattern] = [
        re.compile(r"\b(lottery|prize|winner|won|jackpot|lucky draw|reward|gift)\b", re.IGNORECASE),
        re.compile(r"\b(claim|collect|receive your|congratulations|you have been selected)\b", re.IGNORECASE),
    ]

    # Tech support scam indicators
    TECH_SUPPORT_PATTERNS: List[Pattern] = [
        re.compile(r"\b(virus|malware|hack|security breach|compromised|suspicious activity)\b", re.IGNORECASE),
        re.compile(r"\b(remote access|teamviewer|anydesk|support|technician|microsoft|apple)\b", re.IGNORECASE),
    ]

    # Romance scam indicators
    ROMANCE_PATTERNS: List[Pattern] = [
        re.compile(r"\b(money transfer|help me|emergency|hospital|sick|family problem)\b", re.IGNORECASE),
        re.compile(r"\b(gift card|bitcoin|crypto|western union|moneygram)\b", re.IGNORECASE),
    ]


class ExtractionPatterns:
    """Regex patterns for extracting intelligence from conversations."""

    # Bank account patterns
    BANK_ACCOUNT_PATTERNS: List[Pattern] = [
        # Simple pattern to match account numbers directly
        re.compile(r"\b\d{9,18}\b"),
        # Pattern with account/acc keywords
        re.compile(r"\b(account|acc|a/c)\s*(no|number|#)?\s*:?\s*(\d{9,18})\b", re.IGNORECASE),
        re.compile(r"\b(\d{9,18})\s*(is my|is\s)\s*(account|acc|a/c)\s*(no|number|#)?\b", re.IGNORECASE),
    ]

    # IFSC code patterns
    IFSC_PATTERNS: List[Pattern] = [
        re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),  # Standard IFSC format
        re.compile(r"\b(ifsc|ifsc code)\s*:?\s*([A-Z]{4}0[A-Z0-9]{6})\b", re.IGNORECASE),
    ]

    # UPI ID patterns
    UPI_PATTERNS: List[Pattern] = [
        re.compile(r"\b[\w.-]+@(paytm|gpay|phonepe|ybl|axis|icici|hdfc|sbi|kotak|upi|oksbi)\b", re.IGNORECASE),
    ]

    # Phone number patterns (India)
    PHONE_PATTERNS: List[Pattern] = [
        re.compile(r"\b(\+91[-\s]?)?[6-9]\d{9}\b"),  # Indian mobile numbers
        re.compile(r"\b(\+91[-\s]?)?\d{4}[-\s]?\d{3}[-\s]?\d{3}\b"),  # Various formats
        re.compile(r"\b(\+91[-\s]?)?\d{10}\b"),  # 10 digit format with country code
        re.compile(r"\b(phone|mobile|contact|call|whatsapp)\s*:?\s*(\+?\d[\d\s\-\(\)]{9,15})\b", re.IGNORECASE),
    ]

    # URL patterns
    URL_PATTERNS: List[Pattern] = [
        re.compile(r"https?://[^\s<>\"']+"),
        re.compile(r"(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s<>\"']*"),
        re.compile(r"bit\.ly/[^\s<>\"']+"),  # Bit.ly short URLs
    ]

    # Phishing URL indicators
    PHISHING_DOMAIN_INDICATORS: List[str] = [
        "verify", "secure", "login", "account", "bank", "update", "confirm",
        "support", "help", "service", "customer", "official", "genuine",
        "bit.ly", "tinyurl", "short.link", "goo.gl", "t.co",
    ]


def extract_matches(text: str, patterns: List[Pattern]) -> List[str]:
    """Extract all matches from text using the provided patterns."""
    matches = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            # Get the full match
            matches.add(match.group(0))
    return list(matches)


def is_phishing_url(url: str) -> bool:
    """Check if a URL has phishing indicators."""
    url_lower = url.lower()
    for indicator in ExtractionPatterns.PHISHING_DOMAIN_INDICATORS:
        if indicator in url_lower:
            return True
    return False
