"""Configuration management for the Agentic Honey-Pot System."""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_key: str = "test_api_key_12345"  # Ensure this matches the key you submit
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Provider Configuration
    llm_provider: str = "openrouter"
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "google/gemini-2.0-flash-lite-preview-02-05:free"
    
    # Detection Configuration
    scam_confidence_threshold: float = 0.7
    high_confidence_threshold: float = 0.9
    
    # Callback Configuration (Mandatory for Hackathon)
    guvi_callback_url: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

    # Database
    database_url: str = "sqlite:///./honeypot.db"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()