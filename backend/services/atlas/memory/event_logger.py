import logging
import json
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.atlas.models import EventLog

logger = logging.getLogger(__name__)

class EventLogger:
    """
    Structured Logging utility persisting inputs and outputs for any ML/Rule-Engine executions.
    Serves as the foundation for the hybrid active learning loops.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    def hash_payload(self, payload: Dict[str, Any]) -> str:
        """Securely build a hash representation of inputs to avoid duplicate training payloads."""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    async def log_execution(self, engine_name: str, engine_version: str, input_payload: Dict[str, Any], output_blob: Dict[str, Any], confidence: Optional[float] = None, label: Optional[str] = None):
        """Append to EventLog immediately."""
        input_hash = self.hash_payload(input_payload)
        
        event = EventLog(
            engine_name=engine_name,
            engine_version=engine_version,
            input_hash=input_hash,
            output_blob=output_blob,
            confidence_score=confidence,
            outcome_label=label
        )
        
        self.db.add(event)
        await self.db.commit()
        logger.debug(f"Event Logged: [{engine_name}_{engine_version}] (Hash: {input_hash[:8]})")
