import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.atlas.models import BenchmarkSnapshots, EngineeredFeatures, RawMetrics

logger = logging.getLogger(__name__)

class AtlasBenchmarkEngine:
    """
    Computes aggregated anonymous percentiles across the whole datalake to form industry baselines.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def compute_industry_snapshot(self, records: List[EngineeredFeatures], industry: str, aov: str):
        """
        Aggregate anonymized ROAS, CPA, and CTR metrics across similar business structures.
        """
        logger.info(f"Computing Benchmark Snapshot for {industry} / {aov}")
        
        # In a real environment, we use numpy/scipy or native Postgres Percentile capabilities
        # For mock deterministic architecture:
        roas_list = [r.feature_blob.get("roas_1d", 0) for r in records if "roas_1d" in r.feature_blob]
        
        if not roas_list:
            logger.warning(f"No ROAS records found for benchmarking {industry}.")
            return

        sorted_roas = sorted(roas_list)
        n = len(sorted_roas)
        
        p25 = sorted_roas[int(n*0.25)] if n > 0 else 0
        p50 = sorted_roas[int(n*0.50)] if n > 0 else 0
        p75 = sorted_roas[int(n*0.75)] if n > 0 else 0
        
        snapshot = BenchmarkSnapshots(
            industry=industry,
            aov_range=aov,
            metric_name="roas_1d",
            percentile_25=round(p25, 2),
            percentile_50=round(p50, 2),
            percentile_75=round(p75, 2)
        )
        self.db.add(snapshot)
        await self.db.commit()
        logger.info(f"Successfully recorded Benchmark Snapshot for Industry {industry}")
