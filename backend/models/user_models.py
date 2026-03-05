"""
User & Access Models
====================
Manages Authentication, Team Members, Roles (Owner, Admin, Manager, Analyst),
and explicit Asset-Level Permissions limiting access to specific Ad Accounts, Domains, etc.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class RoleEnum(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company_memberships = relationship("CompanyMember", back_populates="user")

class CompanyMember(Base):
    """Links a user to a company with a specific Role Level (Admin, Manager, Analyst)."""
    __tablename__ = "company_members"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    company_id = Column(String, ForeignKey("companies.id"))
    role = Column(Enum(RoleEnum), default=RoleEnum.ANALYST)
    
    user = relationship("User", back_populates="company_memberships")
    company = relationship("Company", back_populates="members")
    
    # Granular Asset Permissions
    asset_permissions = relationship("AssetPermission", back_populates="member")

class AssetPermission(Base):
    """
    Extremely specific explicit grants linking a Team Member to a physical Asset.
    E.g., John Doe (Manager) ONLY has access to 'Meta Ad Account #123'.
    """
    __tablename__ = "asset_permissions"

    id = Column(String, primary_key=True)
    member_id = Column(String, ForeignKey("company_members.id"))
    asset_id = Column(String, ForeignKey("business_assets.id"))
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    
    member = relationship("CompanyMember", back_populates="asset_permissions")
    asset = relationship("BusinessAsset", back_populates="permissions")
