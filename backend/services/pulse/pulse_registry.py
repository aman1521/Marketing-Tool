import logging
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.services.pulse.models import PulseRegistryModel

logger = logging.getLogger(__name__)

class PulseRegistry:
    """
    Maintains historical array of Macro factors preventing identical intensive queries
    running every CaptainDiagnose orchestration. Modifies System Cache.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def retrieve_active_pulse(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch latest modifiers injected straight into CaptainDiagnose Logic constraints.
        """
        query = select(PulseRegistryModel).where(PulseRegistryModel.company_id == company_id).order_by(PulseRegistryModel.created_at.desc()).limit(1)
        res = await self.db.execute(query)
        record = res.scalar_one_or_none()
        
        if not record:
             return None
             
        return {
             "seasonality_index": record.seasonality_index,
             "demand_shift_score": record.demand_shift_score,
             "volatility_index": record.volatility_index,
             "macro_drift_score": record.macro_drift_score,
             "market_phase": record.market_phase,
             "confidence_modifier": record.confidence_modifier
        }

    async def log_pulse_iteration(self, company_id: str, pulse_blob: Dict[str, Any]) -> PulseRegistryModel:
        """Saves output of the Gravity calculation sequentially into memory blocks."""
        record = PulseRegistryModel(
            company_id=company_id,
            seasonality_index=pulse_blob.get("seasonality_index", 0.5),
            demand_shift_score=pulse_blob.get("demand_shift_score", 0.0),
            volatility_index=pulse_blob.get("volatility_index", 0.0),
            macro_drift_score=pulse_blob.get("macro_drift_score", 0.0),
            market_phase=pulse_blob.get("market_phase", "stable_growth"),
            confidence_modifier=pulse_blob.get("confidence_modifier", 1.0),
            pulse_blob=pulse_blob,
            created_at=datetime.utcnow()
        )
        self.db.add(record)
        await self.db.commit()
        return record
