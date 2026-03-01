from typing import List, Dict
from backend.services.atlas.models import RawMetrics

def calculate_fatigue_signals(metrics: List[RawMetrics]) -> Dict[str, float]:
    """
    Evaluates audience saturation and creative decay over time.
    """
    total_imps = sum(m.impressions for m in metrics)
    total_spend = sum(m.spend for m in metrics)
    
    # Mock fatigue logic
    frequency_growth = 0.8 if total_imps > 10000 else 0.2
    decay_rate = 0.05
    
    # High frequency + spending implies burn
    score = min(1.0, (frequency_growth * 0.6) + (total_spend / 1000 * 0.4))
    
    return {
        "frequency_growth_rate": frequency_growth,
        "engagement_decay_rate": decay_rate,
        "fatigue_score": round(score, 3)
    }
