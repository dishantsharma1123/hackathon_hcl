"""Intelligence extraction service."""

import re
from typing import List, Dict
from app.utils.patterns import ScamPatterns  # Assuming regex patterns exist here

class ExtractionService:
    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts all intelligence fields required by the hackathon.
        """
        return {
            "bankAccounts": self._extract_regex(text, r"\b\d{9,18}\b"), # Basic Account Regex
            "upiIds": self._extract_regex(text, r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"),
            "phishingLinks": self._extract_regex(text, r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"),
            "phoneNumbers": self._extract_regex(text, r"(\+91[\-\s]?)?[6-9]\d{9}"),
            "suspiciousKeywords": self._extract_keywords(text)
        }

    def _extract_regex(self, text: str, pattern: str) -> List[str]:
        return list(set(re.findall(pattern, text)))

    def _extract_keywords(self, text: str) -> List[str]:
        # Simple keyword matching based on known scam patterns
        keywords = ["urgent", "verify", "blocked", "kyc", "suspend", "lottery", "winner"]
        found = [k for k in keywords if k in text.lower()]
        return list(set(found))

extraction_service = ExtractionService()