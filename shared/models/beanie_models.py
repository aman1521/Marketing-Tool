from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime
import uuid


class User(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: Indexed(str, unique=True) = Field(...)
    username: Indexed(str, unique=True) = Field(...)
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "business_owner"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "user123",
                "first_name": "First",
                "last_name": "Last",
                "role": "business_owner"
            }
        }


class Business(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    industry: Optional[str] = None
    business_type: Optional[str] = None
    margin_percentage: Optional[float] = None
    sales_cycle_days: Optional[int] = None
    subscription_model: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "businesses"


class PlatformAccount(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: Optional[uuid.UUID] = None
    platform_name: str
    platform_account_id: str
    platform_token: Optional[str] = None
    platform_token_expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "platform_accounts"


class UserBusinessAssignment(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    business_id: uuid.UUID
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_business_assignments"


class Campaign(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    platform_id: uuid.UUID
    campaign_name: str
    platform_campaign_id: Optional[str] = None
    campaign_objective: Optional[str] = None
    daily_budget: Optional[float] = None
    campaign_status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "campaigns"


class AdSet(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    campaign_id: uuid.UUID
    platform_adset_id: Optional[str] = None
    adset_name: Optional[str] = None
    daily_budget: Optional[float] = None
    audience_cluster_id: Optional[uuid.UUID] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ad_sets"


class Creative(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    platform_creative_id: Optional[str] = None
    creative_type: Optional[str] = None
    format: Optional[str] = None
    hook_type: Optional[str] = None
    video_length_seconds: Optional[int] = None
    body_copy: Optional[str] = None
    cta_text: Optional[str] = None
    creative_score: Optional[float] = None
    predicted_ctr: Optional[float] = None
    predicted_cvr: Optional[float] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "creatives"


class CampaignCreative(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    campaign_id: uuid.UUID
    creative_id: uuid.UUID
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "campaign_creatives"


class AudienceCluster(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    cluster_name: Optional[str] = None
    cluster_number: Optional[int] = None
    profitability_score: Optional[float] = None
    scalability_score: Optional[float] = None
    size: Optional[int] = None
    demographics: Optional[dict] = None
    interests: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audience_clusters"


class PerformanceMetrics(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    platform_id: uuid.UUID
    campaign_id: Optional[uuid.UUID] = None
    metric_date: datetime
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    spend: Optional[float] = None
    conversions: Optional[int] = None
    revenue: Optional[float] = None
    ctr: Optional[float] = None
    cpc: Optional[float] = None
    cvr: Optional[float] = None
    roas: Optional[float] = None
    watch_time_seconds: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "performance_metrics"


class BudgetAllocation(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    allocation_date: datetime
    campaign_id: Optional[uuid.UUID] = None
    recommended_budget: Optional[float] = None
    current_budget: Optional[float] = None
    status: str = "pending"
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "budget_allocations"


class StrategyOutput(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    generated_date: datetime
    content_calendar: Optional[dict] = None
    funnel_structure: Optional[dict] = None
    ad_copy_variations: Optional[dict] = None
    hook_angles: Optional[dict] = None
    budget_explanation: Optional[str] = None
    weekly_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "strategy_outputs"


class MLPrediction(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    prediction_type: Optional[str] = None
    input_features: Optional[dict] = None
    predicted_value: Optional[float] = None
    actual_value: Optional[float] = None
    error_rate: Optional[float] = None
    prediction_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ml_predictions"


class RawDataLog(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    business_id: uuid.UUID
    platform_id: uuid.UUID
    data_type: Optional[str] = None
    raw_response: Optional[dict] = None
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "raw_data_logs"


class AuditLog(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: Optional[uuid.UUID] = None
    business_id: Optional[uuid.UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[uuid.UUID] = None
    before_state: Optional[dict] = None
    after_state: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"


class ApiError(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    service_name: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stacktrace: Optional[str] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "api_errors"
