import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MacroDriftEngine:
    """
    Computes system-level inflation & platform delivery shifts analyzing aggregate
    anonymized account histories identifying Meta or Google specific algorithm collapses.
    """

    def evaluate_platform_drift(self, network_data: Dict[str, float]) -> Dict[str, Any]:
        """
        network_data example: { "meta_roas_delta": -0.15, "google_cpc_delta": +0.80 }
        Output maps positive/negative drifts into a final -1 to 1 multiplier block.
        """
        logger.info("Pulse tracking system-wide network Algorithm Drift patterns.")
        
        if not network_data:
             return {"macro_drift_score": 0.0, "drift_direction": "stable"}
             
        # Negative Drift = Platform destroying accounts algorithms
        # Positive Drift = Platform performing exceptionally
        
        composite = 0.0
        weights = 0
        for platform, delta in network_data.items():
            if "roas" in platform.lower():
                 composite += delta # Positive delta = positive drift
                 weights += 1
            elif "cpc" in platform.lower() or "cpm" in platform.lower():
                 composite -= delta # Positive CPC delta = negative drift 
                 weights += 1
                 
        if weights == 0:
            return {"macro_drift_score": 0.0, "drift_direction": "stable"}
            
        final_drift = composite / weights
        bounded_drift = min(1.0, max(-1.0, final_drift))
        
        if bounded_drift < -0.15:
            direction = "down"
            logger.warning(f"Major Macro algorithm crash detected on Networks. Drift [{round(bounded_drift, 2)}]")
        elif bounded_drift > 0.15:
            direction = "up"
            logger.info("Favorable Meta/Google market algorithm drift detected.")
        else:
            direction = "stable"
            
        return {
             "macro_drift_score": round(bounded_drift, 3),
             "drift_direction": direction
        }
