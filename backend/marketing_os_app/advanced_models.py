from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class EscalationState(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"
    EXPIRED = "expired"
    CONFLICT = "conflict"

class DecisionSpeedRecord(Base):
    """Historical per-loop cycle time record."""
    __tablename__ = "decision_speed_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)

    diagnose_to_strategy_ms   = Column(Float, nullable=True)
    strategy_to_execute_ms    = Column(Float, nullable=True)
    execute_to_drift_eval_ms  = Column(Float, nullable=True)
    escalation_to_approval_ms = Column(Float, nullable=True)
    task_create_to_complete_ms = Column(Float, nullable=True)

    decision_speed_index = Column(Float, nullable=True)   # Weighted composite
    approving_role = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

class AutonomyControlRecord(Base):
    """History of autonomy % adjustments per company."""
    __tablename__ = "autonomy_control_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    previous_pct = Column(Float, nullable=False)
    new_pct = Column(Float, nullable=False)
    trigger = Column(String, nullable=False)   # DRIFT_SPIKE, VOLATILITY, ROLLBACK_RATE, CONFIDENCE_STABLE
    context = Column(JSON, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow, index=True)

class StrategyArchetypeRecord(Base):
    """Reusable intelligence pattern harvested from historical executions."""
    __tablename__ = "strategy_archetypes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(String, unique=True, nullable=False)
    industry = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False)
    aov_tier = Column(String, nullable=False)          # low / mid / high
    creative_archetype = Column(String, nullable=False)
    scaling_band = Column(String, nullable=False)      # conservative / moderate / aggressive

    avg_lift_pct = Column(Float, nullable=False)
    avg_risk_exposure = Column(Float, nullable=False)
    volatility_context = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    sample_count = Column(Integer, nullable=False, default=1)

    first_observed = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
