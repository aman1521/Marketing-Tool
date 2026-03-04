"""
Agent Debate Engine
===================
Reviews all proposed actions from the 5 specialized agents. 
Identifies contradictions (e.g., Growth wants to scale, Risk wants to reduce) 
and synthesizes a resolution through structured debate rules.
"""

from typing import List, Dict, Any, Tuple
from .models import AgentInsight, DebateInteraction, AgentRole

class DebateEngine:
    
    def run_debate(self, insights: List[AgentInsight]) -> List[DebateInteraction]:
        """
        Takes raw agent insights, finds overlaps, and outputs a debate log 
        that challenges or modifies proposals.
        """
        interactions = []
        
        # Unpack agents
        indexed = {i.agent_role: i for i in insights}
        growth_agent   = indexed.get(AgentRole.GROWTH)
        risk_agent     = indexed.get(AgentRole.RISK)
        creative_agent = indexed.get(AgentRole.CREATIVE)
        market_agent   = indexed.get(AgentRole.MARKET)

        # Debate Rule 1: Risk overrides Growth on Aggressive Scaling
        if growth_agent and risk_agent:
            growth_actions = [a for a in growth_agent.proposed_actions if a.action_type in ("SCALE_BUDGET", "PLATFORM_SHIFT")]
            risk_actions   = [a for a in risk_agent.proposed_actions if a.action_type == "REDUCE_BUDGET"]
            
            if growth_actions and risk_actions:
                 interactions.append(
                     DebateInteraction(
                         source_agent=AgentRole.RISK,
                         target_agent=AgentRole.GROWTH,
                         interaction_type="challenge",
                         rationale="Memory/Momentum baseline prevents aggressive scaling. Capping expansion to preserve ROAS.",
                         proposed_adjustment={"action_type": "SCALE_BUDGET", "parameters": {"increase_pct": 0, "status": "blocked"}}
                     )
                 )
                 
        # Debate Rule 2: Market Volatility restricts Creative pivots
        if creative_agent and market_agent:
             creative_pivots = [a for a in creative_agent.proposed_actions if a.action_type == "NEW_CREATIVE_ANGLE"]
             market_pauses   = [a for a in market_agent.proposed_actions if a.action_type == "PAUSE_CAMPAIGN"]
             
             if creative_pivots and market_pauses:
                  interactions.append(
                     DebateInteraction(
                         source_agent=AgentRole.MARKET,
                         target_agent=AgentRole.CREATIVE,
                         interaction_type="refine",
                         rationale="Extreme market volatility limits A/B testing predictability. Shrinking sandbox testing scope.",
                         proposed_adjustment={"action_type": "NEW_CREATIVE_ANGLE", "parameters": {"budget_allocation": "5%"}}
                     )
                 )
                  
        # Debate Rule 3: Growth supports Creative's New Angle if Momentum is strong
        if growth_agent and creative_agent and growth_agent.confidence_score > 0.8:
             creative_pivots = [a for a in creative_agent.proposed_actions if a.action_type == "NEW_CREATIVE_ANGLE"]
             if creative_pivots:
                  interactions.append(
                     DebateInteraction(
                         source_agent=AgentRole.GROWTH,
                         target_agent=AgentRole.CREATIVE,
                         interaction_type="support",
                         rationale="Strong business momentum observed. Accelerating novel creative discovery vectors.",
                         proposed_adjustment={"action_type": "NEW_CREATIVE_ANGLE", "parameters": {"budget_allocation": "25%"}}
                     )
                 )
                  
        return interactions
