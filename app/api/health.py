"""Health check endpoint."""

from fastapi import APIRouter, status
from app.services.llm import llm_service
from app.utils.logger import app_logger

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        Health status information
    """
    # Check LLM connection with error handling
    try:
        llm_connected = await llm_service.check_connection()
    except Exception as e:
        app_logger.error(f"Health check LLM connection failed: {e}")
        llm_connected = False
    
    return {
        "status": "healthy",
        "service": "agentic-honeypot",
        "llm_provider": llm_service.provider,
        "llm_connected": llm_connected,
    }
