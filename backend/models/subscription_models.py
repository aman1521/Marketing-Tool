"""
Subscription and Billing Models
===============================
Handles SaaS Stripe limits, monthly billing cycles, and Intelligence usage tracking.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class SubscriptionTierEnum(str, enum.Enum):
    STARTER = "starter"        # 1 Ad Account, 10,000 spend tracking
    PROFESSIONAL = "pro"       # Reddit, Meta, TikTok connectors, AI Simulations
    ENTERPRISE = "enterprise"  # Unlimited AI generation, unlimited connectors

class Subscription(Base):
    """
    Ties a specific company to a Stripe/Braintree recurring payment plan.
    """
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    
    tier = Column(Enum(SubscriptionTierEnum), default=SubscriptionTierEnum.STARTER)
    status = Column(String, default="trialing") # active, trial, past_due, canceled
    
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # -------------------------------------------------------------
    # SaaS Limit Tracking (Per Month)
    # -------------------------------------------------------------
    ad_spend_tracked_this_month = Column(Float, default=0.0)
    ai_simulations_used = Column(Integer, default=0)
    ai_creatives_generated = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company")
