import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from backend.marketing_os_app.ecosystem_models import (
    EscalationLogModel, EscalationStatus, ActivityFeedModel, ActivityType
)
from backend.marketing_os_app.collaboration.role_matrix import get_escalation_targets
from backend.marketing_os_app.collaboration.activity_feed import ActivityFeed

logger = logging.getLogger(__name__)


class EscalationEngine:
    """
    Triggered when EnvelopeManager detects a breach.
    Logs the full context, routes to appropriate roles, blocks execution.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.feed = ActivityFeed(db)

    async def trigger_escalation(self, company_id: str, breach_type: str,
                                  action_payload: Dict[str, Any],
                                  envelope_snapshot: Dict[str, Any],
                                  exposure_snapshot: Dict[str, Any],
                                  risk_snapshot: Dict[str, Any]) -> str:
        escalation_id = f"esc_{uuid.uuid4().hex[:10]}"
        routed_to = get_escalation_targets(breach_type)

        record = EscalationLogModel(
            company_id=company_id,
            escalation_id=escalation_id,
            breach_type=breach_type,
            action_payload=action_payload,
            envelope_snapshot=envelope_snapshot,
            exposure_snapshot=exposure_snapshot,
            risk_snapshot=risk_snapshot,
            routed_to_roles=routed_to,
            status=EscalationStatus.PENDING
        )
        self.db.add(record)
        await self.db.commit()

        await self.feed.emit(
            company_id=company_id,
            activity_type=ActivityType.ESCALATION,
            actor="ai_engine",
            summary=f"Escalation {breach_type} raised → routed to {routed_to}",
            payload={"escalation_id": escalation_id, "breach_type": breach_type}
        )

        logger.warning(f"ESCALATION [{company_id}] {breach_type} → {routed_to} | ID: {escalation_id}")
        return escalation_id

    async def resolve_escalation(self, escalation_id: str, company_id: str,
                                  resolved_by: str, decision: str, note: str):
        from sqlalchemy import select
        q = select(EscalationLogModel).where(
            EscalationLogModel.escalation_id == escalation_id,
            EscalationLogModel.company_id == company_id
        )
        res = await self.db.execute(q)
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError(f"Escalation {escalation_id} not found.")

        record.status = EscalationStatus.APPROVED if decision == "approved" else EscalationStatus.REJECTED
        record.resolved_by = resolved_by
        record.resolution_note = note
        record.resolved_at = datetime.utcnow()
        await self.db.commit()

        await self.feed.emit(
            company_id=company_id,
            activity_type=ActivityType.APPROVAL,
            actor=resolved_by,
            summary=f"Escalation {escalation_id} {decision} by {resolved_by}",
            payload={"escalation_id": escalation_id, "decision": decision}
        )
