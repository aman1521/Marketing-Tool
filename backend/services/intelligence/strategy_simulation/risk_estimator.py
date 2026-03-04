"""
Risk Estimator
==============
Estimates the downside volatility of each Scenario inside the EnvironmentState.
Predicts how likely the scaling or pivoting is to fail or bounce against limits.
"""

from typing import Dict, Any, List
import logging

from .models import Scenario, EnvironmentState, RiskProfile

logger = logging.getLogger(__name__)

class RiskEstimator:
    """
    Simulates the likelihood of strategies causing budget runaway, audience fatigue,
    or provoking aggressive competitor spend reaction.
    """

    def estimate_risks(self, scenarios: List[Scenario], predictions: Dict[str, Dict[str, float]], environment: EnvironmentState) -> Dict[str, RiskProfile]:
        """
        Evaluate each scenario's bounds and return a structured RiskProfile.
        Downside risks map directly into Outcome Analysis confidence levels.
        """
        risk_profiles = {}

        for scenario in scenarios:
            logger.debug(f"[RiskEstimator] Calculating downside volatility for {scenario.action_type}")
            
            action = scenario.action_type
            params = scenario.parameter_variations
            
            # Start neutral
            volatility = 0.20
            uncertainty = 0.30
            factors = []

            # Hypothesis 1: Aggressive scaling in a saturated market explodes CPA unpredictably.
            if action == "SCALE_BUDGET":
                inc = params.get("increase_pct", 0) / 100.0
                if environment.audience_saturation > 0.8:
                    volatility += 0.40 # Very risky
                    factors.append("Scale budget against high saturation boundary")
                elif inc > 0.30:
                    volatility += 0.30
                    factors.append("Aggressive scale velocity exceeds threshold")
                
                uncertainty += 0.10 # Known mechanic, but unknown threshold bounce
                
            # Hypothesis 2: Brand new creative pivots have high uncertainty but lower volatility.
            elif action == "NEW_CREATIVE_ANGLE":
                if environment.competitor_pressure > 0.7:
                     volatility += 0.10
                     factors.append("New creative entering high pressure zone")
                     
                arch_count = len(params.get("archetypes", ["1"])) if "archetypes" in params else 1
                if arch_count >= 3:
                     uncertainty += 0.30 # Multivariate testing adds fog
                     factors.append("Broad multi-variate test surface")
                else:     
                     uncertainty += 0.15 # Baseline novelty risk
                     factors.append("New angle unpredictability")
                     
            # Hypothesis 3: Bidding / Market platform shifts into low pressure zones.
            elif action == "PLATFORM_SHIFT" or action == "AUDIENCE_EXPANSION":
                uncertainty += 0.40 # Going broad = highly unknown
                volatility += 0.10
                factors.append("Unknown inventory / algorithmic reset")
                
            # Hypothesis 4: Turning off fatiguing creatives protects margin, has low risk!
            elif action == "PAUSE_CAMPAIGN":
                volatility = 0.05
                uncertainty = 0.10
                factors.append("Defensive contraction protects spend")

            # Final Normalization and Assembly
            final_volatility = min(1.0, max(0.0, volatility))
            final_uncertainty = min(1.0, max(0.0, uncertainty))
            
            # The Risk Score is a weighted fusion of volatility (budget swings) and uncertainty (ML fog)
            risk_score = round((final_volatility * 0.6) + (final_uncertainty * 0.4), 3)

            risk_profiles[scenario.id] = RiskProfile(
                risk_score=risk_score,
                volatility_score=round(final_volatility, 3),
                uncertainty_score=round(final_uncertainty, 3),
                risk_factors=factors
            )

        return risk_profiles
