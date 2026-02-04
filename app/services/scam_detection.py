"""Scam detection service using specialized BERT model."""

from typing import List, Tuple, Dict
from transformers import pipeline
from app.utils.patterns import ScamPatterns, extract_matches
from app.utils.logger import app_logger
from app.config import settings

class ScamDetectionService:
    """Service for detecting scam intent using BERT + Pattern Matching."""

    def __init__(self):
        self.threshold = settings.scam_confidence_threshold
        
        # Initialize the specialized Spam Detection Model
        # using a 'tiny' BERT model to save memory (~15MB size)
        app_logger.info("Loading BERT scam detection model...")
        try:
            self.classifier = pipeline(
                "text-classification", 
                model="mrm8488/bert-tiny-finetuned-sms-spam-detection"
            )
            app_logger.info("BERT model loaded successfully.")
        except Exception as e:
            app_logger.error(f"Failed to load BERT model: {e}")
            self.classifier = None

    async def detect_scam(self, message: str, conversation_history: List[str] = None) -> Tuple[bool, float, str]:
        """
        Detect if a message is a scam.
        
        Returns:
            Tuple of (is_scam, confidence, scam_type)
        """
        # 1. Run Pattern Detection (to guess the TYPE of scam)
        pattern_score, pattern_type = self._pattern_detection(message)
        
        # 2. Run BERT Classification (to confirm IF it is a scam)
        bert_is_scam, bert_confidence = self._bert_analysis(message)
        
        app_logger.info(f"Analysis - Pattern: {pattern_score:.2f} ({pattern_type}) | BERT: {bert_confidence:.2f} (Scam: {bert_is_scam})")

        # Decision Logic:
        # If Pattern is very sure, trust it.
        if pattern_score >= 0.9:
            return True, pattern_score, pattern_type
            
        # Otherwise, trust the BERT model for detection
        is_scam = bert_is_scam and (bert_confidence > self.threshold)
        
        # Determine final type
        # If BERT says scam but patterns didn't find a type, mark as 'general_scam'
        final_type = pattern_type if (is_scam and pattern_type != "unknown") else "general_scam"
        if not is_scam:
            final_type = "legitimate"

        final_confidence = max(pattern_score, bert_confidence) if is_scam else bert_confidence

        return is_scam, final_confidence, final_type

    def _bert_analysis(self, message: str) -> Tuple[bool, float]:
        """Run the BERT spam classifier."""
        if not self.classifier:
            return False, 0.0

        try:
            # Truncate to 512 tokens to prevent crash
            result = self.classifier(message[:512])[0]
            
            # This specific model uses 'LABEL_1' for Spam/Scam and 'LABEL_0' for Ham/Legit
            is_scam = result['label'] == 'LABEL_1'
            score = result['score']
            
            return is_scam, score
        except Exception as e:
            app_logger.error(f"BERT prediction error: {e}")
            return False, 0.0

    def _pattern_detection(self, message: str) -> Tuple[float, str]:
        """
        Detect scam type using keyword patterns.
        Returns: (confidence, scam_type)
        """
        detected_types = []
        total_score = 0.0

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

        scam_type = detected_types[0] if detected_types else "unknown"
        return min(total_score, 1.0), scam_type

# Global instance
scam_detection_service = ScamDetectionService()