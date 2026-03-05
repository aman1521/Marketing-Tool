from pydantic import BaseModel, Field

class PulseOutputSchema(BaseModel):
    """
    Structured Gravity Signals output from PulseEngine.
    These fields map dynamically into CaptainDiagnose constraints, modifying 
    confidence thresholds before Execution generation.
    """
    seasonality_index: float = Field(ge=0.0, le=1.0)
    demand_shift_score: float = Field(ge=-1.0, le=1.0) # -1.0 means demand collapsed, 1.0 means extreme surge
    volatility_index: float = Field(ge=0.0, le=1.0)
    macro_drift_score: float = Field(ge=-1.0, le=1.0) # -1.0 platform efficiency destroyed, 1.0 improved
    market_phase: str # e.g. "volatile_decline", "stable_growth"
    confidence_modifier: float = Field(ge=0.1, le=1.0) # Represents the final % adjustment to Captain Confidence
