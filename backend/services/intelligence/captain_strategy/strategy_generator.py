"""
Strategy Generator
==================
Decision Layer: Converts opportunities and threats into concrete Executable Actions.
Synthesizes the textual narrative for human operators.
"""

from typing import Dict, Any, List
from .models import ActionType

class StrategyGenerator:
    """
    Transforms detected symmetries (Opp/Threat) into an unstructured strategy payload.
    """

    def generate(self, opportunities: List[Dict[str, Any]], threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Produce recommended actions and generating a strategy brief.
        """
        actions = []
        narrative_lines = []

        # 1. Map Opportunities to Actions
        for opp in opportunities:
            if opp["dimension"] == "budget":
                actions.append({
                    "action_type": ActionType.SCALE_BUDGET,
                    "payload": {"increase_pct": 20},
                    "rationale": opp["rationale"]
                })
                narrative_lines.append(f"Opportunity: Scale aggressive due to signals ({opp['title']}).")
                
            elif opp["dimension"] == "creative" and opp.get("archetype_ids"):
                actions.append({
                    "action_type": ActionType.NEW_CREATIVE_ANGLE,
                    "payload": {"archetypes_to_test": opp["archetype_ids"][:3], "budget_allocation": "15%"},
                    "rationale": opp["rationale"]
                })
                narrative_lines.append(f"Opportunity: Pivot or test {len(opp.get('archetype_ids', []))} new creative archetypes.")

            elif opp["dimension"] == "messaging":
                actions.append({
                    "action_type": ActionType.OFFER_CHANGE,
                    "payload": {"new_message_angle": opp["rationale"]},
                    "rationale": opp["title"] 
                })
                narrative_lines.append(f"Opportunity: Exploit gap ({opp['title']}).")

        # 2. Map Threats to Defensive Actions
        for threat in threats:
            if threat["dimension"] == "systemic" and threat["severity"] == "high":
                actions.append({
                    "action_type": ActionType.PAUSE_CAMPAIGN,
                    "payload": {"criteria": "worst_performers", "count": 2},
                    "rationale": threat["rationale"]
                })
                narrative_lines.append(f"Threat Defense: Pausing worst campaigns due to {threat['title']}.")

            elif threat["dimension"] == "creative":
                actions.append({
                    "action_type": ActionType.REDUCE_BUDGET,
                    "payload": {"decrease_pct": 15, "target": "fatigued_creatives"},
                    "rationale": threat["rationale"] 
                })
                narrative_lines.append(f"Threat Defense: Scaling down budgets on fatigued patterns ({threat['title']}).")

            elif threat["dimension"] == "market" and threat["severity"] == "high":
                 narrative_lines.append(f"Threat Note: Exteme market saturation. All actions down-weighted in risk profile.")

        # Default action if nothing triggers
        if not actions:
            # Maybe just bid adjustments
            if not threats:
                actions.append({
                    "action_type": ActionType.BID_ADJUSTMENT,
                    "payload": {"direction": "optimization", "target": "roas"},
                    "rationale": "Stable state: minor systematic improvements recommended."
                })
            else:
                 narrative_lines.append("High risk state, no positive execution actions found.")
                 
        narrative = "Strategic Analysis Output:\n" + "\n".join(narrative_lines)

        return {
            "actions": actions,
            "narrative": narrative
        }
