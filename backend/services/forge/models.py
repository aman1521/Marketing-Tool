from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ExperimentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    KILLED = "killed"
    PROMOTED = "promoted"

class ExperimentRegistryModel(Base):
    """
    Central log of all structured experimentation hypotheses, 
    variation configurations, and final statistical outcomes.
    """
    __tablename__ = 'forge_experiments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String, index=True, unique=True, nullable=False)
    company_id = Column(String, index=True, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)
    
    hypothesis = Column(String, nullable=False)
    experiment_type = Column(String, nullable=False) # e.g. BUDGET_SPLIT, CREATIVE_ANGLE
    
    # JSON containing definitions for 'control' vs 'variation_1', etc.
    variations_blob = Column(JSON, nullable=False)
    
    # Financial governance tracking
    sandbox_budget_allocated = Column(Float, nullable=False)
    
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.PENDING, index=True)
    winner_id = Column(String, nullable=True) # Variation ID if successful
    
    # Results metadata (p-values, lift, etc.)
    statistical_summary = Column(JSON, nullable=True)
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
