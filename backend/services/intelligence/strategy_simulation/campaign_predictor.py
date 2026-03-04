"""
Campaign Predictor
==================
Simulates expected mathematical shifts (CPA, CTR, ConvRate) 
for proposed Scenarios inside a parsed Environment bounds.
"""

from typing import Dict, Any, List
import logging

from .models import Scenario, EnvironmentState

logger = logging.getLogger(__name__)

class CampaignPredictor:
    """
    Takes scenarios and the mathematical boundaries of the environment,
    outputting raw statistical shifts expected.
    """

    def predict(self, scenarios: List[Scenario], environment: EnvironmentState) -> Dict[str, Dict[str, float]]:
        """
        Evaluate each scenario's parameters against the environmental state.
        Returns expected CTR delta, CPA delta, and Revenue shift per Scenario ID.
        """
        predictions = {}

        for scenario in scenarios:
            logger.debug(f"[CampaignPredictor] Simulating {scenario.action_type} - {scenario.id}")
            
            # Start flatly neutral
            ctr_change = 0.0
            cpa_change = 0.0
            rev_change = 0.0
            
            # Extract logic params
            action = scenario.action_type
            params = scenario.parameter_variations

            # Hypothesis 1: Aggressively scaling into high saturation -> Rapid CPR rise.
            if action == "SCALE_BUDGET":
                inc = params.get("increase_pct", 0) / 100.0
                
                # Model the scaling penalty based on saturation curve
                cpa_penalty = inc * (1.1 + environment.audience_saturation) 
                cpa_change = cpa_penalty
                
                # Revenue grows alongside budget but at deteriorating efficiency
                rev_change = inc * (1.0 - (cpa_penalty * 0.8))
                ctr_change = -0.05 * inc # Slight decay as frequency builds
                
            # Hypothesis 2: A brand new creative angle drops saturation and boosts CTR. 
            elif action == "NEW_CREATIVE_ANGLE":
                if environment.audience_saturation > 0.7:
                     cpa_change = -0.15 # Massive relief from fatigue
                     ctr_change = 0.40  # Massive swing on fresh hook
                     rev_change = 0.10
                else:
                     cpa_change = -0.05
                     ctr_change = 0.15
                     rev_change = 0.05

            # Hypothesis 3: Bidding / Market platform shifts into low pressure zones.
            elif action == "PLATFORM_SHIFT" or action == "AUDIENCE_EXPANSION":
                cpa_change = -0.10 # Finding cheap inventory
                ctr_change = 0.05
                rev_change = 0.15
                
            # Hypothesis 4: Turning off fatiguing creatives protects margin.
            elif action == "PAUSE_CAMPAIGN":
                cpa_change = -0.08
                ctr_change = 0.02
                # Loss of absolute revenue volume vs efficiency trade-off
                method = params.get("method", "hard_pause")
                rev_change = -0.10 if method == "hard_pause" else -0.04
                
            # Add results to collection
            predictions[scenario.id] = {
                "ctr_change": round(ctr_change, 3),
                "cpa_change": round(cpa_change, 3),
                "revenue_change": round(rev_change, 3)
            }

        return predictions
