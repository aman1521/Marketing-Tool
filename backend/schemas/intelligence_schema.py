"""
Intelligence Schemas
====================
Pydantic schemas specifically for the Frontend API responses. Defines exactly what data
the dashboard receives when querying the AI Marketing OS state.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StrategyRunRequest(BaseModel):
    """Payload to physically trigger a manual cycle from the UI."""
    company_id: str
    industry: str
    current_campaigns: List[Dict[str, Any]] = Field(default_factory=list)

class IntelligenceActionSchema(BaseModel):
    """Singular action blueprint returned to UI."""
    action_type: str
    rationale: str
    payload: Dict[str, Any]

class StrategyRunResponse(BaseModel):
    """Terminal output payload summarizing the entire 5-layer intelligence stack."""
    status: str
    strategy_id: Optional[str] = None
    council_confidence: float = 0.0
    actions_simulated: int = 0
    actions_executed: int = 0
    reason: Optional[str] = None
    execution_mapping: Dict[str, str] = Field(default_factory=dict)

class BackgroundTaskResponse(BaseModel):
    """Async queuing response acknowledging process acceptance."""
    task_id: str
    status: str
    message: str
