"""Scam detection service using multi-layered approach."""

from typing import List, Tuple
from app.services.llm import llm_service
from app.utils.patterns import ScamPatterns, extract_matches
from app.utils.logger import app_logger
from app.config import settings


class ScamDetectionService:
    """Service for detecting scam intent in messages."""

    # Scam categories
    SCAM_CATEGORIES = [
        "financial_fraud",
        "phishing",
        "lottery_prize",
        "tech_support",
        "romance",
        "legitimate",
    ]

    # System prompt for LLM classification
    CLASSIFICATION_SYSTEM_PROMPT = """You are an expert at detecting scam messages. Analyze the message and classify it into one of the provided categories.
- financial_fraud: Requests for money, bank details, investment schemes
- phishing: Suspicious links, credential requests, fake login pages
- lottery_prize: Claims of winning prizes, lottery scams
- tech_support: Fake technical support, remote access requests
- romance: Emotional manipulation leading to financial requests
- legitimate: Normal, non-scam messages
"""

    def __init__(self):
        self.threshold = settings.scam_confidence_threshold
        self.high_threshold = settings.high_confidence_threshold

    async def detect_scam(self, message: str, conversation_history: List[str] = None) -> Tuple[bool, float, str]:
        """
        Detect if a message is a scam using multi-layered approach.

        Args:
            message: The message to analyze
            conversation_history: Previous messages for context

        Returns:
            Tuple of (is_scam, confidence, scam_type)
        """
        # Layer 1: Pattern-based detection (fast)
        pattern_score, pattern_type = self._pattern_detection(message)
        app_logger.debug(f"Pattern detection: score={pattern_score}, type={pattern_type}")

        if pattern_score >= 0.9:
            # High confidence from patterns
            return True, pattern_score, pattern_type

        # Layer 2: LLM-based classification (accurate)
        llm_category, llm_confidence = await self._llm_classification(message, conversation_history)
        app_logger.debug(f"LLM classification: category={llm_category}, confidence={llm_confidence}")

        # Determine if it's a scam
        is_scam = llm_category != "legitimate" and llm_confidence >= self.threshold

        # Combine scores
        combined_confidence = max(pattern_score, llm_confidence)

        return is_scam, combined_confidence, llm_category

    def _pattern_detection(self, message: str) -> Tuple[float, str]:
        """
        Detect scam using pattern matching.

        Returns:
            Tuple of (confidence, scam_type)
        """
        message_lower = message.lower()
        total_score = 0.0
        detected_types = []

        # Check each category
        if extract_matches(message, ScamPatterns.URGENCY_PATTERNS):
            total_score += 0.3

        if extract_matches(message, ScamPatterns.FINANCIAL_PATTERNS):
            total_score += 0.4
            detected_types.append("financial_fraud")

        if extract_matches(message, ScamPatterns.PHISHING_PATTERNS):
            total_score += 0.4
            detected_types.append("phishing")

        if extract_matches(message, ScamPatterns.LOTTERY_PATTERNS):
            total_score += 0.4
            detected_types.append("lottery_prize")

        if extract_matches(message, ScamPatterns.TECH_SUPPORT_PATTERNS):
            total_score += 0.4
            detected_types.append("tech_support")

        if extract_matches(message, ScamPatterns.ROMANCE_PATTERNS):
            total_score += 0.3
            detected_types.append("romance")

        # Cap the score at 1.0
        total_score = min(total_score, 1.0)

        scam_type = detected_types[0] if detected_types else "unknown"

        return total_score, scam_type

    async def _llm_classification(
        self,
        message: str,
        conversation_history: List[str] = None,
    ) -> Tuple[str, float]:
        """
        Classify message using LLM.

        Returns:
            Tuple of (category, confidence)
        """
        # Build context from history
        context = ""
        if conversation_history:
            context = "\n".join([f"- {msg}" for msg in conversation_history[-5:]])  # Last 5 messages
            context = f"\nPrevious messages:\n{context}\n\n"

        prompt = f"""{context}Current message: {message}

Classify this message as one of: {", ".join(self.SCAM_CATEGORIES)}
"""

        category, confidence = await llm_service.classify(
            text=prompt,
            categories=self.SCAM_CATEGORIES,
            system_prompt=self.CLASSIFICATION_SYSTEM_PROMPT,
        )

        return category, confidence

    def is_high_confidence(self, confidence: float) -> bool:
        """Check if confidence is above high threshold."""
        return confidence >= self.high_threshold


# Global service instance
scam_detection_service = ScamDetectionService()
