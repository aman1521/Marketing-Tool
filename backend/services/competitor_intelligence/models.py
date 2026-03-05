"""
Competitor Intelligence Engine — SQLAlchemy Models
===================================================
All models for persisting competitor intelligence data.
No direct coupling to execution engines.
Produces signals only.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


class CompetitorProfile(Base):
    """Registered competitor entity."""
    __tablename__ = "competitor_profiles"

    id            = Column(String, primary_key=True, default=_uuid)
    company_id    = Column(String, index=True, nullable=False)   # owning tenant
    name          = Column(String, nullable=False)
    domain        = Column(String, nullable=False, index=True)
    industry      = Column(String, nullable=True)
    is_active     = Column(Boolean, default=True)
    last_crawled  = Column(DateTime, nullable=True)
    crawl_count   = Column(Integer, default=0)
    notes         = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


class CrawledPage(Base):
    """Raw crawled page record — HTML stored, then cleaned separately."""
    __tablename__ = "crawled_pages"

    id              = Column(String, primary_key=True, default=_uuid)
    competitor_id   = Column(String, index=True, nullable=False)
    url             = Column(String, nullable=False)
    page_type       = Column(String, nullable=True)   # homepage, pricing, features, about, ad
    raw_html_length = Column(Integer, nullable=True)
    cleaned_text    = Column(Text, nullable=True)
    chunk_count     = Column(Integer, default=0)
    crawled_at      = Column(DateTime, default=datetime.utcnow)
    http_status     = Column(Integer, nullable=True)


class AdCreative(Base):
    """Captured ad creative from public ad libraries."""
    __tablename__ = "ad_creatives"

    id              = Column(String, primary_key=True, default=_uuid)
    competitor_id   = Column(String, index=True, nullable=False)
    platform        = Column(String, nullable=False)    # meta, google, tiktok
    ad_id           = Column(String, nullable=True)     # platform-native ID if available
    headline        = Column(Text, nullable=True)
    body_text       = Column(Text, nullable=True)
    cta             = Column(String, nullable=True)
    image_url       = Column(String, nullable=True)
    offer_type      = Column(String, nullable=True)     # discount, trial, demo, content
    emotional_tone  = Column(String, nullable=True)     # aggressive, educational, premium
    qdrant_point_id = Column(String, nullable=True)     # vector DB reference
    captured_at     = Column(DateTime, default=datetime.utcnow)


class SimilarityCluster(Base):
    """Detected messaging similarity cluster across competitors."""
    __tablename__ = "similarity_clusters"

    id                  = Column(String, primary_key=True, default=_uuid)
    company_id          = Column(String, index=True, nullable=False)
    cluster_label       = Column(String, nullable=False)
    theme               = Column(String, nullable=False)
    centroid_summary    = Column(Text, nullable=True)
    member_count        = Column(Integer, default=0)
    avg_similarity      = Column(Float, nullable=True)
    saturation_score    = Column(Float, nullable=True)   # 0–1, 1 = fully saturated
    detected_at         = Column(DateTime, default=datetime.utcnow)


class MarketPressureSnapshot(Base):
    """Point-in-time market pressure score per company."""
    __tablename__ = "market_pressure_snapshots"

    id                        = Column(String, primary_key=True, default=_uuid)
    company_id                = Column(String, index=True, nullable=False)
    pressure_score            = Column(Float, nullable=False)    # 0–100
    competitor_count_active   = Column(Integer, nullable=True)
    avg_ad_saturation         = Column(Float, nullable=True)
    dominant_theme            = Column(String, nullable=True)
    cluster_count             = Column(Integer, nullable=True)
    unique_angle_opportunity  = Column(Boolean, default=False)
    snapshot_context          = Column(JSON, nullable=True)
    computed_at               = Column(DateTime, default=datetime.utcnow)


class StrategyGapSignal(Base):
    """Structured gap insight produced for CaptainStrategy consumption."""
    __tablename__ = "strategy_gap_signals"

    id                = Column(String, primary_key=True, default=_uuid)
    company_id        = Column(String, index=True, nullable=False)
    gap_type          = Column(String, nullable=False)   # POSITIONING, CONTENT, OFFER, TONE
    severity          = Column(String, nullable=False)   # HIGH, MEDIUM, LOW
    description       = Column(Text, nullable=False)
    opportunity       = Column(Text, nullable=True)
    data_source       = Column(String, nullable=True)    # crawl | ad_library
    confidence        = Column(Float, nullable=True)
    is_actioned       = Column(Boolean, default=False)
    payload           = Column(JSON, nullable=True)      # raw evidence
    generated_at      = Column(DateTime, default=datetime.utcnow)
