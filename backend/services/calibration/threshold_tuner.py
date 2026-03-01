import logging
from typing import Dict, Any

from backend.services.calibration.schemas import CalibrationOutputSchema

logger = logging.getLogger(__name__)

class ThresholdTuner:
    """
    Reads backtested penalty structures and evaluates if an adjustment parameter
    warrants sending a formalized Governance request to Genesis.
    """

    def calculate_optimal_threshold(self, parameter_name: str, baseline_value: float, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews multiple variations evaluated by the Backtester.
        """
        logger.info(f"Calibration evaluating optimal setting for {parameter_name}")
        
        lift = backtest_results.get("decision_lift_score", 0.0)
        penalty = backtest_results.get("over_scaling_penalty", 0.0)
        
        # Simple logical heuristic: Does the proposed execution lift heavily outweigh the penalty?
        # A ratio > 2.0 (We make $2 for every $1 we misclassify)
        suggested_value = baseline_value
        if lift > (penalty * 2.0) and lift > 0.1:
            suggested_value = backtest_results.get("simulated_threshold", baseline_value)
            logger.warning(f"Calibration identified inefficient OS threshold! Proposing {baseline_value} -> {suggested_value}")
            
        payload = CalibrationOutputSchema(
            parameter_name=parameter_name,
            current_value=baseline_value,
            suggested_value=suggested_value,
            decision_lift_score=lift,
            over_scaling_penalty=penalty,
            under_scaling_penalty=0.0,
            requires_genesis_approval=True
        )
        
        return payload.model_dump()
