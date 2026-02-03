"""Intelligence extraction service from conversations."""

import re
from typing import List, Dict, Any
from app.services.llm import llm_service
from app.utils.patterns import ExtractionPatterns, extract_matches, is_phishing_url
from app.utils.logger import app_logger
from app.models.intelligence import (
    ExtractedBankAccount,
    ExtractedUPI,
    ExtractedURL,
    ExtractedPhone,
    ExtractedIntelligence,
)


class IntelligenceExtractionService:
    """Service for extracting intelligence from conversations."""

    def __init__(self):
        pass

    async def extract_intelligence(
        self,
        message: str,
        conversation_history: List[str] = None,
    ) -> ExtractedIntelligence:
        """
        Extract intelligence from conversation.

        Args:
            message: Current message
            conversation_history: Previous messages

        Returns:
            ExtractedIntelligence object
        """
        # Combine message with recent history for better extraction
        full_text = message
        if conversation_history:
            full_text = " ".join(conversation_history[-3:] + [message])

        intelligence = ExtractedIntelligence()

        # Extract using regex patterns
        intelligence.bank_accounts.extend(self._extract_bank_accounts(full_text))
        intelligence.upi_ids.extend(self._extract_upi_ids(full_text))
        intelligence.phishing_urls.extend(self._extract_urls(full_text))
        intelligence.phone_numbers.extend(self._extract_phones(full_text))

        # Use LLM to verify and enhance extraction
        await self._llm_verification(intelligence, full_text)

        app_logger.info(f"Extracted intelligence: {len(intelligence.bank_accounts)} accounts, "
                       f"{len(intelligence.upi_ids)} UPIs, {len(intelligence.phishing_urls)} URLs, "
                       f"{len(intelligence.phone_numbers)} phones")

        return intelligence

    def _extract_bank_accounts(self, text: str) -> List[ExtractedBankAccount]:
        """Extract bank account numbers."""
        accounts = []
        matches = extract_matches(text, ExtractionPatterns.BANK_ACCOUNT_PATTERNS)
        
        for match in matches:
            # Clean the account number (keep only digits)
            account_number = re.sub(r"[^\d]", "", match)
            if len(account_number) >= 9 and len(account_number) <= 18:
                # Try to find associated IFSC code
                ifsc_match = extract_matches(text, ExtractionPatterns.IFSC_PATTERNS)
                ifsc_code = ifsc_match[0] if ifsc_match else None
                
                # Try to identify bank name from IFSC
                bank_name = self._get_bank_name_from_ifsc(ifsc_code) if ifsc_code else None
                
                accounts.append(ExtractedBankAccount(
                    account_number=account_number,
                    ifsc_code=ifsc_code,
                    bank_name=bank_name,
                    confidence=0.8,
                ))

        return accounts

    def _extract_upi_ids(self, text: str) -> List[ExtractedUPI]:
        """Extract UPI IDs."""
        upi_ids = []
        matches = extract_matches(text, ExtractionPatterns.UPI_PATTERNS)
        
        for match in matches:
            # Clean UPI ID
            upi_id = match.lower().strip()
            if "@" in upi_id:
                upi_ids.append(ExtractedUPI(upi_id=upi_id, confidence=0.9))

        return upi_ids

    def _extract_urls(self, text: str) -> List[ExtractedURL]:
        """Extract URLs and identify phishing ones."""
        urls = []
        matches = extract_matches(text, ExtractionPatterns.URL_PATTERNS)
        
        for match in matches:
            # Clean URL
            url = match.strip()
            if url.startswith("www."):
                url = "https://" + url
            
            # Extract domain
            domain = self._extract_domain(url)
            
            # Check if it's a phishing URL
            is_phishing = is_phishing_url(url)
            confidence = 0.9 if is_phishing else 0.5
            
            urls.append(ExtractedURL(url=url, domain=domain, confidence=confidence))

        return urls

    def _extract_phones(self, text: str) -> List[ExtractedPhone]:
        """Extract phone numbers."""
        phones = []
        matches = extract_matches(text, ExtractionPatterns.PHONE_PATTERNS)
        
        for match in matches:
            # Clean phone number
            phone = re.sub(r"[^\d+]", "", match)
            if len(phone) >= 10:
                phones.append(ExtractedPhone(number=phone, confidence=0.8))

        return phones

    async def _llm_verification(self, intelligence: ExtractedIntelligence, text: str) -> None:
        """Use LLM to verify and enhance extracted intelligence."""
        schema_description = """
{
  "bank_accounts": [{"account_number": "string", "ifsc_code": "string", "bank_name": "string"}],
  "upi_ids": [{"upi_id": "string"}],
  "phishing_urls": [{"url": "string", "domain": "string"}],
  "phone_numbers": [{"number": "string"}]
}
"""
        
        try:
            extracted = await llm_service.extract_json(
                prompt=f"{schema_description}\n\nMessage: {text}",
                system_prompt="Extract bank accounts, UPI IDs, phishing URLs, and phone numbers from the message. Return valid JSON only.",
            )

            # Merge LLM extraction with regex extraction
            if "bank_accounts" in extracted:
                for acc in extracted["bank_accounts"]:
                    if "account_number" in acc:
                        intelligence.bank_accounts.append(ExtractedBankAccount(
                            account_number=acc["account_number"],
                            ifsc_code=acc.get("ifsc_code"),
                            bank_name=acc.get("bank_name"),
                            confidence=0.95,
                        ))

            if "upi_ids" in extracted:
                for upi in extracted["upi_ids"]:
                    if "upi_id" in upi:
                        intelligence.upi_ids.append(ExtractedUPI(upi_id=upi["upi_id"], confidence=0.95))

            if "phishing_urls" in extracted:
                for url_data in extracted["phishing_urls"]:
                    if "url" in url_data:
                        intelligence.phishing_urls.append(ExtractedURL(
                            url=url_data["url"],
                            domain=url_data.get("domain", self._extract_domain(url_data["url"])),
                            confidence=0.95,
                        ))

            if "phone_numbers" in extracted:
                for phone in extracted["phone_numbers"]:
                    if "number" in phone:
                        intelligence.phone_numbers.append(ExtractedPhone(number=phone["number"], confidence=0.95))

        except Exception as e:
            app_logger.warning(f"LLM verification failed: {e}")

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            # Remove protocol
            url = url.replace("https://", "").replace("http://", "")
            # Remove path
            domain = url.split("/")[0]
            # Remove port
            domain = domain.split(":")[0]
            return domain
        except Exception:
            return url

    def _get_bank_name_from_ifsc(self, ifsc: str) -> str:
        """Get bank name from IFSC code."""
        if not ifsc or len(ifsc) < 4:
            return None
        
        bank_code = ifsc[:4].upper()
        bank_map = {
            "HDFC": "HDFC Bank",
            "ICIC": "ICICI Bank",
            "SBIN": "State Bank of India",
            "AXIS": "Axis Bank",
            "KKBK": "Kotak Mahindra Bank",
            "PUNB": "Punjab National Bank",
            "UBIN": "Union Bank of India",
            "BKID": "Bank of India",
            "BARB": "Bank of Baroda",
            "CNRB": "Canara Bank",
        }
        
        return bank_map.get(bank_code)


# Global service instance
intelligence_extraction_service = IntelligenceExtractionService()
