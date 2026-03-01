import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from backend.marketing_os_app.ecosystem_models import ActivityFeedModel, ActivityType

logger = logging.getLogger(__name__)

class ActivityFeed:
    """
    Real-time intelligence stream. Every AI action, escalation, rollback
    or human decision emits a structured event that the UI consumes.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def emit(self, company_id: str, activity_type: ActivityType,
                   actor: str, summary: str, payload: Dict[str, Any] = None):
        event = ActivityFeedModel(
            company_id=company_id,
            activity_type=activity_type,
            actor=actor,
            summary=summary,
            payload=payload or {}
        )
        self.db.add(event)
        await self.db.commit()
        logger.info(f"FEED [{company_id}] {activity_type.value}: {summary}")

    async def get_feed(self, company_id: str, limit: int = 50,
                       filter_type: str = None) -> List[Dict[str, Any]]:
        """Returns recent events, optionally filtered by activity_type."""
        query = (
            select(ActivityFeedModel)
            .where(ActivityFeedModel.company_id == company_id)
            .order_by(ActivityFeedModel.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        rows = result.scalars().all()

        events = []
        for r in rows:
            if filter_type and r.activity_type.value != filter_type:
                continue
            events.append({
                "id": r.id,
                "type": r.activity_type.value,
                "actor": r.actor,
                "summary": r.summary,
                "payload": r.payload,
                "timestamp": r.created_at.isoformat()
            })
        return events
