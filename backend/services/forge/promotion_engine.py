import logging
from typing import Dict, Any

from backend.services.forge.models import ExperimentStatus

logger = logging.getLogger(__name__)

class PromotionEngine:
    """
    Executes logic determining the final scaling or termination 
    of experiments once significance boundaries are crossed.
    """

    def __init__(self, experiment_registry, experiment_logger):
        self.registry = experiment_registry
        self.logger = experiment_logger

    async def escalate_winner(self, experiment_record: Dict[str, Any], stats: Dict[str, Any], winner_id: str) -> Dict[str, Any]:
        """
        Variation beat the Control Baseline with statistical significance.
        Commits promotion rules mapping Captain Strategy updates structurally.
        """
        exp_id = experiment_record["experiment_id"]
        logger.info(f"🏆 Promoting Experiment {exp_id} - Winner: {winner_id} (Lift: {stats.get('lift_percentage')}%)")
        
        # Registry Update (PAUSED -> PROMOTED)
        await self.registry.update_status(exp_id, ExperimentStatus.PROMOTED, stats, winner_id)
        
        # Emit final ML EventLabel logic 
        await self.logger.log_experiment_learning(experiment_record, "WINNER", stats.get("confidence_level", 0.0))
        
        return {
             "promotion_action": "REPLACE_CONTROL",
             "target_campaign": experiment_record["campaign_id"],
             "variation_id_to_scale": winner_id,
             "action_type": "APPLY_VARIATION_GLOBALS" # Feeds back to CaptainExecute ultimately
        }

    async def kill_loser(self, experiment_record: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Variation failed the baseline. Revert budget safely backwards.
        """
        exp_id = experiment_record["experiment_id"]
        logger.info(f"💀 Killing Experiment {exp_id} - Loss registered structurally.")
        
        # Registry Update
        await self.registry.update_status(exp_id, ExperimentStatus.KILLED, stats, None)
        
        await self.logger.log_experiment_learning(experiment_record, "LOSER", stats.get("confidence_level", 0.0))
        
        return {
             "promotion_action": "TERMINATE_SANDBOX",
             "target_campaign": experiment_record["campaign_id"],
             "action_type": "REVERT_BUDGET_ALLOCATION"
        }
