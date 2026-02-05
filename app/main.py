from fastapi import FastAPI
from app.api.conversation import router as conversation_router
from app.config import settings

app = FastAPI(title="Agentic Honey-Pot API")

# Mount the router. 
# The hackathon might expect the endpoint at root or a specific path.
# We will expose it at /api/v1/process based on our router logic.
# If they post to root, you might need to adjust this.
app.include_router(conversation_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "active", "provider": settings.llm_provider}