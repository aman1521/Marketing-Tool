from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PlanTier(str, enum.Enum):
    SHADOW_ONLY = "shadow_only"
    ASSISTED_MODE = "assisted_mode"
    PARTIAL_AUTONOMY = "partial_autonomy"
    FULL_BOUNDED = "full_bounded_autonomy"
    ENTERPRISE = "enterprise"

class TenantRegistryModel(Base):
    """
    Absolute scoping mechanism. Every external query MUST strictly map to a company_id here.
    """
    __tablename__ = 'saas_tenants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, unique=True, nullable=False)
    tenant_name = Column(String, nullable=False)
    
    # Billing & Gating Reference
    active_plan_tier = Column(Enum(PlanTier), default=PlanTier.SHADOW_ONLY)
    shadow_mode_forced = Column(Boolean, default=True) # Overrides Genesis natively if True
    
    # Billing
    stripe_customer_id = Column(String, nullable=True)
    billing_status = Column(String, default="active") # active, past_due, canceled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AccountUserModel(Base):
    """
    RBAC mappings.
    """
    __tablename__ = 'saas_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("saas_tenants.company_id"), index=True, nullable=False)
    user_id = Column(String, index=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    role = Column(String, nullable=False, default="VIEWER") # OWNER, ADMIN, ANALYST, VIEWER
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
