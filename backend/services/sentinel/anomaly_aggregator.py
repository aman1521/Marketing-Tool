import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.sentinel.models import SystemAnomalyLog

logger = logging.getLogger(__name__)

class AnomalyAggregator:
    """
    Groups and labels misclassifications preventing false signals from continuously firing
    without Sentinel categorizing them as 'Noise'.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def record_anomaly(self, anomaly_type: str, severity: str, details: Dict[str, Any]) -> SystemAnomalyLog:
        """
        E.g. "FATIGUE_FALSE_POSITIVE" when Hawkeye kills an ad too early, but Manual intervention brings it back.
        """
        record = SystemAnomalyLog(
            anomaly_type=anomaly_type,
            severity_label=severity,
            details=details
        )
        self.db.add(record)
        await self.db.commit()
        logger.warning(f"Sentinel Anomaly Aggregated: [{anomaly_type}] - {severity}")
        return record
        
    def detect_budget_overexposure(self, allocated_spend: float, revenue_target: float) -> bool:
        """
        Basic guard tracking gross divergence logic passively.
        """
        if revenue_target > 0 and (allocated_spend / revenue_target) > 5.0: # 5x CPA threshold
            logger.error("Sentinel identified severe Budget Overexposure risk on trailing 2h spend velocity.")
            return True
        return False
