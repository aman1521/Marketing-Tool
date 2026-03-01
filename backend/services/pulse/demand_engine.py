import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DemandEngine:
    """
    Analyzes broad macro demand drops independent of core creative failures.
    Detects when entire networks or categories collapse in conversion propensity.
    """

    def calculate_demand_shift(self, baseline_conversions: float, recent_conversions: float, search_trend_proxy: float = 0.0) -> Dict[str, Any]:
        """
        Derives shift directions from -1.0 to 1.0. Positive means surging demand globally.
        """
        logger.info("Pulse analyzing systemic consumer demand shifts...")
        
        if baseline_conversions <= 0:
             return {"demand_shift_score": 0.0, "demand_direction": "stable"}
             
        # Example conversion volume drop globally:
        # dropped from 100/day to 50/day = -50% shift
        delta = (recent_conversions - baseline_conversions) / baseline_conversions
        
        # Merge with macro proxy (E.g. "Google Trends" if API configured, or platform-wide impressions drops)
        total_shift = (delta * 0.7) + (search_trend_proxy * 0.3)
        
        bounded_score = min(1.0, max(-1.0, total_shift))
        
        if bounded_score < -0.2:
             direction = "down"
             logger.warning(f"Macro Demand contraction detected: Score [{round(bounded_score, 2)}]")
        elif bounded_score > 0.3:
             direction = "up"
        else:
             direction = "stable"
             
        return {
             "demand_shift_score": round(bounded_score, 3),
             "demand_direction": direction
        }
