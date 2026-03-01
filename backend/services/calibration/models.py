from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ParameterSuggestion(Base):
    """
    Log of exact threshold changes recommended by the Calibration engine.
    Must be approved by Genesis to enter live routing.
    """
    __tablename__ = 'calibration_suggestions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    
    parameter_name = Column(String, nullable=False) # e.g. "fatigue_score_threshold"
    current_value = Column(Float, nullable=False)
    suggested_value = Column(Float, nullable=False)
    
    # Justification vectors
    historical_lift_detected = Column(Float, nullable=True) 
    penalty_reduced = Column(Float, nullable=True) 
    
    status = Column(String, default="PENDING_GENESIS_APPROVAL") # PENDING, APPROVED, REJECTED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
