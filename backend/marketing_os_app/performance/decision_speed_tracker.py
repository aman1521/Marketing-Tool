import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from backend.marketing_os_app.advanced_models import DecisionSpeedRecord

logger = logging.getLogger(__name__)

# Weighted contribution of each loop stage to the composite DSI
STAGE_WEIGHTS = {
    "diagnose_to_strategy_ms":    0.15,
    "strategy_to_execute_ms":     0.20,
    "execute_to_drift_eval_ms":   0.25,
    "escalation_to_approval_ms":  0.30,   # Heaviest: human latency is largest risk
    "task_create_to_complete_ms": 0.10
}

# Target SLA in ms per stage (24-hour loop target)
SLA_TARGETS_MS = {
    "diagnose_to_strategy_ms":    5_000,       # 5s
    "strategy_to_execute_ms":     10_000,      # 10s
    "execute_to_drift_eval_ms":   3_600_000,   # 1h
    "escalation_to_approval_ms":  14_400_000,  # 4h SLA
    "task_create_to_complete_ms": 86_400_000   # 24h
}

class DecisionSpeedTracker:
    """
    Tracks the end-to-end decision velocity of the intelligence loop.
    Slower approval latency → lower DSI → triggers autonomy extension pressure.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _compute_dsi(self, stages: Dict[str, Optional[float]]) -> float:
        """
        DSI = 100 − weighted penalty score.
        Each stage contributes a penalty proportional to how far it exceeds SLA.
        """
        total_penalty = 0.0
        for stage, weight in STAGE_WEIGHTS.items():
            actual = stages.get(stage)
            if actual is None:
                continue
            target = SLA_TARGETS_MS[stage]
            ratio = actual / max(target, 1.0)
            penalty = max(0.0, ratio - 1.0) * weight * 100
            total_penalty += penalty
        return round(max(0.0, 100.0 - total_penalty), 2)

    async def record(self, company_id: str, campaign_id: str,
                     stages: Dict[str, Optional[float]],
                     approving_role: str = None):
        dsi = self._compute_dsi(stages)
        record = DecisionSpeedRecord(
            company_id=company_id,
            campaign_id=campaign_id,
            diagnose_to_strategy_ms=stages.get("diagnose_to_strategy_ms"),
            strategy_to_execute_ms=stages.get("strategy_to_execute_ms"),
            execute_to_drift_eval_ms=stages.get("execute_to_drift_eval_ms"),
            escalation_to_approval_ms=stages.get("escalation_to_approval_ms"),
            task_create_to_complete_ms=stages.get("task_create_to_complete_ms"),
            decision_speed_index=dsi,
            approving_role=approving_role
        )
        self.db.add(record)
        await self.db.commit()
        logger.info(f"DSI [{company_id}/{campaign_id}] = {dsi}")
        return dsi

    async def get_company_summary(self, company_id: str) -> Dict[str, Any]:
        now = datetime.utcnow()
        day7 = now - timedelta(days=7)
        day30 = now - timedelta(days=30)

        q7 = select(func.avg(DecisionSpeedRecord.decision_speed_index)).where(
            DecisionSpeedRecord.company_id == company_id,
            DecisionSpeedRecord.recorded_at >= day7
        )
        q30 = select(func.avg(DecisionSpeedRecord.decision_speed_index)).where(
            DecisionSpeedRecord.company_id == company_id,
            DecisionSpeedRecord.recorded_at >= day30
        )
        r7  = (await self.db.execute(q7)).scalar() or 0.0
        r30 = (await self.db.execute(q30)).scalar() or 0.0

        # Role-level approval latency
        q_role = select(
            DecisionSpeedRecord.approving_role,
            func.avg(DecisionSpeedRecord.escalation_to_approval_ms)
        ).where(
            DecisionSpeedRecord.company_id == company_id,
            DecisionSpeedRecord.approving_role.isnot(None)
        ).group_by(DecisionSpeedRecord.approving_role)
        role_rows = (await self.db.execute(q_role)).all()
        role_latency = {row[0]: round(row[1] / 60_000, 2) for row in role_rows}

        return {
            "company_id": company_id,
            "dsi_7day_avg": round(r7, 2),
            "dsi_30day_avg": round(r30, 2),
            "approval_latency_by_role_minutes": role_latency,
            "trend": "improving" if r7 > r30 else "degrading"
        }
