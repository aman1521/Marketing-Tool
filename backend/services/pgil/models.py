"""
Private Global Intelligence Layer (PGIL) — SQLAlchemy Models
=============================================================

PGIL is a platform-wide, cross-tenant intelligence system.

🔒 ISOLATION GUARANTEE:
  Every table and column in this module is designed so that:
  - No company_id, operator_id, campaign_id, brand name or any
    identifiable string can be stored.
  - All data is bucketed / anonymised before reaching the DB.
  - Operator-level access control enforced at query time.

Schema attributes stored per event:
  industry_bucket   — ecommerce / saas / fintech / health / agency / other
  creative_cluster  — trial / discount / premium / trust / education / comparison
  funnel_stage      — tofu / mofu / bofu / retention
  volatility_band   — low / medium / high / extreme
  scaling_band      — micro / growth / scale / enterprise
  outcome           — win / loss / neutral
  lift_delta        — float (no currency / spend amounts)
  risk_score        — float 0–1
  confidence        — Wilson lower bound
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import (Column, String, Float, Integer, Boolean,
                        DateTime, JSON, Text, Index)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


# ─── Categorical Buckets ──────────────────────────────────────────────────

class IndustryBucket(str, enum.Enum):
    ECOMMERCE = "ecommerce"
    SAAS      = "saas"
    FINTECH   = "fintech"
    HEALTH    = "health"
    AGENCY    = "agency"
    OTHER     = "other"


class CreativeCluster(str, enum.Enum):
    TRIAL      = "trial"
    DISCOUNT   = "discount"
    PREMIUM    = "premium"
    TRUST      = "trust"
    EDUCATION  = "education"
    COMPARISON = "comparison"
    URGENCY    = "urgency"
    OTHER      = "other"


class FunnelStage(str, enum.Enum):
    TOFU      = "tofu"        # awareness
    MOFU      = "mofu"        # consideration
    BOFU      = "bofu"        # conversion
    RETENTION = "retention"


class VolatilityBand(str, enum.Enum):
    LOW     = "low"       # 0.0–0.25
    MEDIUM  = "medium"    # 0.25–0.50
    HIGH    = "high"      # 0.50–0.75
    EXTREME = "extreme"   # 0.75–1.0


class ScalingBand(str, enum.Enum):
    MICRO      = "micro"       # <$5k/month
    GROWTH     = "growth"      # $5k–$50k
    SCALE      = "scale"       # $50k–$500k
    ENTERPRISE = "enterprise"  # >$500k


class PatternStatus(str, enum.Enum):
    EMERGING   = "emerging"
    VALIDATED  = "validated"
    DOMINANT   = "dominant"
    DEPRECATED = "deprecated"


class ArchetypeStatus(str, enum.Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    RETIRED   = "retired"


# ─── Core PGIL Event (fully anonymised) ──────────────────────────────────

class PGILEvent(Base):
    """
    Atomic anonymised strategy execution record.
    No identifiable data whatsoever.
    """
    __tablename__ = "pgil_events"

    id               = Column(String,  primary_key=True, default=_uuid)

    # Structural attributes (bucketed — not identifiable)
    industry_bucket  = Column(String,  nullable=False, index=True)
    creative_cluster = Column(String,  nullable=False, index=True)
    funnel_stage     = Column(String,  nullable=False, index=True)
    volatility_band  = Column(String,  nullable=False, index=True)
    scaling_band     = Column(String,  nullable=False, index=True)
    strategy_type    = Column(String,  nullable=False, index=True)

    # Signal context (statistical only — no absolutes)
    drift_bucket     = Column(String,  nullable=True)   # low/med/high
    confidence_bucket= Column(String,  nullable=True)   # low/med/high
    roi_direction    = Column(String,  nullable=True)   # up/flat/down
    escalation_level = Column(String,  nullable=True)   # none/low/high

    # Outcome metrics
    outcome          = Column(String,  nullable=False, default="pending")
    lift_delta       = Column(Float,   nullable=True)   # % change, not absolute
    risk_score       = Column(Float,   nullable=True)
    time_to_result_h = Column(Integer, nullable=True)   # hours, not timestamps

    # Vector reference
    qdrant_point_id  = Column(String,  nullable=True)
    pattern_fingerprint = Column(String, nullable=True, index=True)

    # Metadata (no identifiers)
    collected_at     = Column(DateTime, default=datetime.utcnow)
    week_of_year     = Column(Integer, nullable=True)   # temporal signal w/o date


# ─── PGIL Pattern ─────────────────────────────────────────────────────────

class PGILPattern(Base):
    """
    Aggregated cross-tenant success pattern.
    Computed by PGILPatternEngine from raw PGILEvents.
    """
    __tablename__ = "pgil_patterns"

    id               = Column(String,  primary_key=True, default=_uuid)
    fingerprint      = Column(String,  nullable=False, unique=True, index=True)

    # Profile (same buckets as event)
    industry_bucket  = Column(String,  nullable=False)
    creative_cluster = Column(String,  nullable=False)
    funnel_stage     = Column(String,  nullable=False)
    volatility_band  = Column(String,  nullable=False)
    scaling_band     = Column(String,  nullable=False)
    strategy_type    = Column(String,  nullable=False)

    # Aggregated metrics (Welford running average)
    sample_count     = Column(Integer, default=1)
    win_count        = Column(Integer, default=0)
    avg_lift         = Column(Float,   default=0.0)
    avg_risk         = Column(Float,   default=0.0)
    stddev_lift      = Column(Float,   default=0.0)   # variance tracking
    win_rate         = Column(Float,   default=0.0)
    confidence       = Column(Float,   default=0.0)   # Wilson lower bound

    # Pattern classification
    status           = Column(String,  default=PatternStatus.EMERGING)
    qdrant_point_id  = Column(String,  nullable=True)

    first_seen       = Column(DateTime, default=datetime.utcnow)
    last_updated     = Column(DateTime, default=datetime.utcnow)


# ─── PGIL Archetype ───────────────────────────────────────────────────────

class PGILArchetype(Base):
    """
    High-confidence cross-industry strategy archetype.
    Produced by PGILArchetypeBuilder. Consumed by PGILInfluenceController.
    """
    __tablename__ = "pgil_archetypes"

    id               = Column(String,  primary_key=True, default=_uuid)
    name             = Column(String,  nullable=False)
    description      = Column(Text,    nullable=True)

    # Profile
    strategy_type    = Column(String,  nullable=False)
    industry_bucket  = Column(String,  nullable=True)   # null = cross-industry
    funnel_stage     = Column(String,  nullable=True)
    volatility_band  = Column(String,  nullable=True)
    scaling_band     = Column(String,  nullable=True)
    creative_cluster = Column(String,  nullable=True)

    # Statistical backing
    sample_count     = Column(Integer, default=0)
    avg_lift         = Column(Float,   default=0.0)
    avg_risk         = Column(Float,   default=0.0)
    win_rate         = Column(Float,   default=0.0)
    confidence       = Column(Float,   default=0.0)
    industry_coverage= Column(Integer, default=0)   # # industries represented

    # Influence output
    bias_modifier    = Column(Float,   default=0.0)   # ±0.15
    lift_prior       = Column(Float,   default=0.0)   # Bayesian prior lift
    risk_prior       = Column(Float,   default=0.0)

    status           = Column(String,  default=ArchetypeStatus.CANDIDATE)
    pattern_ids      = Column(JSON,    nullable=True)   # source pattern IDs
    qdrant_point_id  = Column(String,  nullable=True)

    created_at       = Column(DateTime, default=datetime.utcnow)
    last_updated     = Column(DateTime, default=datetime.utcnow)


# ─── PGIL Influence Log ───────────────────────────────────────────────────

class PGILInfluenceLog(Base):
    """Audit trail of PGIL influence signals delivered to CaptainStrategy."""
    __tablename__ = "pgil_influence_logs"

    id               = Column(String, primary_key=True, default=_uuid)
    strategy_type    = Column(String, nullable=False)
    industry_bucket  = Column(String, nullable=True)
    archetype_id     = Column(String, nullable=True)
    bias_applied     = Column(Float,  nullable=True)
    lift_prior       = Column(Float,  nullable=True)
    confidence       = Column(Float,  nullable=True)
    action_suggested = Column(String, nullable=True)
    delivered_at     = Column(DateTime, default=datetime.utcnow)
