import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.execution.forge.experiment_registry import ExperimentRegistry
from backend.services.execution.forge.variation_generator import VariationGenerator
from backend.services.execution.forge.allocation_manager import AllocationManager
from backend.services.execution.forge.sandbox_controller import SandboxController
from backend.services.execution.forge.significance_engine import SignificanceEngine
from backend.services.execution.forge.promotion_engine import PromotionEngine
from backend.services.execution.forge.experiment_logger import ExperimentLogger
from backend.services.execution.forge.models import ExperimentStatus

logger = logging.getLogger(__name__)

class ForgeExperimentEngine:
    """
    Capstone structure orchestrating the full Forge Sandbox lifecycle.
    Wraps deterministic constraints dynamically across 6 sub-engines securely.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.registry = ExperimentRegistry(db_session)
        self.variations = VariationGenerator()
        self.allocator = AllocationManager()
        self.sandbox = SandboxController()
        self.significance = SignificanceEngine()
        self.logger = ExperimentLogger()
        self.promotion = PromotionEngine(self.registry, self.logger)

    async def launch_experiment(self, 
                                campaign_id: str, 
                                company_id: str, 
                                diagnosis_state: str, 
                                total_budget: float, 
                                genesis_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiated by CaptainStrategy. Synthesizes hypothesis, verifies constraints dynamically, 
        assigns capital and registers the ML tracking loops safely.
        """
        logger.info(f"Forge Engine starting launch sequence for Campaign: {campaign_id}")
        
        # 1. Structural Validation via Genesis Constraints map
        if not genesis_env.get("constraints", {}).get("creative_sandbox_required", True):
             return {"status": "blocked", "reason": "genesis_sandboxes_disabled"}
             
        # 2. Risk & Budget mapping via AllocationManager
        tier = genesis_env.get("mappings", {}).get("aggression_tier", "Moderate")
        test_budget = self.allocator.allocate_sandbox_budget(total_budget, tier)
        
        if not self.sandbox.check_sandbox_safe(test_budget, total_budget, genesis_env.get("constraints", {})):
             return {"status": "blocked", "reason": "sandbox_budget_cap_exceeded"}

        # 3. Generate Valid Variation Arrays
        experiment_schema = self.variations.generate_variations(diagnosis_state, genesis_env)
        
        experiment_data = {
            "company_id": company_id,
            "campaign_id": campaign_id,
            "hypothesis": experiment_schema["hypothesis"],
            "experiment_type": experiment_schema["experiment_type"],
            "variations": experiment_schema["variations"],
            "sandbox_budget": test_budget
        }
        
        # 4. Record to DB actively
        exp_id = await self.registry.register_experiment(experiment_data)
        
        # 5. Format Output back to CaptainExecute targeting payload
        return {
            "status": "launched",
            "experiment_id": exp_id,
            "sandbox_budget_assigned": test_budget,
            "captain_action_payload": {
                 "action_type": "INITIATE_FORGE_SANDBOX",
                 "campaign_id": campaign_id,
                 "platform": "auto",  # Captain Router abstracts
                 "parameters": {
                      "isolation": self.sandbox.calculate_isolation_parameters(campaign_id, "all"),
                      "variations": experiment_schema["variations"]
                 }
            }
        }

    async def evaluate_running_experiment(self, experiment_record: Dict[str, Any], control_stats: Dict[str, Any], variation_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called post-launch by ExecutionMonitor loops natively determining if significance
        is crossed over time actively.
        """
        
        if experiment_record.get("status") != ExperimentStatus.RUNNING:
             return {"status": "ignored", "reason": "experiment_not_active"}
             
        # Execute Z-Test Engine
        sig_results = self.significance.evaluate_experiment(control_stats, variation_stats)
        
        # Act entirely deterministically upon output
        if sig_results["significant"] and sig_results["lift_percentage"] > 0:
             # Promote Win
             consequences = await self.promotion.escalate_winner(experiment_record, sig_results, "variation_1")
             return {"status": "resolved", "outcome": "promoted", "escalation": consequences}
             
        elif sig_results["p_value"] < 0.1 and sig_results["lift_percentage"] < 0:
             # Confirm strict Loss
             consequences = await self.promotion.kill_loser(experiment_record, sig_results)
             return {"status": "resolved", "outcome": "killed", "escalation": consequences}
             
        else:
             # Continue burning sandbox budget actively tracking (No P-Val hit)
             return {"status": "running", "outcome": "inconclusive", "current_stats": sig_results}
