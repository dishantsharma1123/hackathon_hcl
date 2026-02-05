"""Main Conversation API Handler."""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
import httpx
from app.models.conversation import ConversationRequest, AgentResponse, CallbackPayload, ExtractedIntelligence
from app.api.auth import verify_api_key
from app.services.scam_detection import scam_detection_service
from app.services.llm import llm_service
from app.services.extraction import extraction_service
from app.config import settings
from app.utils.logger import app_logger

router = APIRouter()

async def send_guvi_callback(payload: CallbackPayload):
    """Background task to send results to GUVI."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.guvi_callback_url,
                json=payload.model_dump(),
                timeout=10.0
            )
            app_logger.info(f"GUVI Callback Status: {response.status_code} | Body: {response.text}")
    except Exception as e:
        app_logger.error(f"Failed to send GUVI callback: {e}")

@router.post("/process", response_model=AgentResponse)
async def process_conversation(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Main Hackathon Endpoint.
    1. Detects Scam.
    2. Engages Agent if scam detected.
    3. Extracts Intelligence.
    4. Sends Async Callback to GUVI.
    """
    try:
        current_text = request.message.text
        
        # 1. Detect Scam
        is_scam, confidence, scam_type = await scam_detection_service.detect_scam(current_text)
        
        # 2. Extract Intelligence
        intelligence_data = extraction_service.extract_all(current_text)
        
        reply_text = ""
        
        if is_scam:
            # 3. Generate Agent Response (Persona-based)
            # We construct a history string for the LLM
            history_context = [
                {"role": "user" if msg.sender == "scammer" else "assistant", "content": msg.text}
                for msg in request.conversationHistory
            ]
            
            # Add current message
            history_context.append({"role": "user", "content": current_text})
            
            reply_text = await llm_service.generate_scambait_response(
                history=history_context,
                scam_type=scam_type
            )
            
            # 4. Prepare Callback Payload
            # Calculate total messages: History + Current + Reply
            total_messages = len(request.conversationHistory) + 2
            
            payload = CallbackPayload(
                sessionId=request.sessionId,
                scamDetected=True,
                totalMessagesExchanged=total_messages,
                extractedIntelligence=ExtractedIntelligence(**intelligence_data),
                agentNotes=f"Detected {scam_type} with confidence {confidence}. Engaged to extract data."
            )
            
            # 5. Queue Background Callback
            background_tasks.add_task(send_guvi_callback, payload)
            
        else:
            # If not a scam, politelty decline or ignore
            reply_text = "I am not interested. Please do not contact me again."

        return AgentResponse(
            status="success",
            reply=reply_text
        )

    except Exception as e:
        app_logger.error(f"Error processing request: {e}")
        # Even on error, try to return a valid JSON structure if possible, or 500
        raise HTTPException(status_code=500, detail=str(e))