import os
from sqlalchemy import create_engine, Column, Integer, Text, JSON, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

# Database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/nexus_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # Will store vector as list for now, or use pgvector type if available
    category = Column(Text, index=True)
    info = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class AIProviderConfig(Base):
    __tablename__ = "ai_provider_config"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(Text, nullable=False, default="openrouter")
    base_url = Column(Text, nullable=False, default="https://openrouter.ai/api/v1/chat/completions")
    api_key = Column(Text, nullable=False, default="")
    model = Column(Text, nullable=False, default="openrouter/free")
    fallback_models = Column(JSON, nullable=False, default=list)
    referer = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    extra_headers = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
