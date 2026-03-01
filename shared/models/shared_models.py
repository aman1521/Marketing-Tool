"""
Shared Data Models for API Requests/Responses
Used across all microservices
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, validator


# ============= Enums =============
class UserRole(str, Enum):
    BUSINESS_OWNER = "business_owner"
    AGENCY_ADMIN = "agency_admin"
    INTERNAL_OPERATOR = "internal_operator"


class BusinessType(str, Enum):
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    SERVICE = "service"
    AGENCY = "agency"
    LOCAL = "local"
    OTHER = "other"


class PlatformName(str, Enum):
    META = "meta"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    PENDING = "pending"


# ============= Auth Models =============
class TokenRequest(BaseModel):
    """OAuth token request"""
    grant_type: str
    code: str
    client_id: str
    client_secret: str
    redirect_uri: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "Bearer"
    expires_in: int


class UserLogin(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Create new user"""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: UserRole
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============= Business Models =============
class BusinessCreate(BaseModel):
    """Create new business"""
    name: str
    industry: str
    business_type: BusinessType
    margin_percentage: Optional[float] = None
    sales_cycle_days: Optional[int] = None
    subscription_model: bool = False


class BusinessUpdate(BaseModel):
    """Update business"""
    name: Optional[str] = None
    industry: Optional[str] = None
    margin_percentage: Optional[float] = None
    sales_cycle_days: Optional[int] = None
    subscription_model: Optional[bool] = None


class BusinessResponse(BaseModel):
    """Business response model"""
    id: str
    name: str
    industry: str
    business_type: BusinessType
    margin_percentage: Optional[float]
    sales_cycle_days: Optional[int]
    subscription_model: bool
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============= Platform Integration Models =============
class PlatformAccountCreate(BaseModel):
    """Create platform account"""
    business_id: str
    platform_name: PlatformName
    platform_account_id: str
    platform_token: str


class PlatformAccountResponse(BaseModel):
    """Platform account response"""
    id: str
    business_id: str
    platform_name: PlatformName
    platform_account_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Campaign Models =============
class CampaignCreate(BaseModel):
    """Create campaign"""
    business_id: str
    platform_id: str
    campaign_name: str
    campaign_objective: str
    daily_budget: float


class CampaignResponse(BaseModel):
    """Campaign response"""
    id: str
    business_id: str
    platform_id: str
    campaign_name: str
    campaign_objective: str
    daily_budget: float
    campaign_status: CampaignStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Creative Models =============
class CreativeCreate(BaseModel):
    """Create creative"""
    business_id: str
    creative_type: str
    format: str
    hook_type: Optional[str] = None
    video_length_seconds: Optional[int] = None
    body_copy: str
    cta_text: Optional[str] = None


class CreativeResponse(BaseModel):
    """Creative response"""
    id: str
    business_id: str
    creative_type: str
    format: str
    hook_type: Optional[str]
    video_length_seconds: Optional[int]
    body_copy: str
    cta_text: Optional[str]
    creative_score: Optional[float]
    predicted_ctr: Optional[float]
    predicted_cvr: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Audience Cluster Models =============
class AudienceClusterResponse(BaseModel):
    """Audience cluster response"""
    id: str
    business_id: str
    cluster_name: str
    cluster_number: int
    profitability_score: float
    scalability_score: float
    size: int
    demographics: Dict[str, Any]
    interests: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Performance Metrics Models =============
class PerformanceMetricsCreate(BaseModel):
    """Create performance metrics"""
    platform_id: str
    campaign_id: Optional[str] = None
    metric_date: str
    impressions: int
    clicks: int
    spend: float
    conversions: int
    revenue: float
    watch_time_seconds: Optional[int] = None


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response"""
    id: str
    platform_id: str
    campaign_id: Optional[str]
    metric_date: str
    impressions: int
    clicks: int
    spend: float
    conversions: int
    revenue: float
    ctr: Optional[float]
    cpc: Optional[float]
    cvr: Optional[float]
    roas: Optional[float]
    watch_time_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= ML Prediction Models =============
class MLPredictionInput(BaseModel):
    """ML prediction input"""
    business_id: str
    prediction_type: str
    input_features: Dict[str, Any]


class MLPredictionResponse(BaseModel):
    """ML prediction response"""
    id: str
    business_id: str
    prediction_type: str
    input_features: Dict[str, Any]
    predicted_value: float
    prediction_date: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Budget Allocation Models =============
class BudgetAllocationResponse(BaseModel):
    """Budget allocation response"""
    id: str
    business_id: str
    campaign_id: Optional[str]
    allocation_date: str
    recommended_budget: float
    current_budget: float
    status: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Strategy Output Models =============
class StrategyOutputResponse(BaseModel):
    """Strategy output response"""
    id: str
    business_id: str
    generated_date: str
    content_calendar: Dict[str, Any]
    funnel_structure: Dict[str, Any]
    ad_copy_variations: List[str]
    hook_angles: List[str]
    budget_explanation: str
    weekly_summary: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Decision Engine Models =============
class DecisionEngineInput(BaseModel):
    """Input for decision engine"""
    business_id: str
    campaign_id: str
    ml_outputs: Dict[str, Any]
    business_constraints: Dict[str, Any]


class DecisionEngineOutput(BaseModel):
    """Decision engine output"""
    campaign_id: str
    platform_fit_score: float
    recommended_action: str  # scale, maintain, reduce
    budget_scaling_factor: float
    should_replace_creative: bool
    reason: str
    predictions: Dict[str, Any]


# ============= API Gateway Models =============
class APIError(BaseModel):
    """API error response"""
    status_code: int
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[APIError] = None
    timestamp: datetime


# ============= Health Check Models =============
class HealthCheckResponse(BaseModel):
    """Service health check response"""
    status: str
    service_name: str
    version: str
    timestamp: datetime
    checks: Optional[Dict[str, bool]] = None
