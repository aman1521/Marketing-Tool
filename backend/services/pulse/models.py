from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PulseRegistryModel(Base):
    """
    Central repository for tracking Pulse Gravity states chronologically.
    Allows Captain systems to access cached macro modifiers without re-calculating
    heavy macro aggregations constantly.
    """
    __tablename__ = 'pulse_signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    
    # Core Pulses
    seasonality_index = Column(Float, nullable=False)
    demand_shift_score = Column(Float, nullable=False)
    volatility_index = Column(Float, nullable=False)
    macro_drift_score = Column(Float, nullable=False)
    market_phase = Column(String, nullable=False)
    confidence_modifier = Column(Float, nullable=False)
    
    # Store complete computational raw output dynamically for ML
    pulse_blob = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
