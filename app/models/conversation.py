"""Pydantic models for conversation-related data structures."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class Message(BaseModel):
    """Represents a single message in a conversation."""
    
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class EngagementMetrics(BaseModel):
    """Metrics tracking conversation engagement."""
    
    conversation_turns: int = Field(default=0, description="Number of conversation turns")
    engagement_duration_seconds: int = Field(default=0, description="Total engagement duration in seconds")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")


class ConversationRequest(BaseModel):
    """Request model for the conversation endpoint."""
    
    conversation_id: uuid.UUID = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="Incoming message from scammer")
    sender_id: str = Field(..., description="Sender identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    conversation_history: List[Message] = Field(default_factory=list, description="Previous messages in conversation")


class ConversationResponse(BaseModel):
    """Response model for the conversation endpoint."""
    
    conversation_id: uuid.UUID = Field(..., description="Conversation identifier")
    response: str = Field(..., description="Agent's response message")
    scam_detected: bool = Field(..., description="Whether scam was detected")
    agent_active: bool = Field(..., description="Whether agent is actively engaging")
    engagement_metrics: EngagementMetrics = Field(..., description="Conversation engagement metrics")
    extracted_intelligence: "ExtractedIntelligence" = Field(..., description="Extracted intelligence data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


# Forward reference for ExtractedIntelligence
from .intelligence import ExtractedIntelligence

ConversationResponse.model_rebuild()
