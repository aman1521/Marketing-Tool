import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.services.atlas.models import EngineeredFeatures

logger = logging.getLogger(__name__)

class FeatureStore:
    """
    Interfaces with the backend database serving exactly as a low-latency "online"
    and high-latency "offline" Feature Store for downstream ML models.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_latest_features(self, campaign_id: str) -> Dict[str, Any]:
        """Online Store Simulation: Pull the most recent feature packet."""
        logger.info(f"Retrieving online features for {campaign_id}")
        query = select(EngineeredFeatures).where(EngineeredFeatures.campaign_id == campaign_id).order_by(EngineeredFeatures.calculated_at.desc()).limit(1)
        
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()
        
        if record:
            return record.feature_blob
        return {}

    async def get_historical_features(self, campaign_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Offline Store Simulation: Pull training sequences."""
        query = select(EngineeredFeatures).where(EngineeredFeatures.campaign_id == campaign_id).order_by(EngineeredFeatures.calculated_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return [r.feature_blob for r in records]
