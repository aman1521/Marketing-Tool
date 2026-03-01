import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.marketing_os_app.ecosystem_models import UsageSnapshotModel

logger = logging.getLogger(__name__)

class UsageMeter:
    """
    Tracks all metered usage per tenant per period.
    Feeds billing layer + AI impact engine.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_event(self, company_id: str, event_type: str,
                            amount: float = 1.0, meta: Dict[str, Any] = None):
        """
        event_type: execution | experiment | creative_analysis |
                    calibration | escalation | rollback
        """
        logger.debug(f"USAGE [{company_id}] {event_type} × {amount}")
        # In production: increment Redis counters + persist to UsageSnapshotModel periodically
        # Here: log for traceability
        pass

    async def get_current_period_summary(self, company_id: str) -> Dict[str, Any]:
        """Returns latest usage snapshot."""
        q = (
            select(UsageSnapshotModel)
            .where(UsageSnapshotModel.company_id == company_id)
            .order_by(UsageSnapshotModel.computed_at.desc())
            .limit(1)
        )
        res = await self.db.execute(q)
        row = res.scalar_one_or_none()
        if not row:
            return {"company_id": company_id, "no_data": True}
        return {
            "company_id": company_id,
            "executions_count": row.executions_count,
            "budget_modified_usd": row.budget_modified_usd,
            "experiments_launched": row.experiments_launched,
            "creative_analyses": row.creative_analyses,
            "calibration_runs": row.calibration_runs,
            "escalations_triggered": row.escalations_triggered,
            "autonomy_percentage": row.autonomy_percentage,
            "avg_approval_latency_minutes": row.avg_approval_latency_minutes,
            "period_start": row.period_start.isoformat(),
            "period_end": row.period_end.isoformat()
        }
