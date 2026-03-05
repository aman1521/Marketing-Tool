from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class AssetPermissionBase(BaseModel):
    asset_id: str
    asset_name: str
    can_view: bool = True
    can_edit: bool = False

class CompanyMemberBase(BaseModel):
    user_id: str
    company_id: str
    role: str # owner, admin, manager, analyst

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime
    
    company_role: Optional[str] = None
    asset_restrictions: List[AssetPermissionBase] = []

    class Config:
        from_attributes = True

class InviteUserRequest(BaseModel):
    email: EmailStr
    name: str
    role: str
    asset_restrictions: Optional[List[str]] = None # List of Asset IDs if restricted
