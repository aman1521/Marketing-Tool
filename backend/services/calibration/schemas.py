from pydantic import BaseModel, Field

class CalibrationOutputSchema(BaseModel):
    """
    Determines if thresholds are mismatched based on historic simulations.
    """
    parameter_name: str
    current_value: float
    suggested_value: float
    decision_lift_score: float = Field(ge=0.0) # E.g., moving confidence threshold from 0.8 -> 0.6 would have secured 15% more ROI last week.
    over_scaling_penalty: float = Field(ge=0.0)
    under_scaling_penalty: float = Field(ge=0.0)
    requires_genesis_approval: bool = True
