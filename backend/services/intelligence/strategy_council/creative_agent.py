"""
Creative Intelligence Agent
===========================
Focuses entirely on the Creative Genome, DNA saturation metrics, 
and fatigue profiling. Recommends pivots to unsaturated archetypes.
"""

from typing import Dict, Any, List
from .models import AgentInsight, AgentRole, ActionProposal

class CreativeAgent:
    
    def analyze(self, context: Dict[str, Any]) -> AgentInsight:
        """Analyze strategic context from the perspective of creative DNA."""
        observations = []
        actions = []
        
        flags = context.get("critical_flags", {})
        directional = context.get("directional_signals", {})
        
        # 1. Fatigue Detection
        if flags.get("creative_fatigue"):
            observations.append("Severe creative fatigue detected on active clusters.")
            actions.append(ActionProposal(
                action_type="REDUCE_BUDGET",
                target="fatigued_creatives",
                rationale="Prevent wasted spend on exhausted creative permutations.",
                parameters={"decrease_pct": 20},
                expected_cpa_delta= -0.05 # Pausing losers improves CPA slightly
            ))
            
        # 2. Angle Generation
        pivots = directional.get("recommended_creative_pivots", [])
        if pivots:
            observations.append(f"Identified {len(pivots)} high-potential, unsaturated archetypes to launch.")
            actions.append(ActionProposal(
                action_type="NEW_CREATIVE_ANGLE",
                target="forge_sandbox",
                rationale="Inject novel messaging DNA to replace attrited clusters.",
                parameters={"archetype_ids": pivots, "budget_allocation": "15%"},
                expected_cpa_delta= -0.10 # Assume winner breakout
            ))
            
        conf = 0.85 if flags.get("creative_fatigue") else 0.50
        
        return AgentInsight(
            agent_role=AgentRole.CREATIVE,
            observations=observations,
            proposed_actions=actions,
            confidence_score=conf,
            risk_level="medium"
        )
