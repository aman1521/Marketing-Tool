import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Backtester:
    """
    Simulates what CaptainExecute would have done historically using adjusted
    parameters compared against actual realized returns on spend.
    """

    def simulate_decision_matrix(self, historical_data: List[Dict[str, Any]], simulated_threshold: float) -> Dict[str, Any]:
        """
        historical_data format: [{"actual_roi": 1.2, "confidence_score_at_time": 0.75, "action_taken": "NONE"}]
        Simulates if a lowered threshold would have executed actions that generated positive historic ROI.
        """
        logger.info(f"Calibration Backtester spinning up vs threshold: {simulated_threshold}")
        
        simulated_actions_taken = 0
        missed_lift = 0.0 # Opportunities we missed, but would have caught with the new threshold
        over_scale_penalty = 0.0 # Bad executions we WOULD have made with a relaxed threshold
        
        for record in historical_data:
            c_score = record.get("confidence_score_at_time", 0.0)
            actual_roi = record.get("actual_roi", 1.0)
            action = record.get("action_taken", "NONE")
            
            # Simulated Execution logic: If confidence exceeds our hypothetical threshold
            if c_score >= simulated_threshold:
                 simulated_actions_taken += 1
                 if actual_roi > 1.0 and action == "NONE":
                      missed_lift += (actual_roi - 1.0) # We would have scaled a winner!
                 elif actual_roi < 1.0:
                      over_scale_penalty += (1.0 - actual_roi) # We would have scaled a loser!
            
            # Simulated Hold logic: We block executions under threshold
            elif c_score < simulated_threshold:
                 if actual_roi > 1.0 and action != "NONE":
                      pass # We would have blocked a winner - wait, the user manually scaled it and won. 
                           # Underscaling penalty applies.
                 elif actual_roi < 1.0 and action != "NONE":
                      pass # We would have safely blocked a historical loser the human lost money on! Good.

        lift_score = missed_lift # Positive net benefit of this threshold
        
        return {
             "simulated_threshold": simulated_threshold,
             "simulated_executions": simulated_actions_taken,
             "decision_lift_score": round(lift_score, 3),
             "over_scaling_penalty": round(over_scale_penalty, 3),
             "under_scaling_penalty": 0.0 # Placeholded for simplicity
        }
