"""Authentication middleware for API key validation."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
from app.utils.logger import app_logger

# API Key header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(authorization: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the Authorization header.

    Args:
        authorization: Authorization header value (expected format: "Bearer <api_key>")

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if authorization is None:
        app_logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Provide it in the Authorization header as 'Bearer <your_api_key>'.",
        )

    # Extract the key from "Bearer <key>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        app_logger.warning(f"Invalid Authorization header format: {authorization[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer <your_api_key>'.",
        )

    api_key = parts[1]

    # Validate the API key
    if api_key != settings.api_key:
        app_logger.warning(f"Invalid API key provided: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    app_logger.debug("API key validated successfully")
    return api_key
