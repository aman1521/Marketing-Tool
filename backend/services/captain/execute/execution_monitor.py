from typing import Dict, Any, List
import logging
import asyncio

from backend.services.captain.execute.rollback_manager import RollbackManager
from backend.services.captain.execute.execution_logger import ExecutionLogger

logger = logging.getLogger(__name__)

class ExecutionMonitor:
    """
    Long-running background agent verifying the expected outputs of CaptainStrategy against
    AtlasSignals after a 24/48-hour delay window.
    Triggers Rollbacks exclusively if expected trajectory flips destructively.
    """
    
    def __init__(self, rollback_mgr: RollbackManager, logger_instance: ExecutionLogger):
        self.rollback = rollback_mgr
        self.exec_logger = logger_instance

    async def trigger_monitoring_loop(self, execution_record: Dict[str, Any], wait_hours: int = 24):
        """
        Kicks off asynchronous celery-based polling evaluating the post-action Atlas ingestion.
        """
        action = execution_record.get("action", {})
        c_id = action.get("campaign_id", "unknown")
        
        logger.info(f"Monitoring Triggered: Verifying '{action.get('action_type')}' outcome for {c_id} in {wait_hours}hrs.")
        
        # In actual system, schedules a Celery Task.
        # For validation simulation, run direct evaluation mock.
        
        await self._evaluate_drift(execution_record)
        
    async def _evaluate_drift(self, execution_record: Dict[str, Any]):
        """
        Called when the wait_hours sleep expires. Assesses ROAS or CPA deviation.
        """
        # Pseudo: Fetch AtlasSignals(c_id)
        # compare to execution_record["context"]["features"]["roas_1d"]
        
        # Simulating drift threshold failure randomly or deterministically
        simulation_roas_drop = 0.35 # (35% drop in ROAS = Danger)
        action_type = execution_record.get("action", {}).get("action_type")
        c_id = execution_record.get("action", {}).get("campaign_id")
        
        if simulation_roas_drop > 0.2 and action_type == "BUDGET_INCREASE":
             logger.error(f"Execution Monitor Detects Fatal Deviation: ROAS fell {simulation_roas_drop*100}% post-execution on {c_id}.")
             
             # Trigger Reversal
             resp = await self.rollback.attempt_rollback(execution_record)
             
             # Append Failure label to EventLogger for Hybrid learning 
             await self.exec_logger.log_action(
                 action={"type": "ROLLBACK_TRIGGERED", "target": action_type}, 
                 context={"drift_delta": simulation_roas_drop},
                 status="reversal_complete",
                 error_detail="ROAS failed to hold at new budget limits."
             )
             
             return False

        logger.info(f"Execution {c_id} stabilized within baseline variance. Optimization secure.")
        return True
