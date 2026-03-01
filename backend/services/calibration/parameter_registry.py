import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.services.calibration.models import ParameterSuggestion

logger = logging.getLogger(__name__)

class ParameterRegistry:
    """
    Safely captures Calibration Engine mappings into DB requests pending
    Genesis Governance approvals.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def log_suggestion(self, company_id: str, suggestion: Dict[str, Any]) -> ParameterSuggestion:
        """Logs deterministic improvements logically tracking approval lifecycles."""
        
        record = ParameterSuggestion(
             company_id=company_id,
             parameter_name=suggestion.get("parameter_name", "UNKNOWN"),
             current_value=suggestion.get("current_value", 0.0),
             suggested_value=suggestion.get("suggested_value", 0.0),
             historical_lift_detected=suggestion.get("decision_lift_score", 0.0),
             penalty_reduced=0.0, # Computed relative
             status="PENDING_GENESIS_APPROVAL"
        )
        
        self.db.add(record)
        await self.db.commit()
        logger.info(f"Calibration locked Parameter Adjustment proposal for Governance Review: {record.parameter_name}")
        
        return record
