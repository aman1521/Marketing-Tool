from typing import Dict, Any

class CampaignClassifier:
    """
    LAYER 2: Campaign-Level Classification
    Evaluates computed deviation scores deterministically to assign states.
    """
    
    # Valid States Defined by Architecture
    VALID_STATES = [
        "TRAFFIC_PROBLEM",
        "CONVERSION_PROBLEM",
        "CREATIVE_FATIGUE",
        "SCALING_OPPORTUNITY",
        "TRACKING_ISSUE",
        "BUDGET_INEFFICIENCY",
        "STABLE"
    ]

    def classify_campaign(self, campaign_id: str, deviations: Dict[str, float]) -> Dict[str, Any]:
        """
        Takes output from SignalAggregator and assigns exactly one dominant state.
        Rules are hardcoded, versionable, and deterministic. No LLM logic.
        """
        
        ctr_deviation = deviations.get("ctr_deviation_score", 0)
        conversion_gap = deviations.get("conversion_gap_score", 0)
        fatigue_index = deviations.get("fatigue_index", 0)
        scaling_readiness = deviations.get("scaling_readiness_score", 0)
        anomaly_score = deviations.get("anomaly_score", 0)
        roas_deviation = deviations.get("roas_deviation_score", 0)
        
        # Rule Evaluation Pipeline (Order designates priority of diagnosis)
        
        state = "STABLE"
        strength = 0.5
        
        if anomaly_score > 0.8:
            state = "TRACKING_ISSUE"
            strength = anomaly_score
            
        elif fatigue_index > 0.7:
            state = "CREATIVE_FATIGUE"
            strength = fatigue_index
            
        elif scaling_readiness > 0.65 and roas_deviation > 0.2:
            state = "SCALING_OPPORTUNITY"
            strength = scaling_readiness
            
        elif ctr_deviation < -0.3:
            # CTR is drastically below P50
            state = "TRAFFIC_PROBLEM"
            strength = min(abs(ctr_deviation), 1.0)
            
        elif ctr_deviation >= 0 and conversion_gap > 0.4:
            # People click, but ROAS is severely lagging
            state = "CONVERSION_PROBLEM"
            strength = min(conversion_gap, 1.0)
            
        elif roas_deviation < -0.4:
            # Broad spectrum inefficiency
            state = "BUDGET_INEFFICIENCY"
            strength = min(abs(roas_deviation), 1.0)
            
        return {
            "campaign_id": campaign_id,
            "campaign_state": state,
            "state_strength": round(strength, 3),
            "key_signals": deviations
        }
