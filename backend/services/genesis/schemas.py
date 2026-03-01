from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# ================= Enums =================

class IndustryType(str, Enum):
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    LOCAL_SERVICE = "local_service"
    EDUCATION = "education"
    B2B_SERVICE = "b2b_service"

class FunnelType(str, Enum):
    LEAD_GEN = "lead_gen"
    DIRECT_CHECKOUT = "direct_checkout"
    TRIAL_CONVERSION = "trial_conversion"
    APP_INSTALL = "app_install"

class GrowthStage(str, Enum):
    SEED = "seed"
    SCALING = "scaling"
    MATURE = "mature"

class BudgetTier(str, Enum):
    MICRO = "micro"       # < $5k/mo
    SMB = "smb"           # $5k - $50k/mo
    MID_MARKET = "mid"    # $50k - $250k/mo
    ENTERPRISE = "ent"    # > $250k/mo

class GoalMode(str, Enum):
    PROFIT_FIRST = "profit_first"
    SCALE_FIRST = "scale_first"
    AWARENESS_FIRST = "awareness_first"
    LEAD_GEN = "lead_gen"

class TimelinePriority(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

# ================= Profile =================

class GenesisProfileSchema(BaseModel):
    industry: IndustryType
    aov: float = Field(gt=0.0)
    gross_margin: float = Field(ge=0.01, le=1.0)
    funnel_type: FunnelType
    geography: str
    growth_stage: GrowthStage
    budget_tier: BudgetTier

# ================= Goals =================

class GenesisGoalsSchema(BaseModel):
    goal_mode: GoalMode
    target_roas: Optional[float] = Field(None, gt=0.0)
    target_cpa: Optional[float] = Field(None, gt=0.0)
    scaling_aggressiveness: float = Field(ge=0.0, le=1.0)
    timeline_priority: TimelinePriority

    @field_validator("target_roas", mode="after")
    @classmethod
    def validate_goals(cls, v, info):
        # Prevent conflicting empty goals depending on mode
        mode = info.data.get("goal_mode")
        cpa = info.data.get("target_cpa")
        
        if mode in [GoalMode.PROFIT_FIRST, GoalMode.SCALE_FIRST] and v is None and cpa is None:
            raise ValueError("ROAS or CPA target is required for performance-driven Goal Modes.")
        return v

# ================= Constraints =================

class GenesisConstraintsSchema(BaseModel):
    max_budget_change_percent: float = Field(ge=0.0, le=100.0)
    max_daily_budget: float = Field(gt=0.0)
    min_allowed_roas: Optional[float] = Field(None, gt=0.0)
    max_risk_score: float = Field(ge=0.0, le=1.0)
    
    auto_execution_enabled: bool
    creative_sandbox_required: bool
    landing_page_auto_edit_allowed: bool

# ================= API Schemas =================
# Schemas defining exact PUT structure required to interact with genesis endpoints.

class ProfileUpdateRequest(BaseModel):
    profile: GenesisProfileSchema
    change_reason: str

class GoalsUpdateRequest(BaseModel):
    goals: GenesisGoalsSchema
    change_reason: str

class ConstraintsUpdateRequest(BaseModel):
    constraints: GenesisConstraintsSchema
    change_reason: str

class GenesisFullResponse(BaseModel):
    company_id: str
    version: int
    profile: GenesisProfileSchema
    goals: GenesisGoalsSchema
    constraints: GenesisConstraintsSchema
    last_updated: str
