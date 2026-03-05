"""
Company & Business Assets Models
================================
Defines the Parent Corporate entity, Subscriptions, and the child 
Business Assets (Ad Accounts, Pixels, Domains, Google My Business Locations).
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class AssetTypeEnum(str, enum.Enum):
    AD_ACCOUNT = "ad_account"
    PAGE = "social_page"
    DOMAIN = "website_domain"
    PIXEL = "tracking_pixel"
    AUDIENCE = "custom_audience"
    GMB_LOCATION = "gmb_location"
    SEO_PROPERTY = "seo_property"

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    domain = Column(String, nullable=True)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription_tier = Column(String, default="starter") # E.g., Pro, Enterprise, etc.
    
    # Relationships
    members = relationship("CompanyMember", back_populates="company")
    assets = relationship("BusinessAsset", back_populates="company")
    connectors = relationship("PlatformConnector", back_populates="company")

class BusinessAsset(Base):
    """
    Physical instances of marketing assets.
    E.g. A Meta Ad Account ID, A Domain name 'acme.com', A Local GMB address.
    """
    __tablename__ = "business_assets"

    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    asset_type = Column(Enum(AssetTypeEnum), nullable=False)
    name = Column(String, nullable=False) # e.g. "Acme Corp US Branch Meta Account"
    external_id = Column(String, index=True) # Direct mapping to external API ID like Meta Act_1234
    
    # SEO Insights 
    seo_metrics = relationship("SEOMetricMap", uselist=False, back_populates="asset")
    
    # User permissions controlling access to this explicit asset
    permissions = relationship("AssetPermission", back_populates="asset")
    company = relationship("Company", back_populates="assets")
    
class SEOMetricMap(Base):
    """Metrics attached explicitly to 'Domain' type Assets."""
    __tablename__ = "seo_metrics_maps"
    
    asset_id = Column(String, ForeignKey("business_assets.id"), primary_key=True)
    organic_traffic_vol = Column(Integer, default=0)
    top_ranking_keywords_json = Column(String, default="[]") 
    page_speed_index = Column(Integer, default=100)
    domain_authority = Column(Integer, default=0)
    
    asset = relationship("BusinessAsset", back_populates="seo_metrics")
