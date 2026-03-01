import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.services.sentinel.models import ExecutionAuditLog

logger = logging.getLogger(__name__)

class ExecutionAuditor:
    """
    Sits passively inside ExecutionMonitor collecting exact version mapping logic.
    Who exactly made the decision, based on what models, and what Genesis bounds?
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def audit_execution_loop(self, payload: Dict[str, Any], outcome: Dict[str, Any]) -> ExecutionAuditLog:
        """
        Takes combined logic arrays inserting into explicit Audit tracking.
        Ensures SOC2/Traceability limits.
        """
        
        record = ExecutionAuditLog(
             company_id=payload.get("company_id", "default"),
             campaign_id=payload.get("campaign_id", "unknown"),
             execution_id=payload.get("execution_id", "sim_" + str(datetime.utcnow().timestamp())),
             strategy_version=payload.get("strategy_v", "1.0"),
             diagnosis_version=payload.get("diagnosis_v", "1.0"),
             execution_version=payload.get("execute_v", "1.0"),
             genesis_version=payload.get("genesis_v", "1.0"),
             action_type=payload.get("action_type", "UNKNOWN"),
             expected_delta=payload.get("expected_delta", 0.0),
             actual_delta=outcome.get("real_delta", 0.0)
        )
        
        self.db.add(record)
        await self.db.commit()
        
        logger.info(f"Sentinel Execution Auditor secured lifecycle log: {record.execution_id}")
        return record
