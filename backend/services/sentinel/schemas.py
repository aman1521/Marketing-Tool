from pydantic import BaseModel, Field

class SentinelRiskSchema(BaseModel):
    """
    Outputs standard macro stability scoring indicating if CaptainExecute
    needs a global pause from humans.
    """
    autonomy_stability_index: float = Field(ge=0.0, le=1.0)
    drift_frequency: float = Field(ge=0.0, le=1.0)
    execution_precision_score: float = Field(ge=0.0, le=1.0)
    system_risk_exposure_score: float = Field(ge=0.0, le=1.0)
    shadow_mode_active: bool = False
