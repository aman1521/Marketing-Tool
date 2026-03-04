"""
Growth Agent
============
Focuses on scaling opportunities, budget expansion, and channel arbitrage.
Identifies positive momentum and aggressively pursues them.
"""

from typing import Dict, Any, List
from .models import AgentInsight, AgentRole, ActionProposal

class GrowthAgent:
    
    def analyze(self, context: Dict[str, Any]) -> AgentInsight:
        """Analyze strategic context from a purely scaling perspective."""
        observations = []
        actions = []
        conf = 0.5
        
        # 1. Evaluate Momentum
        momentum = context.get("momentum", "flat")
        if momentum == "positive":
            observations.append("Strong positive momentum detected across current campaigns.")
            conf = 0.85
            actions.append(ActionProposal(
                action_type="SCALE_BUDGET",
                target="winning_campaigns",
                rationale="Momentum is highly positive. Scale aggressively while CPA is stable.",
                parameters={"increase_pct": 25},
                expected_cpa_delta=0.08  # Typically CPA rises slightly with scaling
            ))

        # 2. Channel Arbitrage (Mock logic based on market signals)
        ms = context.get("market_signals", {})
        if ms.get("platform_momentum") == "tiktok":
            observations.append("TikTok currently showing macro performance tailwinds in this industry.")
            if not any(a.action_type == "PLATFORM_SHIFT" for a in actions):
                actions.append(ActionProposal(
                    action_type="PLATFORM_SHIFT",
                    target="tiktok_sandboxes",
                    rationale="Exploit TikTok macro-momentum. Capital reallocation recommended.",
                    parameters={"shift_pct": 15},
                    expected_cpa_delta=-0.15 # Expect cheaper acquisition
                ))

        if not observations:
            observations.append("Growth plateau. No obvious scaling asymmetry found.")
            conf = 0.40
            
        return AgentInsight(
            agent_role=AgentRole.GROWTH,
            observations=observations,
            proposed_actions=actions,
            confidence_score=conf,
            risk_level="high" if momentum == "positive" else "low"
        )
