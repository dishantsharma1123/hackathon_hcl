"""Main conversation endpoint for the honey-pot system."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.auth import verify_api_key
from app.models.conversation import (
    ConversationRequest,
    ConversationResponse,
    EngagementMetrics,
    Message,
)
from app.models.intelligence import ExtractedIntelligence
from app.services.scam_detection import scam_detection_service
from app.services.extraction import intelligence_extraction_service
from app.agents.agent import agent_service
from app.database import get_db, Conversation as DBConversation, Message as DBMessage
from sqlalchemy.orm import Session
from app.utils.logger import app_logger
from datetime import datetime

router = APIRouter()


@router.post("/api/v1/conversation/message", response_model=ConversationResponse)
async def process_message(
    request: ConversationRequest,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Main endpoint to process incoming scam messages and generate agent responses.
    
    Args:
        request: Conversation request with message and history
        api_key: Validated API key
        db: Database session

    Returns:
        ConversationResponse with agent response, scam detection, and extracted intelligence
    """
    try:
        app_logger.info(f"Processing message for conversation {request.conversation_id}")
        
        # Extract conversation history as strings
        conversation_history = [msg.message for msg in request.conversation_history]
        
        # Step 1: Detect scam intent
        is_scam, confidence, scam_type = await scam_detection_service.detect_scam(
            message=request.message,
            conversation_history=conversation_history,
        )
        
        app_logger.info(f"Scam detection: is_scam={is_scam}, confidence={confidence:.2f}, type={scam_type}")
        
        # Step 2: Extract intelligence
        extracted_intelligence = await intelligence_extraction_service.extract_intelligence(
            message=request.message,
            conversation_history=conversation_history,
        )
        
        # Step 3: Generate agent response if scam detected
        agent_response = ""
        agent_active = False
        
        if is_scam:
            agent_active = True
            agent_response = await agent_service.generate_response(
                message=request.message,
                conversation_id=str(request.conversation_id),
                scam_type=scam_type,
                conversation_history=conversation_history,
                extracted_intelligence={
                    "bank_accounts": [acc.account_number for acc in extracted_intelligence.bank_accounts],
                    "upi_ids": [upi.upi_id for upi in extracted_intelligence.upi_ids],
                    "phishing_urls": [url.url for url in extracted_intelligence.phishing_urls],
                    "phone_numbers": [phone.number for phone in extracted_intelligence.phone_numbers],
                },
            )
        else:
            # Polite decline for non-scam messages
            agent_response = "I'm sorry, I'm not interested in this. Thank you for reaching out."
        
        # Step 4: Get engagement metrics
        metrics_data = agent_service.get_engagement_metrics(str(request.conversation_id))
        engagement_metrics = EngagementMetrics(**metrics_data)
        
        # Step 5: Save to database
        _save_conversation_to_db(
            db=db,
            conversation_id=str(request.conversation_id),
            request=request,
            response=agent_response,
            is_scam=is_scam,
            confidence=confidence,
            agent_active=agent_active,
            extracted_intelligence=extracted_intelligence,
            engagement_metrics=engagement_metrics,
        )
        
        # Step 6: Build response
        response = ConversationResponse(
            conversation_id=request.conversation_id,
            response=agent_response,
            scam_detected=is_scam,
            agent_active=agent_active,
            engagement_metrics=engagement_metrics,
            extracted_intelligence=extracted_intelligence,
            timestamp=datetime.utcnow(),
        )
        
        app_logger.info(f"Successfully processed message for conversation {request.conversation_id}")
        return response
        
    except Exception as e:
        app_logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the message: {str(e)}",
        )


@router.get("/api/v1/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Retrieve full conversation history for a given conversation ID.
    
    Args:
        conversation_id: Conversation identifier
        api_key: Validated API key
        db: Database session

    Returns:
        Conversation details with all messages
    """
    # Get conversation
    db_conv = db.query(DBConversation).filter(
        DBConversation.id == conversation_id
    ).first()
    
    if not db_conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Get messages
    db_messages = db.query(DBMessage).filter(
        DBMessage.conversation_id == conversation_id
    ).order_by(DBMessage.timestamp).all()
    
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in db_messages
    ]
    
    return {
        "conversation_id": db_conv.id,
        "created_at": db_conv.created_at.isoformat(),
        "updated_at": db_conv.updated_at.isoformat(),
        "scam_detected": db_conv.scam_detected,
        "agent_active": db_conv.agent_active,
        "persona_type": db_conv.persona_type,
        "conversation_turns": db_conv.conversation_turns,
        "engagement_duration_seconds": db_conv.engagement_duration_seconds,
        "messages": messages,
    }


@router.post("/api/v1/conversation/new")
async def create_conversation(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Create a new conversation and return its ID.
    
    Args:
        api_key: Validated API key
        db: Database session

    Returns:
        New conversation ID
    """
    import uuid
    
    new_id = str(uuid.uuid4())
    
    db_conv = DBConversation(
        id=new_id,
        scam_detected=False,
        agent_active=False,
        conversation_turns=0,
        engagement_duration_seconds=0,
    )
    
    db.add(db_conv)
    db.commit()
    
    app_logger.info(f"Created new conversation: {new_id}")
    
    return {
        "conversation_id": new_id,
        "message": "New conversation created successfully",
    }


def _save_conversation_to_db(
    db: Session,
    conversation_id: str,
    request: ConversationRequest,
    response: str,
    is_scam: bool,
    confidence: float,
    agent_active: bool,
    extracted_intelligence: ExtractedIntelligence,
    engagement_metrics: EngagementMetrics,
):
    """Save conversation data to database."""
    import json
    
    # Get or create conversation
    db_conv = db.query(DBConversation).filter(
        DBConversation.id == conversation_id
    ).first()
    
    if not db_conv:
        db_conv = DBConversation(
            id=conversation_id,
            scam_detected=is_scam,
            agent_active=agent_active,
            conversation_turns=engagement_metrics.conversation_turns,
            engagement_duration_seconds=engagement_metrics.engagement_duration_seconds,
        )
        db.add(db_conv)
    else:
        db_conv.scam_detected = db_conv.scam_detected or is_scam
        db_conv.agent_active = agent_active
        db_conv.conversation_turns = engagement_metrics.conversation_turns
        db_conv.engagement_duration_seconds = engagement_metrics.engagement_duration_seconds
        db_conv.updated_at = datetime.utcnow()
    
    # Save user message
    db_user_msg = DBMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        timestamp=request.timestamp,
        scam_confidence=confidence,
    )
    db.add(db_user_msg)
    
    # Save assistant message
    db_assistant_msg = DBMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=response,
        timestamp=datetime.utcnow(),
        scam_confidence=confidence,
        extracted_intelligence=extracted_intelligence.model_dump(),
    )
    db.add(db_assistant_msg)
    
    db.commit()
