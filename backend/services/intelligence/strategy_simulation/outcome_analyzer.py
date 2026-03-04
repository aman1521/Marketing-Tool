"""
Outcome Analyzer
================
Matches individual Scenario logic predictions against the estimated
Risk Profiles to calculate definitive ROI shifts and global Confidence.
"""

from typing import Dict, Any, List
import logging

from .models import Scenario, RiskProfile, OutcomePrediction

logger = logging.getLogger(__name__)

class OutcomeAnalyzer:
    """
    Computes an expected growth vector and scales Confidence proportionally against Risk.
    """

    def analyze_outcomes(self, scenarios: List[Scenario], predictions: Dict[str, Dict[str, float]], risk_profiles: Dict[str, RiskProfile]) -> List[OutcomePrediction]:
        """
        Calculates Net ROI and scales overall ML confidence using the baseline action's inherent risk.
        Returns array of robust Outcome Predictions representing each generated Scenario's future state.
        """
        outcomes = []

        for scenario in scenarios:
            logger.debug(f"[OutcomeAnalyzer] Computing ROI fusion for {scenario.id}")
            
            preds = predictions[scenario.id]
            risk = risk_profiles[scenario.id]
            
            cpa_shift = preds["cpa_change"]
            rev_shift = preds["revenue_change"]
            
            # Simple ROI approximation: (Revenue gain - Cost gain) / Cost
            # Here: if CPA drops (gets cheaper) AND Revenue grows, ROI explodes positively.
            # If CPA drops AND Revenue drops (Pausing losers), ROI improves but growth is negative.
            if cpa_shift > 0:
                expected_roi = rev_shift - (cpa_shift * 0.5) 
            else:
                expected_roi = rev_shift + (abs(cpa_shift) * 0.8)
                
            expected_growth = rev_shift

            # System Confidence decays exponentially against Volatility and Uncertainty Risk
            base_confidence = 0.90
            adjusted_confidence = base_confidence - (risk.volatility_score * 0.4) - (risk.uncertainty_score * 0.5)
            
            # Action specific hard-bounds
            if scenario.action_type == "PAUSE_CAMPAIGN":
               adjusted_confidence = min(0.95, adjusted_confidence + 0.15) # Pausing is highly deterministic

            outcomes.append(OutcomePrediction(
                scenario_id=scenario.id,
                expected_growth=round(expected_growth, 3),
                expected_cpa_change=round(cpa_shift, 3),
                expected_roi=round(expected_roi, 3),
                confidence_score=round(max(0.1, adjusted_confidence), 3),
                risk_profile=risk
            ))

        return outcomes
