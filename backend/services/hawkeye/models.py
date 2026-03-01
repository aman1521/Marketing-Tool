from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class CreativeType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"

class FatigueStage(str, enum.Enum):
    FRESH = "fresh"
    SCALING = "scaling"
    SATURATED = "saturated"
    FATIGUED = "fatigued"
    DEAD = "dead"

class CreativeRegistryModel(Base):
    """
    Tracks structured mappings of all analyzed Solid Matter (creatives)
    down to the Qdrant Embedding References and abstract hook signatures.
    """
    __tablename__ = 'hawkeye_creatives'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    creative_id = Column(String, index=True, unique=True, nullable=False)
    company_id = Column(String, index=True, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)
    
    creative_type = Column(Enum(CreativeType), nullable=False)
    
    # NLP & Semantic Classifications
    hook_type = Column(String, nullable=True)
    emotional_tone = Column(String, nullable=True)
    offer_type = Column(String, nullable=True)
    
    # Vector Database Link
    embedding_reference = Column(String, nullable=True)
    semantic_cluster_id = Column(String, nullable=True)
    
    # Performance Status
    fatigue_stage = Column(Enum(FatigueStage), default=FatigueStage.FRESH)
    fatigue_score = Column(Float, default=0.0)
    
    # Structured Object Blob of comprehensive NLP/CV scores
    hawkeye_blob = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
