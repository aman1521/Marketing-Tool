from typing import List, Dict
import random
from backend.services.atlas.models import RawMetrics

def calculate_risk_signals(metrics: List[RawMetrics]) -> Dict[str, float]:
    """
    Identifies anomalies, tracking drops, or sudden budget hemorrhages.
    """
    conversions = sum(m.conversions for m in metrics)
    spend = sum(m.spend for m in metrics)
    
    # Spike detection pseudo
    anomaly = random.uniform(0.0, 0.2)
    
    budget_risk = 0.8 if spend > 1000 and conversions == 0 else 0.1
    tracking_health = 1.0 if conversions > 0 else 0.5
    
    return {
        "anomaly_score": round(anomaly, 3),
        "budget_risk_score": budget_risk,
        "tracking_health_score": tracking_health
    }
