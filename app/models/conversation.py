"""Pydantic models for API Request/Response strictly adhering to Hackathon guidelines."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Sub-models for Input ---

class MessageContent(BaseModel):
    sender: str  # "scammer" or "user"
    text: str
    timestamp: int

class RequestMetadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

# --- Main Request Model ---

class ConversationRequest(BaseModel):
    sessionId: str
    message: MessageContent
    conversationHistory: List[MessageContent] = []
    metadata: Optional[RequestMetadata] = None

# --- Main Response Model ---

class AgentResponse(BaseModel):
    status: str  # "success"
    reply: str

# --- Callback Payload Model (For GUVI) ---

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class CallbackPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str