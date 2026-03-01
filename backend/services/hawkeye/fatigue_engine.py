import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from backend.services.hawkeye.models import FatigueStage

logger = logging.getLogger(__name__)

class FatigueEngine:
    """
    Connects AtlasSignals time-series logic to physical Ad Creative definitions,
    detecting mathematically when audiences exhaust visual compositions.
    """

    def calculate_lifecycle_fatigue(self, 
                                    historical_ctr_data: list, 
                                    historical_spend: float, 
                                    visual_similarity_score: float) -> Dict[str, Any]:
        """
        Synthesizes visual redundancy and CTR decays to calculate exact scaling risk.
        Requires AtlasSignals to calculate accurately.
        """
        logger.info("Hawkeye isolating cross-media fatigue calculations.")
        
        if not historical_ctr_data:
             return {"fatigue_score": 0.0, "stage": FatigueStage.FRESH}
             
        # Mock decay logic: Is the latest CTR significantly worse than the peak?
        peak_ctr = max(historical_ctr_data) if historical_ctr_data else 0.0
        current_ctr = historical_ctr_data[-1] if historical_ctr_data else 0.0
        
        ctr_decay = ((peak_ctr - current_ctr) / peak_ctr) if peak_ctr > 0 else 0.0
        
        # Penalize if visually similar to previous dead ads
        fatigue_penalty = visual_similarity_score * 0.3
        
        # Total fatigue (0.0 means perfect, 1.0 means dead)
        total_fatigue = min(1.0, max(0.0, ctr_decay + fatigue_penalty))
        
        stage = FatigueStage.FRESH
        if total_fatigue > 0.8:
            stage = FatigueStage.DEAD
        elif total_fatigue > 0.6:
            stage = FatigueStage.FATIGUED
        elif total_fatigue > 0.35:
            stage = FatigueStage.SATURATED
        elif historical_spend > 500:
            stage = FatigueStage.SCALING

        return {
            "fatigue_score": round(total_fatigue, 3),
            "stage": stage
        }
