import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from backend.marketing_os_app.ecosystem_models import DecisionThreadModel

logger = logging.getLogger(__name__)

class CommentThreads:
    """
    Every AI execution action carries a full decision thread:
    Envelope snapshot, risk context, simulation summary, comments, approvals.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thread(self, company_id: str, action_type: str,
                             envelope_snapshot: Dict, risk_context: Dict,
                             simulation_summary: Dict) -> str:
        thread_id = f"thread_{uuid.uuid4().hex[:10]}"
        thread = DecisionThreadModel(
            company_id=company_id,
            thread_id=thread_id,
            action_type=action_type,
            envelope_snapshot=envelope_snapshot,
            risk_context=risk_context,
            simulation_summary=simulation_summary,
            execution_result=None,
            comments=[],
            approval_history=[]
        )
        self.db.add(thread)
        await self.db.commit()
        logger.info(f"Decision thread created: {thread_id}")
        return thread_id

    async def add_comment(self, thread_id: str, user_id: str,
                           comment: str, company_id: str):
        from sqlalchemy import select
        q = select(DecisionThreadModel).where(
            DecisionThreadModel.thread_id == thread_id,
            DecisionThreadModel.company_id == company_id
        )
        res = await self.db.execute(q)
        thread = res.scalar_one_or_none()
        if not thread:
            raise ValueError(f"Thread {thread_id} not found.")

        thread.comments = thread.comments + [{
            "user_id": user_id,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        }]
        await self.db.commit()

    async def record_approval(self, thread_id: str, user_id: str,
                               decision: str, note: str, company_id: str):
        from sqlalchemy import select
        q = select(DecisionThreadModel).where(
            DecisionThreadModel.thread_id == thread_id,
            DecisionThreadModel.company_id == company_id
        )
        res = await self.db.execute(q)
        thread = res.scalar_one_or_none()
        if not thread:
            raise ValueError(f"Thread {thread_id} not found.")

        thread.approval_history = thread.approval_history + [{
            "user_id": user_id,
            "decision": decision,   # "approved" | "rejected"
            "note": note,
            "timestamp": datetime.utcnow().isoformat()
        }]
        await self.db.commit()
