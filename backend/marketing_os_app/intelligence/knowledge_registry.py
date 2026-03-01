import logging
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.marketing_os_app.advanced_models import StrategyArchetypeRecord

logger = logging.getLogger(__name__)

class KnowledgeRegistry:
    """
    Persists and retrieves historical strategy execution patterns.
    Converts raw outcomes into reusable intelligence archetypes.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_outcome(self, outcome: Dict[str, Any]):
        """
        Called after each execution cycle to record the result pattern.
        outcome keys: industry, strategy_type, aov_tier, creative_archetype,
                      scaling_band, lift_pct, risk_exposure, volatility_context
        """
        # Check if pattern exists
        q = select(StrategyArchetypeRecord).where(
            StrategyArchetypeRecord.industry == outcome["industry"],
            StrategyArchetypeRecord.strategy_type == outcome["strategy_type"],
            StrategyArchetypeRecord.creative_archetype == outcome["creative_archetype"],
            StrategyArchetypeRecord.scaling_band == outcome["scaling_band"]
        )
        res = await self.db.execute(q)
        existing = res.scalar_one_or_none()

        if existing:
            # Running average update
            n = existing.sample_count
            existing.avg_lift_pct = (existing.avg_lift_pct * n + outcome["lift_pct"]) / (n + 1)
            existing.avg_risk_exposure = (existing.avg_risk_exposure * n + outcome["risk_exposure"]) / (n + 1)
            existing.sample_count = n + 1
            existing.confidence_score = min(1.0, existing.confidence_score + (0.01 * min(n, 20)))
        else:
            record = StrategyArchetypeRecord(
                pattern_id=f"arch_{uuid.uuid4().hex[:8]}",
                industry=outcome["industry"],
                strategy_type=outcome["strategy_type"],
                aov_tier=outcome["aov_tier"],
                creative_archetype=outcome["creative_archetype"],
                scaling_band=outcome["scaling_band"],
                avg_lift_pct=outcome["lift_pct"],
                avg_risk_exposure=outcome["risk_exposure"],
                volatility_context=outcome["volatility_context"],
                confidence_score=0.4,
                sample_count=1
            )
            self.db.add(record)

        await self.db.commit()
        logger.info(f"Knowledge ingested: {outcome['strategy_type']} | {outcome['industry']}")

    async def get_high_confidence_archetypes(self, min_confidence: float = 0.7) -> List[Dict]:
        q = select(StrategyArchetypeRecord).where(
            StrategyArchetypeRecord.confidence_score >= min_confidence
        ).order_by(StrategyArchetypeRecord.avg_lift_pct.desc())

        res = await self.db.execute(q)
        rows = res.scalars().all()
        return [{
            "pattern_id": r.pattern_id,
            "industry": r.industry,
            "strategy_type": r.strategy_type,
            "avg_lift_pct": r.avg_lift_pct,
            "confidence_score": r.confidence_score,
            "sample_count": r.sample_count
        } for r in rows]
