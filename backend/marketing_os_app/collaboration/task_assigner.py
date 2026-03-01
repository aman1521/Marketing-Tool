import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from backend.marketing_os_app.ecosystem_models import TaskModel, TaskStatus, TeamRole
from backend.marketing_os_app.collaboration.activity_feed import ActivityFeed
from backend.marketing_os_app.ecosystem_models import ActivityType

logger = logging.getLogger(__name__)

# Signal → Role assignment map
SIGNAL_ROLE_MAP = {
    "CREATIVE_FATIGUE": TeamRole.CREATIVE_STRATEGIST,
    "CONVERSION_ISSUE": TeamRole.MEDIA_BUYER,
    "FUNNEL_GAP": TeamRole.CMO,
    "STRATEGY_GAP": TeamRole.CMO,
    "TRACKING_ISSUE": TeamRole.ANALYST,
    "BUDGET_INEFFICIENCY": TeamRole.FINANCE
}

class TaskAssigner:
    """
    When AI detects a condition requiring human action, it auto-creates
    a structured task and assigns it to the correct role.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.feed = ActivityFeed(db)

    async def create_task(self, company_id: str, signal_type: str,
                           title: str, description: str,
                           supporting_signals: Dict[str, Any] = None) -> str:
        task_id = f"task_{uuid.uuid4().hex[:10]}"
        assigned_role = SIGNAL_ROLE_MAP.get(signal_type, TeamRole.VIEWER)

        task = TaskModel(
            company_id=company_id,
            task_id=task_id,
            title=title,
            description=description,
            signal_type=signal_type,
            assigned_role=assigned_role,
            supporting_signals=supporting_signals or {},
            status=TaskStatus.OPEN
        )
        self.db.add(task)
        await self.db.commit()

        # Emit to activity feed
        await self.feed.emit(
            company_id=company_id,
            activity_type=ActivityType.TASK_CREATED,
            actor="ai_engine",
            summary=f"Task auto-created: {title} → assigned to {assigned_role.value}",
            payload={"task_id": task_id, "signal_type": signal_type}
        )
        logger.info(f"Task {task_id} created for {signal_type} → {assigned_role.value}")
        return task_id

    async def complete_task(self, task_id: str, company_id: str,
                             user_id: str, note: str):
        q = select(TaskModel).where(
            TaskModel.task_id == task_id,
            TaskModel.company_id == company_id
        )
        res = await self.db.execute(q)
        task = res.scalar_one_or_none()
        if not task:
            raise ValueError(f"Task {task_id} not found.")

        task.status = TaskStatus.RESOLVED
        task.completed_at = datetime.utcnow()
        task.completion_note = note
        await self.db.commit()

        await self.feed.emit(
            company_id=company_id,
            activity_type=ActivityType.TASK_COMPLETED,
            actor=user_id,
            summary=f"Task resolved: {task.title}",
            payload={"task_id": task_id, "note": note}
        )
