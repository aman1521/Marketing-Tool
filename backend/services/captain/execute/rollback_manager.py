from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RollbackManager:
    """
    Executes defensive reversion mechanisms if the ExecutionMonitor detects 
    anomalous ROAS collapse or platform errors post-autonomy.
    """
    def __init__(self, platform_router):
        self.router = platform_router

    async def attempt_rollback(self, execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read the parameters originally modified and dispatch the inverse payload natively.
        """
        action = execution_record.get("action", {})
        action_type = action.get("action_type")
        params = action.get("parameters", {})
        
        new_payload = action.copy()
        
        if action_type == "BUDGET_INCREASE":
            # Revert to old budget
            logger.warning(f"ROLLBACK INITIATED: Reverting budget for {action.get('campaign_id')} to {params.get('old_budget')}")
            new_payload["action_type"] = "BUDGET_DECREASE"
            new_payload["parameters"] = {
                "new_budget": params.get("old_budget"),
                "old_budget": params.get("new_budget")
            }
        elif action_type == "PAUSE_CREATIVE":
            logger.warning(f"ROLLBACK INITIATED: Reactivating creative for {action.get('campaign_id')}")
            new_payload["action_type"] = "ACTIVATE_CREATIVE"
            
        # Dispatch Rollback specific payload
        rollback_resp = await self.router.dispatch_action(new_payload)
        
        return rollback_resp
