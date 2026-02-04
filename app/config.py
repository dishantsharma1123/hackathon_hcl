"""Configuration management for the Agentic Honey-Pot System."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_key: str = "test_api_key_12345"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Provider Configuration
    llm_provider: str = "openrouter"
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_fallback_model: str = "mistral"
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_fallback_model: str = "mistralai/mistral-7b-instruct:free"

    # --- NEW: Detection Configuration ---
    # The BERT model to use for scam detection
    scam_model_name: str = "mrm8488/bert-tiny-finetuned-sms-spam-detection"
    
    # Confidence thresholds
    scam_confidence_threshold: float = 0.7
    high_confidence_threshold: float = 0.9
    
    # Pattern matching threshold (if patterns score higher than this, it's a scam)
    pattern_match_threshold: float = 0.3

    # Agent Configuration
    max_conversation_turns: int = 20
    response_delay_min: float = 1.0
    response_delay_max: float = 3.0

    # Database
    database_url: str = "sqlite:///./honeypot.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()