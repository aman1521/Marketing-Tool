"""
Three-Tier Operator Memory System — SQLAlchemy Models
======================================================

Tier 1: Private Operator Memory   (operator-level, full fidelity)
Tier 2: Tenant Memory             (company-level, context-rich)
Tier 3: Global Anonymised Memory  (platform-level, zero PII)

Isolation guarantee:
  Global memory stores NO company_id, operator_id, campaign_id,
  or any other identifiable attribute. Only statistical patterns.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


# ─── Enums ────────────────────────────────────────────────────────────────

class MemoryTier(str, enum.Enum):
    PRIVATE = "private"
    TENANT  = "tenant"
    GLOBAL  = "global"


class EventOutcome(str, enum.Enum):
    WIN     = "win"
    LOSS    = "loss"
    NEUTRAL = "neutral"
    PENDING = "pending"


class ArchetypeStatus(str, enum.Enum):
    CANDIDATE   = "candidate"    # not enough evidence yet
    CONFIRMED   = "confirmed"    # statistically validated
    DEPRECATED  = "deprecated"   # no longer high-performing


# ─── Tier 1: Private Operator Events ─────────────────────────────────────

class PrivateStrategyEvent(Base):
    """Full-fidelity strategy execution event. Operator-private."""
    __tablename__ = "private_strategy_events"

    id              = Column(String,  primary_key=True, default=_uuid)
    operator_id     = Column(String,  index=True,  nullable=False)
    company_id      = Column(String,  index=True,  nullable=False)
    campaign_id     = Column(String,  index=True,  nullable=True)
    strategy_type   = Column(String,  nullable=False)   # scale_budget, pause, creative_refresh
    context_snapshot= Column(JSON,    nullable=True)    # full signal state at decision time
    action_taken    = Column(JSON,    nullable=True)    # what was executed
    outcome         = Column(String,  default=EventOutcome.PENDING)
    lift_delta      = Column(Float,   nullable=True)    # % lift vs baseline
    risk_exposure   = Column(Float,   nullable=True)
    confidence_at   = Column(Float,   nullable=True)
    volatility_at   = Column(Float,   nullable=True)
    qdrant_point_id = Column(String,  nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    resolved_at     = Column(DateTime, nullable=True)


# ─── Tier 2: Tenant Intelligence ─────────────────────────────────────────

class TenantStrategyEvent(Base):
    """Company-level strategy pattern record."""
    __tablename__ = "tenant_strategy_events"

    id              = Column(String,  primary_key=True, default=_uuid)
    company_id      = Column(String,  index=True,  nullable=False)
    strategy_type   = Column(String,  nullable=False)
    industry        = Column(String,  nullable=True)
    aov_tier        = Column(String,  nullable=True)    # low / mid / high
    scaling_band    = Column(String,  nullable=True)    # 0-10k, 10k-50k, 50k+
    context_vector_id= Column(String, nullable=True)    # Qdrant point ref
    outcome         = Column(String,  default=EventOutcome.PENDING)
    lift_delta      = Column(Float,   nullable=True)
    risk_exposure   = Column(Float,   nullable=True)
    success_signal  = Column(Boolean, default=False)
    pattern_hash    = Column(String,  index=True, nullable=True)  # dedup key
    archetype_id    = Column(String,  nullable=True)    # linked archetype
    created_at      = Column(DateTime, default=datetime.utcnow)


# ─── Tier 3: Global Anonymised Patterns ──────────────────────────────────

class GlobalStrategyPattern(Base):
    """
    Anonymised aggregate pattern. ZERO identifiable data.
    company_id, operator_id, campaign_id are NEVER stored here.
    """
    __tablename__ = "global_strategy_patterns"

    id              = Column(String,  primary_key=True, default=_uuid)
    strategy_type   = Column(String,  nullable=False)
    industry_bucket = Column(String,  nullable=True)    # broad bucket only, no name
    aov_tier        = Column(String,  nullable=True)
    scaling_band    = Column(String,  nullable=True)
    avg_lift        = Column(Float,   nullable=True)
    avg_risk        = Column(Float,   nullable=True)
    sample_count    = Column(Integer, default=1)
    confidence      = Column(Float,   nullable=True)    # statistical confidence 0-1
    win_rate        = Column(Float,   nullable=True)
    pattern_fingerprint = Column(String, index=True)    # anon hash of strategy context
    qdrant_point_id = Column(String,  nullable=True)
    first_seen      = Column(DateTime, default=datetime.utcnow)
    last_updated    = Column(DateTime, default=datetime.utcnow)


# ─── Strategy Archetypes ──────────────────────────────────────────────────

class StrategyArchetype(Base):
    """
    Validated repeating strategy pattern with statistical backing.
    Produced by ArchetypeBuilder. Consumed by InfluenceController.
    """
    __tablename__ = "strategy_archetypes"

    id              = Column(String,  primary_key=True, default=_uuid)
    name            = Column(String,  nullable=False)
    tier            = Column(String,  default=MemoryTier.TENANT)  # which tier generated it
    strategy_type   = Column(String,  nullable=False)
    industry_bucket = Column(String,  nullable=True)
    aov_tier        = Column(String,  nullable=True)
    scaling_band    = Column(String,  nullable=True)

    # Performance metrics (running average)
    avg_lift        = Column(Float,   default=0.0)
    avg_risk        = Column(Float,   default=0.0)
    win_rate        = Column(Float,   default=0.0)
    sample_count    = Column(Integer, default=0)
    confidence      = Column(Float,   default=0.0)

    # Influence output (fed into Captain Strategy)
    bias_modifier   = Column(Float,   default=0.0)   # -0.15 to +0.15
    status          = Column(String,  default=ArchetypeStatus.CANDIDATE)

    description     = Column(Text,    nullable=True)
    representative_context = Column(JSON, nullable=True)  # anonymised example
    qdrant_point_id = Column(String,  nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    last_updated    = Column(DateTime, default=datetime.utcnow)


# ─── Replay Simulation Records ────────────────────────────────────────────

class ReplaySimulation(Base):
    """Records of replay simulations run against historical contexts."""
    __tablename__ = "replay_simulations"

    id              = Column(String,  primary_key=True, default=_uuid)
    archetype_id    = Column(String,  index=True, nullable=False)
    simulation_context = Column(JSON, nullable=True)    # context replayed against
    predicted_lift  = Column(Float,   nullable=True)
    predicted_risk  = Column(Float,   nullable=True)
    confidence      = Column(Float,   nullable=True)
    match_score     = Column(Float,   nullable=True)    # similarity to archetype
    recommendation  = Column(Text,    nullable=True)
    simulated_at    = Column(DateTime, default=datetime.utcnow)
