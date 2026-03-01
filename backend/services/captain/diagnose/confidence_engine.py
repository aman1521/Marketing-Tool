from typing import Dict, Any, List

class ConfidenceEngine:
    """
    LAYER 4: Confidence Scoring Engine
    Grades the reliability of the deterministic diagnosis based on signal completeness, 
    volatility, and benchmark alignment.
    """
    
    def calculate_confidence(self, campaign_classifications: List[Dict[str, Any]], account_aggregation: Dict[str, Any]) -> float:
        """
        Confidence formula mapping array consistency versus volatility inverses.
        Output range: 0.0 - 1.0
        """
        
        if not campaign_classifications:
            return 0.0
            
        # 1. Signal Consistency 
        # (Are all campaigns reading the same state, or are they scattered?)
        total_campaigns = len(campaign_classifications)
        dominant_state = account_aggregation.get("dominant_campaign_state")
        matching = sum(1 for c in campaign_classifications if c["campaign_state"] == dominant_state)
        
        signal_consistency = matching / total_campaigns
        
        # 2. Volatility Inverse
        # (High volatility mathematically drops the system's confidence in making aggressive calls)
        avg_volatility = sum(c["key_signals"].get("volatility_index", 0) for c in campaign_classifications) / total_campaigns
        volatility_inverse = max(0.0, 1.0 - avg_volatility)
        
        # 3. Benchmark Alignment
        # (Pseudo logic representing how close we are to standard industry behavior profiles)
        benchmark_alignment = 0.8  # Assume strong alignment if benchmark data successfully mapped
        
        # Weighted Final Calculation
        weight_signal = 0.4
        weight_benchmark = 0.3
        weight_vol = 0.3
        
        confidence = (signal_consistency * weight_signal) + \
                     (benchmark_alignment * weight_benchmark) + \
                     (volatility_inverse * weight_vol)
                     
        return round(min(1.0, max(0.0, confidence)), 3)
