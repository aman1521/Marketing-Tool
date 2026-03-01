from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PayloadValidator:
    """
    Ensures that the incoming execution action contains properly formatted mathematical 
    boundaries and exact routing definitions before allowing structural analysis.
    """

    def validate(self, action_payload: Dict[str, Any]) -> bool:
        """
        Validates action format.
        Expected format:
        {
            "action_type": "BUDGET_INCREASE" | "CREATIVE_PAUSE",
            "campaign_id": "cmp_123",
            "platform": "meta",
            "parameters": {"new_budget": 1500, "old_budget": 1000}
        }
        """
        required_keys = ["action_type", "campaign_id", "platform", "parameters"]
        
        for key in required_keys:
            if key not in action_payload:
                logger.error(f"PayloadValidator failed: Missing key '{key}'")
                return False
                
        if not isinstance(action_payload["parameters"], dict):
            logger.error("PayloadValidator failed: 'parameters' must be a dictionary")
            return False

        logger.debug(f"Payload validated successfully for {action_payload.get('action_type')}")
        return True
