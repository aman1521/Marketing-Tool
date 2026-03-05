"""
Platform Connectors Models
==========================
Persistent OAuth tokens, API bindings, and Integration Health status
for external marketing channels including Reddit Ops and Local GMB SEO.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class PlatformEnum(str, enum.Enum):
    META_ADS = "meta"
    GOOGLE_ADS = "google_ads"
    TIKTOK_ADS = "tiktok"
    LINKEDIN_ADS = "linkedin"
    X_ADS = "twitter"
    REDDIT_ADS = "reddit"
    GOOGLE_MY_BUSINESS = "gmb_local"
    SEARCH_CONSOLE = "google_search_console"
    GOOGLE_ANALYTICS = "ga4"
    SHOPIFY = "shopify"

class ConnectorStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    FAILED = "failed"
    PENDING_AUTH = "pending"

class PlatformConnector(Base):
    """
    Physical link between a tenant Company and external APIs like TikTok or Reddit.
    """
    __tablename__ = "platform_connectors"

    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    platform = Column(Enum(PlatformEnum), nullable=False)
    
    # Store heavily encrypted tokens (Assumes Fernet encryption mapping on service layer)
    encrypted_access_token = Column(String, nullable=False)
    encrypted_refresh_token = Column(String, nullable=True)
    
    external_account_id = Column(String, nullable=True) # e.g., the exact Ad Account Id
    token_expires_at = Column(DateTime, nullable=True)
    
    status = Column(Enum(ConnectorStatusEnum), default=ConnectorStatusEnum.PENDING_AUTH)
    last_sync_at = Column(DateTime, nullable=True)
    
    company = relationship("Company", back_populates="connectors")
    
    # Sync Logs mapping pulling history metrics
    sync_logs = relationship("ConnectorSyncLog", back_populates="connector")

class ConnectorSyncLog(Base):
    """Tracks every time we invoke an external API to ingest Reddit Data, GMB visits, etc."""
    __tablename__ = "connector_sync_logs"
    
    id = Column(String, primary_key=True)
    connector_id = Column(String, ForeignKey("platform_connectors.id"))
    records_pulled = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    sync_duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    connector = relationship("PlatformConnector", back_populates="sync_logs")
