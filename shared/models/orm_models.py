"""
SQLAlchemy ORM Models
Maps Python classes to PostgreSQL schema
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, UUID, 
    ForeignKey, Text, JSON, Numeric, BigInteger, create_engine, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), nullable=False)  # business_owner, agency_admin, internal_operator
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    business_assignments = relationship("UserBusinessAssignment", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    business_type = Column(String(50), nullable=False)  # ecommerce, saas, service, agency, local, other
    margin_percentage = Column(Numeric(5, 2))
    sales_cycle_days = Column(Integer)
    subscription_model = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_assignments = relationship("UserBusinessAssignment", back_populates="business")
    platform_accounts = relationship("PlatformAccount", back_populates="business")
    campaigns = relationship("Campaign", back_populates="business")
    creatives = relationship("Creative", back_populates="business")
    audience_clusters = relationship("AudienceCluster", back_populates="business")
    budget_allocations = relationship("BudgetAllocation", back_populates="business")
    strategy_outputs = relationship("StrategyOutput", back_populates="business")
    ml_predictions = relationship("MLPrediction", back_populates="business")
    raw_data_logs = relationship("RawDataLog", back_populates="business")


class UserBusinessAssignment(Base):
    __tablename__ = "user_business_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # owner, admin, operator
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="business_assignments")
    business = relationship("Business", back_populates="user_assignments")


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False)  # meta, google, tiktok, linkedin, shopify, woocommerce
    platform_account_id = Column(String(255), nullable=False)
    platform_token = Column(String(1000))
    platform_token_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="platform_accounts")
    campaigns = relationship("Campaign", back_populates="platform")
    performance_metrics = relationship("PerformanceMetrics", back_populates="platform")
    raw_data_logs = relationship("RawDataLog", back_populates="platform")


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    platform_campaign_id = Column(String(255))
    campaign_objective = Column(String(100))
    daily_budget = Column(Numeric(12, 2))
    campaign_status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="campaigns")
    platform = relationship("PlatformAccount", back_populates="campaigns")
    ad_sets = relationship("AdSet", back_populates="campaign")
    creatives = relationship("CampaignCreative", back_populates="campaign")
    performance_metrics = relationship("PerformanceMetrics", back_populates="campaign")
    budget_allocations = relationship("BudgetAllocation", back_populates="campaign")


class AdSet(Base):
    __tablename__ = "ad_sets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_adset_id = Column(String(255))
    adset_name = Column(String(255))
    daily_budget = Column(Numeric(12, 2))
    audience_cluster_id = Column(UUID(as_uuid=True), ForeignKey("audience_clusters.id"))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="ad_sets")


class Creative(Base):
    __tablename__ = "creatives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_creative_id = Column(String(255))
    creative_type = Column(String(50))
    format = Column(String(50))
    hook_type = Column(String(100))
    video_length_seconds = Column(Integer)
    body_copy = Column(Text)
    cta_text = Column(String(255))
    creative_score = Column(Numeric(5, 2))
    predicted_ctr = Column(Numeric(5, 4))
    predicted_cvr = Column(Numeric(5, 4))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    business = relationship("Business", back_populates="creatives")
    campaigns = relationship("CampaignCreative", back_populates="creative")


class CampaignCreative(Base):
    __tablename__ = "campaign_creatives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    creative_id = Column(UUID(as_uuid=True), ForeignKey("creatives.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="creatives")
    creative = relationship("Creative", back_populates="campaigns")


class AudienceCluster(Base):
    __tablename__ = "audience_clusters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_name = Column(String(255))
    cluster_number = Column(Integer)
    profitability_score = Column(Numeric(5, 2))
    scalability_score = Column(Numeric(5, 2))
    size = Column(Integer)
    demographics = Column(JSON)
    interests = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="audience_clusters")


class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True)
    metric_date = Column(DateTime, nullable=False, index=True)
    impressions = Column(BigInteger)
    clicks = Column(BigInteger)
    spend = Column(Numeric(12, 2))
    conversions = Column(Integer)
    revenue = Column(Numeric(12, 2))
    ctr = Column(Numeric(5, 4))
    cpc = Column(Numeric(8, 2))
    cvr = Column(Numeric(5, 4))
    roas = Column(Numeric(8, 4))
    watch_time_seconds = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("PlatformAccount", back_populates="performance_metrics")
    campaign = relationship("Campaign", back_populates="performance_metrics")


class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    allocation_date = Column(DateTime, nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    recommended_budget = Column(Numeric(12, 2))
    current_budget = Column(Numeric(12, 2))
    status = Column(String(50), default="pending")
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="budget_allocations")
    campaign = relationship("Campaign", back_populates="budget_allocations")


class StrategyOutput(Base):
    __tablename__ = "strategy_outputs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    generated_date = Column(DateTime, nullable=False)
    content_calendar = Column(JSON)
    funnel_structure = Column(JSON)
    ad_copy_variations = Column(JSON)
    hook_angles = Column(JSON)
    budget_explanation = Column(Text)
    weekly_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="strategy_outputs")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    prediction_type = Column(String(100))
    input_features = Column(JSON)
    predicted_value = Column(Numeric(12, 4))
    actual_value = Column(Numeric(12, 4))
    error_rate = Column(Numeric(5, 4))
    prediction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="ml_predictions")


class RawDataLog(Base):
    __tablename__ = "raw_data_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False)
    data_type = Column(String(100))
    raw_response = Column(JSON)
    sync_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="raw_data_logs")
    platform = relationship("PlatformAccount", back_populates="raw_data_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=True)
    action = Column(String(255))
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    before_state = Column(JSON)
    after_state = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class ApiError(Base):
    __tablename__ = "api_errors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(100))
    method = Column(String(50))
    endpoint = Column(String(255))
    error_code = Column(String(50))
    error_message = Column(Text)
    stacktrace = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)
