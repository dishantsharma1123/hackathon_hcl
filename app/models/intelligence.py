"""Pydantic models for extracted intelligence data structures."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class ExtractedBankAccount(BaseModel):
    """Represents an extracted bank account."""
    
    account_number: str = Field(..., description="Bank account number")
    ifsc_code: Optional[str] = Field(None, description="IFSC code")
    bank_name: Optional[str] = Field(None, description="Bank name")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")


class ExtractedUPI(BaseModel):
    """Represents an extracted UPI ID."""
    
    upi_id: str = Field(..., description="UPI ID")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")


class ExtractedURL(BaseModel):
    """Represents an extracted URL."""
    
    url: str = Field(..., description="Full URL")
    domain: str = Field(..., description="Domain name")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")


class ExtractedPhone(BaseModel):
    """Represents an extracted phone number."""
    
    number: str = Field(..., description="Phone number")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")


class ExtractedIntelligence(BaseModel):
    """Container for all extracted intelligence."""
    
    bank_accounts: List[ExtractedBankAccount] = Field(default_factory=list, description="Extracted bank accounts")
    upi_ids: List[ExtractedUPI] = Field(default_factory=list, description="Extracted UPI IDs")
    phishing_urls: List[ExtractedURL] = Field(default_factory=list, description="Extracted phishing URLs")
    phone_numbers: List[ExtractedPhone] = Field(default_factory=list, description="Extracted phone numbers")
