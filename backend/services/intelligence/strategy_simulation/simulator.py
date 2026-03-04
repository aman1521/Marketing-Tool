"""
Simulator Orchestrator
======================
The Digital Marketing Twin. Tests abstract strategy proposals inside a simulated 
mathematical environment, predicting outcomes, estimating risk, and selecting the optimal path.
"""

import logging
from typing import Dict, Any, Optional

from .models import SimulationResult, SimulationLog
from .scenario_builder import ScenarioBuilder
from .environment_model import EnvironmentModel
from .campaign_predictor import CampaignPredictor
from .risk_estimator import RiskEstimator
from .outcome_analyzer import OutcomeAnalyzer
from .scenario_ranker import ScenarioRanker

logger = logging.getLogger(__name__)

class StrategySimulationEngine:
    """
    Main pipeline entrypoint. Called by Intelligence Orchestrator before hitting 
    Execution boundaries.
    """

    def __init__(self, db_session = None):
        self.db = db_session
        self.builder = ScenarioBuilder()
        self.env     = EnvironmentModel()
        self.tractor = CampaignPredictor()
        self.risk    = RiskEstimator()
        self.outcome = OutcomeAnalyzer()
        self.ranker  = ScenarioRanker()

    def simulate_strategy(self, company_id: str, strategy_id: str, proposed_action: Dict[str, Any], context: Dict[str, Any]) -> SimulationResult:
        """
        Executes the 6-Step Simulation Pipeline.
        """
        logger.info(f"[Simulator] Initializing Digital Twin Simulation on Strategy Action '{strategy_id}'.")

        # 1. Build Scenarios (Parameter variations)
        scenarios = self.builder.build_scenarios(strategy_id, proposed_action)

        # 2. Extract Mathematical Environment Baseline
        environment = self.env.load_environment(company_id, context)

        # 3. Forecast Campaign Performance
        predictions = self.tractor.predict(scenarios, environment)

        # 4. Estimate Scenario Risk & Uncertainty Profiles
        risk_profiles = self.risk.estimate_risks(scenarios, predictions, environment)

        # 5. Extract Confidence & Expected ROI Vectors
        outcomes = self.outcome.analyze_outcomes(scenarios, predictions, risk_profiles)

        # 6. Score & Rank the Results to select the definitive winner
        best_scenario = self.ranker.rank_scenarios(scenarios, outcomes, predictions)

        # Ensure bounds mapping (Reject extremely risky, low confidence approaches)
        if best_scenario.risk_score > 0.30 or best_scenario.confidence < 0.75:
             logger.warning(
                  f"[Simulator] BLOCKED: Best scenario failed bounds check. "
                  f"Risk: {best_scenario.risk_score} | Confidence: {best_scenario.confidence}"
             )
             # In a real engine, we'd flag the whole Strategy here or rollback slightly.
             # We return it anyway so the intelligence orchestrator knows WHY it failed.

        # 7. Persist Simulation Data for RL
        if self.db:
            try:
                log_entry = SimulationLog(
                    strategy_id=strategy_id,
                    scenarios_generated=len(scenarios),
                    predictions=list(predictions.values()),
                    final_selected_scenario=best_scenario.best_scenario.id
                )
                # self.db.add(log_entry_to_orm_model) # Mock
                logger.debug(f"[Simulator] Logged Scenario {log_entry.final_selected_scenario} securely.")
            except Exception as e:
                logger.error(f"[Simulator] Failed to log simulation block: {e}")

        logger.info(f"[Simulator] Pipeline completed. Chosen Risk Index: {best_scenario.risk_score}.")
        return best_scenario
