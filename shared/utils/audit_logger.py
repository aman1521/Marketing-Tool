from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from shared.models.beanie_models import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Centralized Audit Trail System (Phase 7.1)
    Ensures every mutation (Approve, Reject, Strategy Genesis) is strictly
    tracked and attributed to a user and business tenant for compliance.
    """

    @staticmethod
    async def log_action(
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        business_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Records a mutative action directly into the MongoDB document store.
        """
        try:
            audit_entry = AuditLog(
                user_id=uuid.UUID(user_id) if user_id else None,
                business_id=uuid.UUID(business_id) if business_id else None,
                action=action,
                resource_type=resource_type,
                resource_id=uuid.UUID(resource_id) if resource_id else None,
                before_state=before_state,
                after_state=after_state,
                timestamp=datetime.utcnow()
            )
            await audit_entry.insert()
            logger.info(f"AUDIT LOG INSERTED: [{action}] on [{resource_type}] by user [{user_id}]")
            return True
        except Exception as e:
            logger.error(f"Failed to insert audit log for action '{action}': {str(e)}")
            return False
