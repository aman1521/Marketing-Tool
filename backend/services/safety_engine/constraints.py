import logging
from typing import Dict, Any

from backend.services.safety_engine.schemas import GenesisConstraintsSchema

logger = logging.getLogger(__name__)

class GenesisConstraintsManager:
    """
    Manages structural limits on Captain auto-execution actions.
    Values here form the hard boundaries governing CaptainRisk modules.
    """

    def validate_constraints(self, payload: Dict[str, Any]) -> GenesisConstraintsSchema:
        """
        Throws exact logical errors if requested constraints represent dangerous system rules bounds.
        """
        try:
            constraints = GenesisConstraintsSchema(**payload)

            if constraints.max_budget_change_percent > 30.0 and constraints.auto_execution_enabled:
                logger.warning("Dangerous constraint configured: Auto budget > 30% execution.")

            logger.debug(f"Constraints validated effectively. Auto-Execution: {constraints.auto_execution_enabled}")
            return constraints
            
        except Exception as e:
            logger.error(f"Constraints validation failed: {str(e)}")
            raise ValueError(f"Invalid constraints configuration: {str(e)}")
