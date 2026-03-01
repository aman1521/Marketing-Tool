from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class GenesisState(Base):
    """
    Active State Table. Represents the live, active identity of the business unit.
    Constantly overwritten dynamically during safely validated mutations.
    """
    __tablename__ = 'genesis_state'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, unique=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Profile JSON Cache
    profile_data = Column(JSON, nullable=False)
    
    # Goals JSON Cache
    goals_data = Column(JSON, nullable=False)
    
    # Constraints JSON Cache
    constraints_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GenesisHistory(Base):
    """
    Append-Only Versioning Store representing exact point-in-time constraints.
    Prevents historical loss and ensures auditing fidelity.
    """
    __tablename__ = 'genesis_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    
    profile_snapshot = Column(JSON, nullable=False)
    goals_snapshot = Column(JSON, nullable=False)
    constraints_snapshot = Column(JSON, nullable=False)
    
    changed_by = Column(String, nullable=False)
    change_reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
