import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.atlas.models import EngineeredFeatures, RawMetrics

from backend.services.atlas.signals.fatigue_model import calculate_fatigue_signals
from backend.services.atlas.signals.scaling_model import calculate_scaling_signals
from backend.services.atlas.signals.risk_model import calculate_risk_signals

logger = logging.getLogger(__name__)

class AtlasFeatureEngine:
    """
    Central pipeline converting RawMetrics into engineered performance, 
    fatigue, scaling, and risk features.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.feature_version = "v1.0"

    def compute_performance_features(self, metrics: List[RawMetrics]) -> Dict[str, float]:
        """Calculate deterministic performance heuristics."""
        total_spend = sum(m.spend for m in metrics)
        total_revenue = sum(m.revenue for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        
        roas_1d = total_revenue / total_spend if total_spend > 0 else 0
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        
        # Simplistic trends - in prod uses rolling arrays
        return {
            "roas_1d": round(roas_1d, 3),
            "roas_7d": round(roas_1d * 1.05, 3), # Mock
            "roas_trend_slope": 0.05,
            "cpa_velocity": 1.2,
            "ctr_trend_slope": -0.01,
            "spend_acceleration": 15.5
        }

    async def generate_features(self, company_id: str, campaign_id: str, recent_metrics: List[RawMetrics]):
        """Runs the whole signal processing suite and maps output to Feature Store."""
        logger.info(f"Generating features for {campaign_id}")
        
        perf_features = self.compute_performance_features(recent_metrics)
        fatigue_features = calculate_fatigue_signals(recent_metrics)
        scaling_features = calculate_scaling_signals(recent_metrics, perf_features["roas_1d"])
        risk_features = calculate_risk_signals(recent_metrics)
        
        # Merge all dictionaries
        engineered_blob = {
            **perf_features,
            **fatigue_features,
            **scaling_features,
            **risk_features,
        }
        
        # Persist
        feature_record = EngineeredFeatures(
            company_id=company_id,
            campaign_id=campaign_id,
            feature_version=self.feature_version,
            feature_blob=engineered_blob,
            calculated_at=datetime.utcnow()
        )
        
        self.db.add(feature_record)
        await self.db.commit()
        logger.info(f"Successfully recorded Engineered Features for {campaign_id}")
        return engineered_blob
