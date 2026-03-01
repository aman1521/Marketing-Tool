from typing import Dict, Any, List

class SignalAggregator:
    """
    LAYER 1: Signal Aggregation
    Pulls raw feature arrays from AtlasSignals, baseline percentiles from AtlasBenchmarks, 
    and business context from GenesisProfile to compute deterministic deviation scores.
    """
    
    def __init__(self):
        # Dependencies would normally be injected here (DB Sessions, API clients)
        pass

    def compute_campaign_deviations(self, campaign_features: Dict[str, Any], benchmark_data: Dict[str, Any], genesis_context: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute standard deviation scores relative to the industry benchmark.
        Positive deviation means over-performing relative to benchmark. 
        Negative deviation means under-performing.
        """
        
        # Safe extraction
        current_roas = campaign_features.get("roas_1d", 0.0)
        current_ctr = campaign_features.get("ctr", 0.01) # Assuming generic safe default
        fatigue_score = campaign_features.get("fatigue_score", 0.0)
        scaling_confidence = campaign_features.get("scaling_confidence_score", 0.0)
        volatility_index = campaign_features.get("volatility_index", 0.0)
        anomaly_score = campaign_features.get("anomaly_score", 0.0)
        
        # Benchmark extraction (Assuming P50 is the 'baseline' to beat)
        roas_p50 = benchmark_data.get("roas_1d", {}).get("percentile_50", 1.0)
        ctr_p50 = benchmark_data.get("ctr", {}).get("percentile_50", 0.015)
        
        # Deviation calculations
        roas_deviation = (current_roas - roas_p50) / roas_p50 if roas_p50 > 0 else 0.0
        ctr_deviation = (current_ctr - ctr_p50) / ctr_p50 if ctr_p50 > 0 else 0.0
        
        # Mocking a conversion gap based on internal logic. 
        # (e.g. Traffic is high and cheap, but revenue is missing = high gap)
        conversion_gap_score = -roas_deviation if ctr_deviation > 0 else 0.0 
        
        return {
            "roas_deviation_score": round(roas_deviation, 3),
            "ctr_deviation_score": round(ctr_deviation, 3),
            "conversion_gap_score": round(conversion_gap_score, 3),
            "fatigue_index": fatigue_score,
            "scaling_readiness_score": scaling_confidence,
            "volatility_index": volatility_index,
            "anomaly_score": anomaly_score
        }
