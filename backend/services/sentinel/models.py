from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ExecutionAuditLog(Base):
    """
    Absolute Traceability Log. Maps versions of Intelligence engines used
    down to the execution decisions and the observed outcome offsets.
    """
    __tablename__ = 'sentinel_execution_audit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)
    execution_id = Column(String, index=True, nullable=False, unique=True)
    
    # Traceability Vectors
    strategy_version = Column(String, nullable=False)
    diagnosis_version = Column(String, nullable=False)
    execution_version = Column(String, nullable=False)
    genesis_version = Column(String, nullable=False)
    
    # Outcome tracking
    action_type = Column(String, nullable=False)
    expected_delta = Column(Float, nullable=True) # Simulated outcome expecting ROI difference
    actual_delta = Column(Float, nullable=True)   # Real outcome after 24h/48h drift monitor
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemAnomalyLog(Base):
    """
    Maps misclassifications and system drift points safely.
    """
    __tablename__ = 'sentinel_anomalies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    anomaly_type = Column(String, nullable=False) # e.g. "FATIGUE_FALSE_POSITIVE"
    severity_label = Column(String, nullable=False)
    details = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
