from typing import List, Dict
from backend.services.atlas.models import RawMetrics

def calculate_scaling_signals(metrics: List[RawMetrics], current_roas: float) -> Dict[str, float]:
    """
    Determines if a campaign presents stable foundations for budget multipliers.
    """
    total_spend = sum(m.spend for m in metrics)
    
    # Mocking scaling signals
    efficiency_ratio = current_roas / 2.0  # Base logic target ratio
    volatility = 0.15 # 15% variance day by day mock
    
    confidence = efficiency_ratio * (1 - volatility)
    confidence = max(0.0, min(1.0, confidence))
    
    return {
        "budget_efficiency_ratio": round(efficiency_ratio, 3),
        "volatility_index": volatility,
        "scaling_confidence_score": round(confidence, 3)
    }
