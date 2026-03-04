"""
Strategy Simulation Engine Models
=================================
Data definitions for the Strategy Simulation Engine, validating generated
scenarios against historical performance environments.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Scenario(BaseModel):
    """A generated variation of a proposed strategy action."""
    id: str
    strategy_reference: str
    action_type: str
    parameter_variations: Dict[str, Any]


class EnvironmentState(BaseModel):
    """The current mathematical realities of the ad platforms/audience."""
    average_cpm: float
    average_ctr: float
    conversion_rate: float
    audience_saturation: float
    competitor_pressure: float


class RiskProfile(BaseModel):
    """Calculated downside vulnerabilities for a specific scenario."""
    risk_score: float = Field(ge=0.0, le=1.0)
    volatility_score: float = Field(ge=0.0, le=1.0)
    uncertainty_score: float = Field(ge=0.0, le=1.0)
    risk_factors: List[str]


class OutcomePrediction(BaseModel):
    """The combined estimation of performance + risk for a scenario."""
    scenario_id: str
    expected_growth: float
    expected_cpa_change: float
    expected_roi: float
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_profile: RiskProfile


class SimulationResult(BaseModel):
    """The definitive output representing the chosen scenario."""
    best_scenario: Scenario
    predicted_metrics: Dict[str, float]  # e.g., ctr_change, cpa_change, revenue_change
    risk_score: float
    confidence: float
    all_scenarios_evaluated: int


class SimulationLog(BaseModel):
    """Data persistence object for training the future ML simulator models."""
    strategy_id: str
    scenarios_generated: int
    predictions: List[Dict[str, Any]]
    final_selected_scenario: str
