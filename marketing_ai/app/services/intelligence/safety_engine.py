from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SafetyEngine:
    """
    Core Automation Filter - AI NEVER directly executes.
    Passes through Rule Engine to classify if manual intervention is needed.
    """
    
    @staticmethod
    def validate_ai_action(action: Dict[str, Any]) -> Tuple[str, str]:
        """
        Takes raw json output from Orchestrator strategies.
        Returns: Tuple of (status_code, reason_string)
        Status codes: 'approved', 'rejected', 'requires_manual_review'
        """
        action_type = action.get("type", "unknown")
        confidence_score = action.get("confidence_score", 0.0)
        value = action.get("value", 0.0)

        # 1. Hard Rule: Absolute Confidence Thresholds
        if confidence_score < 0.75:
            return "rejected", f"Confidence score {confidence_score} strictly below 0.75 limit."

        # 2. Hard Rule: Budget Modifications
        if action_type == "budget_increase":
            if value > 0.30: # Cannot scale more than 30% without human confirmation
                return "requires_manual_review", f"Budget change {value*100}% exceeds 30% auto-increase limit."
            elif value < 0:
                return "rejected", "Budget increase value cannot be negative."

        elif action_type == "budget_decrease":
             if value > 0.50: # Dropping budget by more than 50% usually signals emergency, defer to owner
                return "requires_manual_review", f"Budget decrease {value*100}% exceeds 50% auto-cut limit."

        # 3. Hard Rule: Strategic Changes 
        elif action_type == "audience_targeting_shift":
            return "requires_manual_review", "Audience shifts strictly require manual review."
            
        elif action_type == "campaign_pause":
             return "approved", "Pausing underperforming campaigns automatically approved."
             
        elif action_type == "unknown":
            return "rejected", "Unrecognized execution payload type."

        # If it passes all safety checks
        return "approved", "Sufficient safety thresholds met for autonomic execution."
