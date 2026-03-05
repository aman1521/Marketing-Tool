import logging
from typing import Dict, Any, List
import statistics

logger = logging.getLogger(__name__)

class VolatilityEngine:
    """
    Detects macro chaotic structural deviations like auction CPC spikes,
    tracking system disconnections, or systemic CPA destructions.
    """

    def calculate_volatility(self, cpm_history: List[float], cpa_history: List[float]) -> Dict[str, Any]:
        """
        Uses mathematical variance & standard deviations to score system instability.
        High instability mathematically forces Confidence calculations down.
        """
        logger.info("Pulse tracking system-wide Auction Volatility...")
        
        if len(cpm_history) < 3 or len(cpa_history) < 3:
             return {"volatility_index": 0.1, "turbulence_flag": False}
             
        # CV = Standard Deviation / Mean (Coefficient of Variation)
        cpm_mean = statistics.mean(cpm_history)
        cpm_std = statistics.stdev(cpm_history) if len(cpm_history) > 1 else 0
        cpm_cv = (cpm_std / cpm_mean) if cpm_mean > 0 else 0
        
        cpa_mean = statistics.mean(cpa_history)
        cpa_std = statistics.stdev(cpa_history) if len(cpa_history) > 1 else 0
        cpa_cv = (cpa_std / cpa_mean) if cpa_mean > 0 else 0
        
        # Combine variance metrics 
        # A CV > 0.3 generally indicates severe structural turbulence in ad auctions
        combined_cv = (cpm_cv * 0.4) + (cpa_cv * 0.6)
        
        idx = min(1.0, (combined_cv / 0.5)) # Map 0.5 CV -> 1.0 Max Volatility
        
        turbulence = True if idx > 0.65 else False
        
        if turbulence:
             logger.warning(f"SEVERE VOLATILITY DETECTED. Market turbulence mapped at {round(idx, 2)} Index.")
             
        return {
             "volatility_index": round(idx, 3),
             "turbulence_flag": turbulence
        }
