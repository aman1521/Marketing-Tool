import logging
from typing import Dict, Any

from backend.services.genesis.schemas import GenesisGoalsSchema, GoalMode

logger = logging.getLogger(__name__)

class GenesisGoalsManager:
    """
    Manages structural limits dictating marketing trajectory (Scale vs Profit).
    """

    def validate_goals(self, payload: Dict[str, Any]) -> GenesisGoalsSchema:
        """
        Validates strategic goals logic and blocks irrational pairings (e.g. extreme scaling + hyper roas requirements)
        """
        try:
            goals = GenesisGoalsSchema(**payload)
            
            # Additional cross-governance logical rules
            if goals.goal_mode == GoalMode.SCALE_FIRST and goals.scaling_aggressiveness < 0.5:
                raise ValueError("Scale-First mode requires minimum scaling aggressiveness of 0.5")
                
            if goals.goal_mode == GoalMode.PROFIT_FIRST and goals.target_roas and goals.target_roas < 1.0:
                raise ValueError("Profit-First mode requires Target ROAS >= 1.0")

            logger.debug(f"Goals validated securely: Mode -> {goals.goal_mode}")
            return goals

        except Exception as e:
            logger.error(f"Goals validation failed: {str(e)}")
            raise ValueError(f"Invalid goals configuration: {str(e)}")
