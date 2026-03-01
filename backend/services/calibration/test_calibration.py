import pytest
import asyncio
from unittest.mock import AsyncMock

from backend.services.calibration.backtester import Backtester
from backend.services.calibration.threshold_tuner import ThresholdTuner
from backend.services.calibration.outcome_analyzer import OutcomeAnalyzer
from backend.services.calibration.parameter_registry import ParameterRegistry
from backend.services.calibration.schemas import CalibrationOutputSchema

def test_backtester_logic():
    bt = Backtester()
    
    # Simulating history where Confidence Score spiked to 0.70 and historically succeeded (ROI > 1) 
    # but our OLD Threshold was 0.80, so we missed the lift!
    historical = [
         {"confidence_score_at_time": 0.72, "actual_roi": 2.5, "action_taken": "NONE"}
    ]
    
    # We test what happens if we LOWERED the Threshold to 0.65
    res = bt.simulate_decision_matrix(historical, simulated_threshold=0.65)
    
    # Backtester should compute we missed +1.5x ROI (2.5 - 1.0) due to overly strict bounds
    assert res["decision_lift_score"] == 1.5
    assert res["over_scaling_penalty"] == 0.0

def test_threshold_tuner_proposals():
    tuner = ThresholdTuner()
    
    # A backtest proves lowering the bound gives massive lift against penalties (Ratio > 2:1)
    res_suggested = tuner.calculate_optimal_threshold(
         "min_allowed_roas", 2.0,
         {"simulated_threshold": 1.5, "decision_lift_score": 10.0, "over_scaling_penalty": 1.0}
    )
    
    # Suggestion mapped successfully!
    assert res_suggested["suggested_value"] == 1.5
    assert res_suggested["requires_genesis_approval"] == True
    
    # Fail test (Penalty too high, overrides lift ratios)
    res_rejected = tuner.calculate_optimal_threshold(
         "min_allowed_roas", 2.0,
         {"simulated_threshold": 1.0, "decision_lift_score": 2.5, "over_scaling_penalty": 5.0}
    )
    
    # Suggestion aborted! Maintains baseline of 2.0 safely.
    assert res_rejected["suggested_value"] == 2.0

def test_outcome_analyzer_hallucination():
    oa = OutcomeAnalyzer()
    
    # True error > 0.5 (Catastrophic)
    gap1 = oa.analyze_error_gap(simulated_roi=3.5, realized_roi=0.8, expected_volatility=0.2)
    assert gap1 > 2.0
    
    # Perfect alignment tracking
    gap2 = oa.analyze_error_gap(simulated_roi=1.2, realized_roi=1.1, expected_volatility=0.2)
    assert gap2 == 0.0

@pytest.mark.asyncio
async def test_parameter_registry():
    mock_db = AsyncMock()
    reg = ParameterRegistry(mock_db)
    
    res = await reg.log_suggestion("test_company", {
        "parameter_name": "auto_execution_confidence",
        "current_value": 0.8,
        "suggested_value": 0.65,
        "decision_lift_score": 3.0
    })
    
    assert res.parameter_name == "auto_execution_confidence"
    assert res.suggested_value == 0.65
    assert res.status == "PENDING_GENESIS_APPROVAL"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
