from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_type = Column(String(50), default="business_owner")  # business_owner, marketing_professional, freelancer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    companies = relationship("Company", back_populates="owner")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    stripe_customer_id = Column(String(100), unique=True, index=True, nullable=True)
    plan_id = Column(String(50), default="free") # starter, growth, agency
    status = Column(String(50), default="active")
    trial_active = Column(Boolean, default=True)
    trial_start_date = Column(DateTime(timezone=True), nullable=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship back
    user = relationship("User", back_populates="subscription")


class Company(Base):
    __tablename__ = "companies"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    target_audience = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="companies")
    connections = relationship("PlatformConnection", back_populates="company")
    competitor_pages = relationship("CompetitorPageEmbedding", back_populates="company")


class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    platform_name = Column(String(50), nullable=False) # meta, google, tiktok etc
    encrypted_credentials = Column(Text, nullable=False) # Should be AES encrypted!
    status = Column(String(50), default="active")
    last_sync = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="connections")
    accounts = relationship("PlatformAccount", back_populates="connection")


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String(36), ForeignKey("platform_connections.id"))
    account_id = Column(String(255), nullable=False)
    account_name = Column(String(255), nullable=False)
    is_enabled = Column(Boolean, default=True)

    connection = relationship("PlatformConnection", back_populates="accounts")
    metrics = relationship("RawMetrics", back_populates="account")
    posts = relationship("Post", back_populates="account")
    campaigns = relationship("Campaign", back_populates="account")


class Post(Base):
    __tablename__ = "posts"
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("platform_accounts.id"))
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    status = Column(String(50), default="draft")  # draft, scheduled, published
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    engagement_metrics = Column(JSON, nullable=True)

    account = relationship("PlatformAccount", back_populates="posts")


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("platform_accounts.id"))
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active")  # active, paused
    daily_budget = Column(Float, default=0.0)
    performance_metrics = Column(JSON, nullable=True)
    is_auto_managed = Column(Boolean, default=False)

    account = relationship("PlatformAccount", back_populates="campaigns")


class RawMetrics(Base):
    __tablename__ = "raw_metrics"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("platform_accounts.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    raw_payload = Column(JSON, nullable=True) # Full unstructured data

    account = relationship("PlatformAccount", back_populates="metrics")


class EngineeredFeatures(Base):
    __tablename__ = "engineered_features"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    date_calculated = Column(DateTime(timezone=True), server_default=func.now())
    feature_vector = Column(JSON, nullable=False)


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    segment_name = Column(String(100), nullable=False)
    engagement_score = Column(Float, default=0.0)
    conversion_friction = Column(Float, default=0.0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class StrategyLog(Base):
    __tablename__ = "strategy_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    strategy_payload = Column(JSON, nullable=False)
    reasoning_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    action_type = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    target_id = Column(String(255), nullable=False)
    action_payload = Column(JSON, nullable=False)
    safety_status = Column(String(50), nullable=False) # approved, rejected, requires_manual_review
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship backwards (requires AutomationLog table above or below)
    # Added relationship if strategy backlink is utilized.


class AutomationLog(Base):
    __tablename__ = "automation_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    objective = Column(String(255), nullable=False)
    risk_level = Column(String(50), default="Moderate")  # Conservative, Moderate, Aggressive
    status = Column(String(50), default="proposed")      # proposed, approved, rejected, executed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")


class CompetitorPageEmbedding(Base):
    __tablename__ = "competitor_page_embeddings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"))
    competitor_domain = Column(String(255), nullable=False)
    page_type = Column(String(100), nullable=True)
    qdrant_point_id = Column(String(255), nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="competitor_pages")
