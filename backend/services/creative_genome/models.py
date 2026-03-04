"""
Creative Genome — SQLAlchemy Models
=====================================
Full data layer for the Creative Genome Mapping Engine.

Every creative is decomposed into genetic components (the Genome),
enriched with persuasion signals, and stored as a searchable vector.
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import (Column, String, Float, Integer, Boolean,
                        DateTime, JSON, Text)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def _uuid(): return str(uuid.uuid4())


# ─── Categorical vocabulary ───────────────────────────────────────────────

class HookType(str, enum.Enum):
    PROBLEM_AGITATION = "problem_agitation"
    CURIOSITY         = "curiosity"
    AUTHORITY         = "authority"
    STORY             = "story"
    SHOCK             = "shock"
    QUESTION          = "question"
    BOLD_CLAIM        = "bold_claim"
    PATTERN_INTERRUPT = "pattern_interrupt"
    UNKNOWN           = "unknown"

class EmotionType(str, enum.Enum):
    URGENCY = "urgency"; FEAR = "fear"; JOY = "joy"; TRUST = "trust"
    CURIOSITY = "curiosity"; PRIDE = "pride"; GUILT = "guilt"
    EXCITEMENT = "excitement"; ASPIRATIONAL = "aspirational"; NEUTRAL = "neutral"

class AuthoritySignal(str, enum.Enum):
    EXPERT       = "expert"
    CELEBRITY    = "celebrity"
    SOCIAL_PROOF = "social_proof"
    DATA_STATS   = "data_stats"
    AWARD        = "award"
    MEDIA_LOGO   = "media_logo"
    TESTIMONIAL  = "testimonial"
    NONE         = "none"

class OfferType(str, enum.Enum):
    DISCOUNT    = "discount"; TRIAL      = "trial"; DEMO = "demo"
    BUNDLE      = "bundle";   GUARANTEE  = "guarantee"; GIFT = "gift"
    EXCLUSIVITY = "exclusivity"; DIRECT  = "direct"

class CTAStyle(str, enum.Enum):
    DIRECT_COMMAND = "direct_command"; SOFT_INVITE = "soft_invite"
    QUESTION       = "question";       SCARCITY    = "scarcity"
    BENEFIT_LEAD   = "benefit_lead";   SOCIAL      = "social"

class Pacing(str, enum.Enum):
    FAST = "fast"; MEDIUM = "medium"; SLOW = "slow"; VARIED = "varied"

class NarrativeStructure(str, enum.Enum):
    PAIN_SOLUTION_PROOF     = "pain_solution_proof"
    HOOK_STORY_OFFER_CTA    = "hook_story_offer_cta"
    PROBLEM_AGIT_SOLUTION   = "problem_agit_solution"
    BEFORE_AFTER_BRIDGE     = "before_after_bridge"
    FEATURES_BENEFITS_CTA   = "features_benefits_cta"
    TESTIMONIAL_PROOF       = "testimonial_proof"
    CURIOSITY_REVEAL        = "curiosity_reveal"
    DIRECT_OFFER            = "direct_offer"
    UNKNOWN                 = "unknown"

class PersuasionTechnique(str, enum.Enum):
    SCARCITY    = "scarcity";  AUTHORITY  = "authority"
    SOCIAL_PROOF= "social_proof"; RECIPROCITY = "reciprocity"
    COMMITMENT  = "commitment"; LIKING    = "liking"
    FEAR_FOMO   = "fear_fomo"; CURIOSITY  = "curiosity"
    NOVELTY     = "novelty";   LOSS_AVERSION = "loss_aversion"

class ArchetypeStatus(str, enum.Enum):
    CANDIDATE = "candidate"; CONFIRMED = "confirmed"; RETIRED = "retired"

class ClusterStatus(str, enum.Enum):
    GROWING = "growing"; STABLE = "stable"; SATURATED = "saturated"; DECLINING = "declining"


# ─── Core Models ─────────────────────────────────────────────────────────

class CreativeGenome(Base):
    """Full genome of one creative asset."""
    __tablename__ = "creative_genomes"

    id               = Column(String, primary_key=True, default=_uuid)
    creative_id      = Column(String, index=True, nullable=True)  # external ref
    company_id       = Column(String, index=True, nullable=True)

    # Genome components
    hook_type        = Column(String, nullable=False, default=HookType.UNKNOWN)
    emotion          = Column(String, nullable=False, default=EmotionType.NEUTRAL)
    authority_signal = Column(String, nullable=False, default=AuthoritySignal.NONE)
    offer_type       = Column(String, nullable=False, default=OfferType.DIRECT)
    cta_style        = Column(String, nullable=False, default=CTAStyle.DIRECT_COMMAND)
    pacing           = Column(String, nullable=False, default=Pacing.MEDIUM)
    structure        = Column(String, nullable=False, default=NarrativeStructure.UNKNOWN)

    # Rich fields
    persuasion_techniques = Column(JSON, nullable=True)  # list[str]
    structure_stages      = Column(JSON, nullable=True)  # ordered list
    headline              = Column(Text, nullable=True)
    body_text             = Column(Text, nullable=True)
    raw_transcript        = Column(Text, nullable=True)

    # Performance (filled post-launch)
    ctr_lift         = Column(Float, nullable=True)
    cvr_lift         = Column(Float, nullable=True)
    hook_retention   = Column(Float, nullable=True)   # % that passed hook
    outcome          = Column(String, nullable=True)  # win/loss/neutral/pending

    # Vector reference
    qdrant_point_id  = Column(String, nullable=True)
    cluster_id       = Column(String, nullable=True)
    archetype_id     = Column(String, nullable=True)

    # Flags
    is_video         = Column(Boolean, default=False)
    platform         = Column(String, nullable=True)
    industry         = Column(String, nullable=True)

    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow)


class GenomeCluster(Base):
    """Cluster of creatives sharing similar genetic profiles."""
    __tablename__ = "genome_clusters"

    id               = Column(String, primary_key=True, default=_uuid)
    name             = Column(String, nullable=False)
    dominant_hook    = Column(String, nullable=True)
    dominant_emotion = Column(String, nullable=True)
    dominant_structure = Column(String, nullable=True)
    dominant_authority = Column(String, nullable=True)
    member_count     = Column(Integer, default=0)
    status           = Column(String, default=ClusterStatus.GROWING)

    # Performance stats
    avg_ctr_lift     = Column(Float, nullable=True)
    avg_cvr_lift     = Column(Float, nullable=True)
    win_rate         = Column(Float, nullable=True)
    saturation_score = Column(Float, default=0.0)   # 0-1
    confidence       = Column(Float, default=0.0)

    # Industries represented
    industries       = Column(JSON, nullable=True)
    centroid_point_id= Column(String, nullable=True)

    first_seen       = Column(DateTime, default=datetime.utcnow)
    last_updated     = Column(DateTime, default=datetime.utcnow)


class CreativeArchetype(Base):
    """Validated, reusable creative template backed by cluster data."""
    __tablename__ = "creative_archetypes"

    id               = Column(String, primary_key=True, default=_uuid)
    name             = Column(String, nullable=False)
    description      = Column(Text, nullable=True)
    status           = Column(String, default=ArchetypeStatus.CANDIDATE)

    # Genome template
    hook_type        = Column(String, nullable=True)
    emotion          = Column(String, nullable=True)
    authority_signal = Column(String, nullable=True)
    offer_type       = Column(String, nullable=True)
    cta_style        = Column(String, nullable=True)
    pacing           = Column(String, nullable=True)
    structure        = Column(String, nullable=True)
    persuasion_mix   = Column(JSON, nullable=True)

    # Evidence
    sample_count     = Column(Integer, default=0)
    avg_ctr_lift     = Column(Float, default=0.0)
    avg_cvr_lift     = Column(Float, default=0.0)
    win_rate         = Column(Float, default=0.0)
    expected_ctr_lift= Column(Float, default=0.0)
    confidence       = Column(Float, default=0.0)
    bias_modifier    = Column(Float, default=0.0)

    industry_fit     = Column(JSON, nullable=True)   # {"saas": 0.8, ...}
    source_cluster_id= Column(String, nullable=True)

    created_at       = Column(DateTime, default=datetime.utcnow)
    last_updated     = Column(DateTime, default=datetime.utcnow)


class CreativeStrategySignal(Base):
    """Output signal from CreativeStrategyEngine → CaptainStrategy / Forge."""
    __tablename__ = "creative_strategy_signals"

    id              = Column(String, primary_key=True, default=_uuid)
    company_id      = Column(String, index=True, nullable=True)
    signal_type     = Column(String, nullable=False)   # CLUSTER_SATURATION / NEW_ANGLE / FATIGUE
    severity        = Column(String, nullable=False)   # HIGH / MEDIUM / LOW
    current_cluster = Column(String, nullable=True)
    recommended_action = Column(Text, nullable=True)
    recommended_tests  = Column(JSON, nullable=True)   # list of genome dicts
    archetype_id    = Column(String, nullable=True)
    confidence      = Column(Float, nullable=True)
    payload         = Column(JSON, nullable=True)
    generated_at    = Column(DateTime, default=datetime.utcnow)
