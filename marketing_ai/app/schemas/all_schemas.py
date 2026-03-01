from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_type: str = "business_owner" # business_owner, marketing_professional, freelancer

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role_type: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Companies
class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    target_audience: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    industry: Optional[str]
    target_audience: Optional[str]
    created_at: datetime
    is_active: bool
    class Config:
        from_attributes = True

# Connectors
class ConnectorConnect(BaseModel):
    platform_name: str
    credentials: dict # Raw payload, gets AES encrypted in service
    
class ActionExecution(BaseModel):
    platform: str
    action_type: str
    value: Any

class WebhookStripePayload(BaseModel):
    event_type: str
    data: dict

# Intelligence
class IntelligenceSummaryResponse(BaseModel):
    company_id: str
    status: str
    recommended_actions: List[dict]
    model_inference_time_ms: int

class CompetitorAnalysisRequest(BaseModel):
    company_id: str
    competitor_url: str

class SafetyValidationRequest(BaseModel):
    action_type: str
    value: Any
    confidence_score: float

class SafetyValidationResponse(BaseModel):
    status: str # approved, rejected, requires_manual_review
    reason: Optional[str] = None
