import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Tracks divergence loops mathematically. 
    Does Captain Strategy's expectation match 24h reality?
    """

    def evaluate_model_drift(self, expected_delta: float, real_delta: float, recent_classifications: List[str]) -> Dict[str, Any]:
        """
        Determines the variance vector producing `DRIFT_WARNING` events.
        """
        variance = abs(expected_delta - real_delta)
        
        # Determine classification stability (e.g., oscillating from SCALING to COLLAPSE daily)
        unique_classes = len(set(recent_classifications))
        is_unstable = True if unique_classes >= 3 and len(recent_classifications) == 3 else False
        
        drift_active = False
        if variance > 0.3 or is_unstable:
            drift_active = True
            logger.warning(f"DRIFT_WARNING: Variance [{round(variance,2)}] detected. Classes alternating {unique_classes} times.")
            
        # Confidence score decay happens naturally via Pulse, but Sentinel monitors the severity independently
        return {
            "drift_active": drift_active,
            "variance_delta": round(variance, 3),
            "classification_oscillation": is_unstable,
        }
