import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.hawkeye.vision_engine import VisionEngine
from backend.services.hawkeye.copy_engine import CopyEngine
from backend.services.hawkeye.funnel_engine import FunnelEngine
from backend.services.hawkeye.fatigue_engine import FatigueEngine
from backend.services.hawkeye.embedding_engine import EmbeddingEngine
from backend.services.hawkeye.creative_registry import CreativeRegistry

logger = logging.getLogger(__name__)

class HawkeyeEngine:
    """
    Orchestrates the Solid Matter transformation. Maps unstructured pixels, words, 
    and landing pages into strict, mathematically encoded JSON signals meant for automated ingestion.
    """

    def __init__(self, db_session: AsyncSession):
         self.db = db_session
         self.vision = VisionEngine()
         self.copy = CopyEngine()
         self.funnel = FunnelEngine()
         self.fatigue = FatigueEngine()
         self.embedding = EmbeddingEngine()
         self.registry = CreativeRegistry(db_session)

    async def analyze_creative(self, 
                               company_id: str, 
                               campaign_id: str, 
                               creative_id: str, 
                               asset_url: str, 
                               landing_page_url: str, 
                               primary_text: str, 
                               headline: str, 
                               historical_ctr: List[float] = [], 
                               historical_spend: float = 0.0) -> Dict[str, Any]:
        """
        Runs the full 5-stage inference pipeline generating the definitive Hawkeye signal array.
        """
        logger.info(f"Hawkeye processing full analysis vector for {creative_id}")
        
        is_video = True if "mp4" in asset_url or "mov" in asset_url else False
        
        # --- Stage 1 & 2 & 3: Parallel Logic Inference Streams ---
        vision_metrics = self.vision.analyze_asset(asset_url, is_video).model_dump()
        copy_metrics = self.copy.analyze_copy(primary_text, headline).model_dump()
        funnel_metrics = self.funnel.extract_funnel_health(landing_page_url).model_dump()
        
        blobs = {
             "url": asset_url,
             "vision": vision_metrics,
             "copy": copy_metrics,
             "funnel": funnel_metrics
        }
        
        # --- Stage 4 & 5: Synthesize and Vectorize ---
        # Produce structural semantic hash for duplicating detection
        creative_vector = self.embedding.generate_embedding(blobs)
        
        # Calculate visual similarity against historical failures securely
        historical_vecs = await self.registry.get_historical_embeddings(company_id)
        similarity = self.embedding.check_similarity(creative_vector, historical_vecs)
        
        fatigue_data = self.fatigue.calculate_lifecycle_fatigue(historical_ctr, historical_spend, similarity)
        
        # --- Data Abstraction & Database Logging ---
        embedding_ref_id = f"vec_{creative_id}" # Normally sent dynamically to Qdrant Index array
        
        await self.registry.log_creative(company_id, campaign_id, creative_id, blobs, embedding_ref_id, fatigue_data)
        
        # --- Standardized Output Mapping logic for CaptainDiagnose ingestion ---
        # Hook strength mathematically maps composition + pacing + textual emotion logic
        hook = (vision_metrics.get("composition_score", 0.0) * 0.4) + (0.3 if vision_metrics.get("hook_detected_in_3s") else 0) + (copy_metrics.get("benefit_framing_score", 0.0) * 0.3)
        hook_strength = min(1.0, max(0.0, hook))
        
        output_schema = {
          "creative_id": creative_id,
          "hook_strength": round(hook_strength, 2),
          "emotional_tone": copy_metrics.get("primary_emotion", "neutral"),
          "offer_clarity_score": max(0.0, 1.0 - funnel_metrics.get("funnel_gap_score", 0.5)),
          "cta_intensity_score": 0.8 if copy_metrics.get("urgency_detected") else 0.4,
          "visual_complexity_score": vision_metrics.get("visual_clutter", 0.5),
          "fatigue_score": fatigue_data.get("fatigue_score", 0.0),
          "creative_cluster": f"{copy_metrics.get('primary_emotion')}_{copy_metrics.get('offer_extracted')}",
          "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mocks saving outputs reliably to Event Logs (AtlasMemory interaction points happens via APIs)
        logger.info(f"Hawkeye Output generated safely for {creative_id} (Hook: {hook_strength})")
        
        return output_schema
