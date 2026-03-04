"""
Outcome Predictor (Simulation Wrapper)
======================================
Decision Layer: Interfaces with the Memory ReplayEngine to simulate 
expected CPA, RoAS, and Lift for generated actions. Assigns Confidence.
"""

from typing import Dict, Any, List
# from ...memory.replay_engine import ReplayEngine # We map this logically

class OutcomePredictor:
    """
    Predicts outcomes for a proposed strategy using the ReplayEngine.
    """

    def predict(self, action: Dict[str, Any], context_snapshot: Dict[str, Any]) -> Dict[str, float]:
        """
        Takes a proposed action and the original context snapshot.
        Returns predicted lift, predicted risk, and predicted CPA delta based on the signal strength.
        """
        # In a fully integrated system, this would call ReplayEngine.run_simulation(action)
        # We will approximate the statistical prior from the context memory snapshot.
        
        mem = context_snapshot.get("operator_memory", {})
        base_lift = mem.get("predicted_lift", 0.0)
        base_risk = mem.get("predicted_risk", 0.10)
        
        # Modifier based on action type
        if action.get("action_type") == "scale_budget":
            # Scaling usually slightly compresses ROAS / increases CPA
            cpa_modifier = 0.05
            lift_modifier = base_lift * 0.9
        elif action.get("action_type") == "new_creative_angle":
            # New angles can swing wildly
            cpa_modifier = -0.15 if base_lift > 0.05 else 0.10
            lift_modifier = base_lift * 1.5
            base_risk += 0.20
        else:
            cpa_modifier = 0.0
            lift_modifier = base_lift

        predicted_cpa_delta = round(cpa_modifier, 4)
        predicted_lift      = round(lift_modifier, 4)
        predicted_risk      = round(min(1.0, base_risk), 4)
        
        # Calculate resulting System Confidence
        # Higher data count from Memory = Higher confidence.
        # High Risk Action = Lower Confidence.
        conf = mem.get("confidence", 0.5) 
        adjusted_conf = max(0.1, min(0.95, conf - (predicted_risk * 0.2)))

        return {
            "expected_cpa_delta": predicted_cpa_delta,
            "expected_ctr_delta": predicted_lift * 0.5, # rule of thumb
            "expected_roas_delta": predicted_lift,
            "confidence": round(adjusted_conf, 4),
            "risk_score": predicted_risk
        }
