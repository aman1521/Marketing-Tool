from typing import Dict, Any, List

class AccountAggregator:
    """
    LAYER 3: Account-Level Aggregation
    Rolls up campaign states into a unified account diagnosis utilizing spend and revenue weighting.
    """

    def aggregate_account_state(self, campaign_classifications: List[Dict[str, Any]], campaign_metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Determines the total macro-state of the ad account.
        campaign_metrics should map campaign_id -> {"revenue": X, "spend": Y}
        """
        
        if not campaign_classifications:
            return {
                "account_state": "NO_DATA",
                "dominant_campaign_state": "NONE",
                "stability_index": 0.0,
                "risk_level": "UNKNOWN"
            }
            
        total_revenue = sum(metrics.get("revenue", 0) for metrics in campaign_metrics.values())
        total_spend = sum(metrics.get("spend", 0) for metrics in campaign_metrics.values())
        
        # Fallback to prevent Div by Zero
        total_revenue = total_revenue if total_revenue > 0 else 1.0
        total_spend = total_spend if total_spend > 0 else 1.0
        
        state_revenue_weight = {}
        state_spend_weight = {}
        
        # Accumulate weights
        for c_class in campaign_classifications:
            c_id = c_class["campaign_id"]
            state = c_class["campaign_state"]
            
            rev = campaign_metrics.get(c_id, {}).get("revenue", 0)
            spend = campaign_metrics.get(c_id, {}).get("spend", 0)
            
            state_revenue_weight[state] = state_revenue_weight.get(state, 0) + (rev / total_revenue)
            state_spend_weight[state] = state_spend_weight.get(state, 0) + (spend / total_spend)

        # Macro Logic
        account_state = "MIXED_VOLATILE"
        risk_level = "MODERATE"
        stability_index = state_spend_weight.get("STABLE", 0.0) + state_spend_weight.get("SCALING_OPPORTUNITY", 0.0)

        # 1. Determine dominant state logically
        for state, weight in state_revenue_weight.items():
            if state == "CONVERSION_PROBLEM" and weight >= 0.6:
                account_state = "CONVERSION_PROBLEM"
                risk_level = "HIGH"
                break
            elif state == "SCALING_OPPORTUNITY" and weight >= 0.5:
                # E.g. 50% of the revenue is coming from scalable arrays
                account_state = "SCALING_OPPORTUNITY"
                risk_level = "LOW"
                break
            elif state == "TRACKING_ISSUE" and state_spend_weight.get("TRACKING_ISSUE", 0) >= 0.4:
                account_state = "CRITICAL_TRACKING_FAILURE"
                risk_level = "CRITICAL"
                break
                
        # 2. Assign Dominant state merely by highest frequency (unweighted fallback)
        dominant_campaign_state = max(set(c["campaign_state"] for c in campaign_classifications), key=lambda s: sum(1 for c in campaign_classifications if c["campaign_state"] == s))
        
        if account_state == "MIXED_VOLATILE" and stability_index < 0.3:
            risk_level = "HIGH"

        return {
            "account_state": account_state,
            "dominant_campaign_state": dominant_campaign_state,
            "stability_index": round(stability_index, 3),
            "risk_level": risk_level,
            "revenue_weights": state_revenue_weight,
            "spend_weights": state_spend_weight
        }
