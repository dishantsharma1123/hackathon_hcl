"""Main FastAPI application for the Agentic Honey-Pot System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import app_logger
from app.api import conversation_router, health_router
from app.database import init_db

# Create FastAPI application
app = FastAPI(
    title="Agentic Honey-Pot System",
    description="AI-powered system for detecting scams and extracting intelligence from scammers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(conversation_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    app_logger.info("Starting Agentic Honey-Pot System...")
    
    # Initialize database
    init_db()
    app_logger.info("Database initialized")
    
    app_logger.info(f"API running on {settings.api_host}:{settings.api_port}")
    app_logger.info(f"LLM Provider: {settings.llm_provider}")
    if settings.llm_provider == "openrouter":
        app_logger.info(f"OpenRouter model: {settings.openrouter_model}")
    else:
        app_logger.info(f"Ollama host: {settings.ollama_host}")
        app_logger.info(f"Ollama model: {settings.ollama_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    app_logger.info("Shutting down Agentic Honey-Pot System...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Agentic Honey-Pot System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
