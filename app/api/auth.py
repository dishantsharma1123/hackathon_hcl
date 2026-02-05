"""Authentication dependency using x-api-key header."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

# Define API Key Header Scheme
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate the x-api-key header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing x-api-key header"
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key