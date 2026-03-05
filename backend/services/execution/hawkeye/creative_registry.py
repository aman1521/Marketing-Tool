import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.services.execution.hawkeye.models import CreativeRegistryModel, CreativeType, FatigueStage

logger = logging.getLogger(__name__)

class CreativeRegistry:
    """
    Persistent SQLAlchemy Database store managing the structured intelligence blobs.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def _safe_query(self, query):
        res = await self.db.execute(query)
        return res

    async def log_creative(self, 
                           company_id: str, 
                           campaign_id: str, 
                           creative_id: str, 
                           blobs: Dict[str, Any], 
                           embedding_ref: str, 
                           fatigue_data: Dict[str, Any]) -> CreativeRegistryModel:
        """Saves or Updates the Creative blob securely."""
        
        query = select(CreativeRegistryModel).where(CreativeRegistryModel.creative_id == creative_id)
        existing = await self._safe_query(query)
        record = existing.scalar_one_or_none()

        if record:
             logger.info(f"Hawkeye updating existing creative {creative_id}")
             record.fatigue_stage = fatigue_data.get("stage", FatigueStage.FRESH)
             record.fatigue_score = fatigue_data.get("fatigue_score", 0.0)
             record.hawkeye_blob = blobs
        else:
             logger.info(f"Hawkeye inserting newly analyzed creative {creative_id}")
             
             record = CreativeRegistryModel(
                 creative_id=creative_id,
                 company_id=company_id,
                 campaign_id=campaign_id,
                 creative_type=CreativeType.VIDEO if "video" in blobs.get("url", "") else CreativeType.IMAGE,
                 hook_type=blobs.get("copy", {}).get("primary_emotion", "unknown"),
                 emotional_tone=blobs.get("copy", {}).get("primary_emotion", "neutral"),
                 offer_type=blobs.get("copy", {}).get("offer_extracted", "Standard"),
                 embedding_reference=embedding_ref,
                 fatigue_stage=fatigue_data.get("stage", FatigueStage.FRESH),
                 fatigue_score=fatigue_data.get("fatigue_score", 0.0),
                 hawkeye_blob=blobs
             )
             self.db.add(record)
             
        await self.db.commit()
        return record
        
    async def get_historical_embeddings(self, company_id: str) -> List[List[float]]:
        """Mock method for embedding abstraction. Usually executed from Qdrant natively."""
        return [[0.1]*16, [0.5]*16] # Mock format 16-dims
