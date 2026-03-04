"""
Scenario Ranker
===============
A mathematically strict ranking engine applying weighted valuation to each Outcome Prediction.
Returns the absolute best variation of a Strategy Action to route back to the Orchestrator.
"""

from typing import Dict, Any, List
import logging

from .models import Scenario, OutcomePrediction, SimulationResult

logger = logging.getLogger(__name__)

class ScenarioRanker:
    """
    Ranks Outcome Predictions based on a heavily weighted formula prioritizing Growth 
    and Confidence while severely punishing Downside Risk.
    """

    def rank_scenarios(self, scenarios: List[Scenario], outcomes: List[OutcomePrediction], predictions: Dict[str, Dict[str, float]]) -> SimulationResult:
        """
        Calculates a global score for each Outcome, finds the highest rated Variant,
        and constructs the final definitive SimulationResult wrapper.
        """
        best_score = -999.0
        best_scenario = None
        best_outcome = None
        
        scenario_map = {s.id: s for s in scenarios}

        for outcome in outcomes:
            logger.debug(f"[ScenarioRanker] Scoring Outcome for {outcome.scenario_id}")
            
            # The Base AI Operator equation: Growth * Conviction - Risk Variance
            # If Growth drops (pausing losers), we flip the weight mapping slightly to protect margin.
            if outcome.expected_growth < 0 and outcome.expected_cpa_change < 0:
                # Defensive Scoring Mode
                 raw_score = (abs(outcome.expected_cpa_change) * 0.50) + (outcome.confidence_score * 0.40) - (outcome.risk_profile.risk_score * 0.10)
            else:
                # Offensive Scaling Mode
                 raw_score = (outcome.expected_growth * 0.45) + (outcome.confidence_score * 0.35) - (outcome.risk_profile.risk_score * 0.20)

            logger.debug(f"Computed Rank Score: {round(raw_score, 4)} -> {outcome.scenario_id}")

            if raw_score > best_score:
                best_score = raw_score
                best_scenario = scenario_map[outcome.scenario_id]
                best_outcome = outcome

        if best_scenario is None:
             raise ValueError("No valid scenarios were scored by the Ranking Engine.")

        logger.info(f"[ScenarioRanker] Winner selected: {best_scenario.id} with final score {round(best_score, 4)} and risk {best_outcome.risk_profile.risk_score}")

        return SimulationResult(
            best_scenario=best_scenario,
            predicted_metrics=predictions[best_scenario.id],
            risk_score=best_outcome.risk_profile.risk_score,
            confidence=best_outcome.confidence_score,
            all_scenarios_evaluated=len(scenarios)
        )
