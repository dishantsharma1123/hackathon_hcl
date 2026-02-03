"""Database configuration and models for the Agentic Honey-Pot System."""

from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from app.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Conversation(Base):
    """Database model for conversations."""
    
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scam_detected = Column(Boolean, default=False)
    agent_active = Column(Boolean, default=False)
    persona_type = Column(String(50), nullable=True)
    conversation_turns = Column(Integer, default=0)
    engagement_duration_seconds = Column(Integer, default=0)


class Message(Base):
    """Database model for messages."""
    
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    scam_confidence = Column(Float, nullable=True)
    extracted_intelligence = Column(JSON, nullable=True)


class Intelligence(Base):
    """Database model for extracted intelligence."""
    
    __tablename__ = "intelligence"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, nullable=False, index=True)
    intelligence_type = Column(String(50), nullable=False)  # 'bank_account', 'upi_id', 'phishing_url', 'phone'
    value = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
