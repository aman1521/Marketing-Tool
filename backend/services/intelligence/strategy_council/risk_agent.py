"""
Risk Agent
==========
Focuses entirely on capital preservation and over-scaling risks.
Acts as a check on aggressive Expansion / Pivot recommendations.
"""

from typing import Dict, Any, List
from .models import AgentInsight, AgentRole, ActionProposal

class RiskAgent:
    
    def analyze(self, context: Dict[str, Any]) -> AgentInsight:
        observations = []
        actions = []
        
        flags = context.get("critical_flags", {})
        dir_signals = context.get("directional_signals", {})
        
        # 1. Action Check
        op_action = dir_signals.get("operator_action")
        confidence = context.get("confidence_score", 0)

        # High risk threshold logic: if operator memory says AVOID, block new scaling.
        if op_action == "AVOID" or (op_action == "MONITOR" and confidence < 0.35):
             observations.append(f"Memory risk extremely heavy. Low data predictability ({confidence}). Downscaling aggressive budgets.")
             actions.append(ActionProposal(
                 action_type="REDUCE_BUDGET",
                 target="all_campaigns",
                 rationale="Fallback to conservative burn until predictive models repopulate accurate priors.",
                 parameters={"decrease_pct": 10},
                 expected_cpa_delta= -0.05
             ))

        # 2. Prevent over-scaling when momentum is weak
        momentum = context.get("momentum", "flat")
        if momentum != "positive" and not flags.get("high_market_pressure") and op_action == "EXECUTE":
            observations.append("False positive execution. Baseline momentum is not strong enough to scale. Retracting.")
            # Risk doesn't propose execution here, just flags high risk to temper Growth.

        return AgentInsight(
            agent_role=AgentRole.RISK,
            observations=observations,
            proposed_actions=actions,
            confidence_score=0.95, # Risk Agent is highly confident in avoiding loss
            risk_level="none" # It's the risk manager.
        )
