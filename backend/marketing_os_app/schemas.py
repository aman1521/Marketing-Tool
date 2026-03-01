from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TenantContext(BaseModel):
    """
    Injected payload validating the user's role and company. 
    Prevents cross-tenant logic.
    """
    company_id: str
    user_id: str
    role: str
    active_plan: str

class AutonomyDashboardResponse(BaseModel):
    company_id: str
    autonomy_stability_index: float
    drift_incidents: int
    current_risk_level: str
    budget_exposure_percentage: float
    shadow_mode_active: bool
    confidence_average: float
    rollback_count: int
    pending_calibration_suggestions: int
