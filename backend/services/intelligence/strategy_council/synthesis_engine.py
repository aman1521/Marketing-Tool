"""
Council Synthesis Engine
========================
Takes the finalized outputs of the Multi-Agent Strategy Council 
(Agent Insights + Debate Interactions) and synthesizes the definitive
CouncilSynthesis strategy object.
"""

from typing import List, Dict, Any
from .models import AgentInsight, DebateInteraction, CouncilSynthesis, ActionProposal, AgentRole

class SynthesisEngine:
    
    def synthesize(self, insights: List[AgentInsight], debates: List[DebateInteraction]) -> CouncilSynthesis:
        """
        Merge all valid actions not overridden by debates.
        Format a collective strategic narrative.
        """
        final_actions = []
        debate_narrative = []
        observations_pool = []
        
        # Track what actions get challenged or refined
        blocked_actions = []
        refined_actions = {}
        
        for db in debates:
            if db.interaction_type == "challenge":
                debate_narrative.append(f"{db.source_agent.value} blocked {db.target_agent.value}: {db.rationale}")
                # Block the specific action target
                if db.proposed_adjustment:
                    blocked_actions.append(db.proposed_adjustment.get("action_type"))
                    
            elif db.interaction_type == "refine":
                debate_narrative.append(f"{db.source_agent.value} restricted {db.target_agent.value}: {db.rationale}")
                if db.proposed_adjustment:
                    refined_actions[db.proposed_adjustment.get("action_type")] = db.proposed_adjustment.get("parameters")
                    
            elif db.interaction_type == "support":
                debate_narrative.append(f"{db.source_agent.value} accelerated {db.target_agent.value}: {db.rationale}")
                if db.proposed_adjustment:
                    refined_actions[db.proposed_adjustment.get("action_type")] = db.proposed_adjustment.get("parameters")

        overall_conf = 0.0
        cpa_sum = 0.0

        for insight in insights:
             # Pool observations from all agents
             observations_pool.extend(insight.observations)
             overall_conf += insight.confidence_score
             
             for action in insight.proposed_actions:
                  if action.action_type in blocked_actions:
                      continue
                      
                  # Apply refinements if any
                  if action.action_type in refined_actions:
                      # e.g., budget allocation change
                      action.parameters.update(refined_actions[action.action_type])
                      
                  final_actions.append(action)
                  cpa_sum += action.expected_cpa_delta

        avg_conf = overall_conf / max(1, len(insights))
        avg_cpa  = cpa_sum / max(1, len(final_actions))

        return CouncilSynthesis(
            opportunity_summary=" | ".join(observations_pool[:3]), # Take highest signal obs
            threat_summary=" | ".join(observations_pool[-2:]), # Mock grouping
            final_actions=final_actions,
            overall_confidence=round(avg_conf, 4),
            expected_cpa_change=round(avg_cpa, 4),
            debate_summary=debate_narrative
        )
