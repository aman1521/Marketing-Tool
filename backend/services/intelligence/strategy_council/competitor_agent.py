"""
Competitor Analyst Agent
========================
Focuses purely on strategic intelligence, saturation pressure, and funnel gaps.
Extracts insights directly from similarity indexing.
"""

from typing import Dict, Any, List
from .models import AgentInsight, AgentRole, ActionProposal

class CompetitorAgent:
    
    def analyze(self, context: Dict[str, Any]) -> AgentInsight:
        observations = []
        actions = []
        
        intel = context.get("competitor_intelligence", {})
        pressure = intel.get("market_pressure")
        gaps = intel.get("strategy_gaps", [])

        # 1. Competitor Density Blocking
        if context.get("critical_flags", {}).get("high_market_pressure"):
             observations.append(f"Intense market saturation detected in cluster {pressure.get('cluster')}. Competitor density highly elevated.")
             # Threat reaction
             actions.append(ActionProposal(
                action_type="REDUCE_BUDGET",
                target=pressure.get("cluster"),
                rationale="Scale down in highly contested quadrants. Bidding war shrinks margin.",
                parameters={"decrease_pct": 20},
                expected_cpa_delta= -0.05
            ))

        # 2. Extract White Space
        for gap in gaps[:2]:
            observations.append(f"Uncontested messaging territory found: {gap.get('summary')}")
            actions.append(ActionProposal(
                action_type="OFFER_CHANGE",
                target="landing_page_hook",
                rationale=gap.get("summary"),
                parameters={"new_message_angle": gap.get("dimension")},
                expected_cpa_delta= -0.12 # Differentiated angles map cheaper CPA theoretically
            ))
            
        return AgentInsight(
            agent_role=AgentRole.COMPETITOR,
            observations=observations,
            proposed_actions=actions,
            confidence_score=0.80 if gaps else 0.50,
            risk_level="medium"
        )
