"""
Market Analyst Agent
====================
Focuses on tracking external market signals, algorithm shifts, 
and category macro tailwinds. Highlights volatility.
"""

from typing import Dict, Any, List
from .models import AgentInsight, AgentRole, ActionProposal

class MarketAgent:
    
    def analyze(self, context: Dict[str, Any]) -> AgentInsight:
        observations = []
        actions = []
        
        market = context.get("market_signals", {})
        cpm_trend = market.get("cpm_trend", 0.0)
        volatility = market.get("volatility_index", 0.0)

        # 1. Broad Volatility Risk
        if volatility > 0.60:
            observations.append("Extreme market instability detected (algorithimic shakeup/seasonal shock).")
            # Usually volatile markets punish big spending jumps
            actions.append(ActionProposal(
                action_type="PAUSE_CAMPAIGN",
                target="learning_phase_ads", # Prune learning phase ads taking a beating
                rationale="Protect core ROAS during extreme algorithmic volatility by killing unstable ads.",
                expected_cpa_delta= -0.05
            ))
            
        # 2. Deflationary Channel Acquisition
        if cpm_trend < -0.10:
             observations.append(f"CPM deflation active in overarching platform: {market.get('platform_momentum')}.")
             actions.append(ActionProposal(
                action_type="AUDIENCE_EXPANSION",
                target=market.get("platform_momentum", "meta"),
                rationale="Seize underpriced inventory aggressively.",
                parameters={"lift_budget": 20},
                expected_cpa_delta= -0.18 # Macro opportunity
            ))
             
        conf = 0.70 if cpm_trend != 0.0 else 0.40
        return AgentInsight(
            agent_role=AgentRole.MARKET,
            observations=observations,
            proposed_actions=actions,
            confidence_score=conf,
            risk_level="high" if volatility > 0.60 else "low"
        )
