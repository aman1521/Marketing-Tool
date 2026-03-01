import logging
from typing import Dict, Any, List
import statistics

logger = logging.getLogger(__name__)

class SeasonalityEngine:
    """
    Calculates intrinsic cyclical business phases deterministically extracting 
    patterns out of aggregate revenue metrics across rolling historical bounds.
    """

    def calculate_seasonality(self, historical_revenue_daily: List[float], current_revenue_velocity: float) -> Dict[str, Any]:
        """
        Calculates baseline seasonality mappings mapping the trailing 30 vs 90-day baselines.
        In full production, this maps into STL matrix decomposers.
        """
        logger.info("Pulse analyzing Seasonality structures...")
        
        if len(historical_revenue_daily) < 7:
             logger.warning("Insufficient historical arrays for Seasonality extraction. Defaulting to Neutral.")
             return {"seasonality_index": 0.5, "seasonal_phase": "neutral", "expected_lift_factor": 1.0}
             
        # Mock rolling average comparison
        recent_avg = statistics.mean(historical_revenue_daily[-7:]) if len(historical_revenue_daily) >= 7 else 0
        baseline_avg = statistics.mean(historical_revenue_daily)
        
        if baseline_avg == 0:
            return {"seasonality_index": 0.5, "seasonal_phase": "neutral", "expected_lift_factor": 1.0}
            
        # Calculate Delta structurally
        delta = (recent_avg - baseline_avg) / baseline_avg
        
        # Seasonality Index mapping (0.0 to 1.0) -> 0.5 is baseline.
        # Example: +40% Delta maps to ~0.70 index.
        base_index = 0.5 + (delta * 0.5)
        safe_index = min(1.0, max(0.0, base_index))
        
        phase = "neutral"
        if safe_index > 0.75:
            phase = "peak"
        elif safe_index < 0.25:
            phase = "low"
            
        return {
            "seasonality_index": round(safe_index, 3),
            "seasonal_phase": phase,
            "expected_lift_factor": round(1.0 + delta, 2)
        }
