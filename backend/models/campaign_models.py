"""
Campaign Data Layer
===================
Stores pulled unified platform metrics from Reddit, Meta, TikTok, GMB.
Standardizes CPA, Spend, CTR so AI Engines can simulate cleanly.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class DeliveryStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    REJECTED = "rejected_creative"
    AI_PAUSED = "ai_engine_disabled"
    LEARNING = "learning_phase"

class UnifiedCampaign(Base):
    """Normalized object representing a Campaign regardless of the Ad Platform (Meta/TikTok/Reddit)."""
    __tablename__ = "unified_campaigns"

    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    asset_id = Column(String, ForeignKey("business_assets.id"), nullable=True) # E.g., The Meta Ad Account ID it belongs to
    
    platform = Column(String) # meta, reddit, tiktok, etc.
    name = Column(String, index=True)
    objective = Column(String) # conversions, leads, brand_awareness
    daily_budget = Column(Float, default=0.0)
    
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PAUSED)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Control override flag - if FALSE, CaptainStrategy can only alert, not modify.
    autonomous_scaling_enabled = Column(Boolean, default=False)
    
    # Downstream structures
    ad_sets = relationship("UnifiedAdSet", back_populates="campaign", cascade="all, delete-orphan")
    
class UnifiedAdSet(Base):
    """Audiences & Targeting Groups (e.g. Reddit Subreddits vs Meta Custom Audiences)."""
    __tablename__ = "unified_ad_sets"
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("unified_campaigns.id"))
    
    name = Column(String)
    targeting_json = Column(String) # e.g. [{"type": "subreddit", "value": "r/marketing"}]
    bid_strategy = Column(String)
    daily_budget = Column(Float)
    
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PAUSED)
    
    campaign = relationship("UnifiedCampaign", back_populates="ad_sets")
    ads = relationship("UnifiedAd", back_populates="ad_set", cascade="all, delete-orphan")

class UnifiedAd(Base):
    """The physical creative and performance metrics for the active ad."""
    __tablename__ = "unified_ads"
    
    id = Column(String, primary_key=True)
    ad_set_id = Column(String, ForeignKey("unified_ad_sets.id"))
    creative_id = Column(String, nullable=True) # Maps to the Creative Intelligence Engine model if extracted
    
    name = Column(String)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PAUSED)
    
    ad_copy = Column(String, nullable=True)
    headline = Column(String, nullable=True)
    media_url = Column(String, nullable=True) # The image/video endpoint
    
    # -------------------------------------------------------------
    # Rolling Metrics Cache (Populated via Connector Sync Workers)
    # -------------------------------------------------------------
    spend = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cpa = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    ad_set = relationship("UnifiedAdSet", back_populates="ads")
