"""
Opportunity Detector
====================
Understanding Layer: Scans fused signals for positive asymmetrical bets.
"""

from typing import Dict, Any, List

class OpportunityDetector:
    """
    Detects actionable marketing opportunities from a fused signal matrix.
    """

    def scan(self, fused_matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns a list of structured opportunities.
        An opportunity must have: 
        - title
        - dimension (e.g. creative, budget, audience)
        - signal_strength (0-1)
        """
        opportunities = []
        flags = fused_matrix.get("critical_flags", {})
        directional = fused_matrix.get("directional_signals", {})
        
        op_action = directional.get("operator_action")
        pivots    = directional.get("recommended_creative_pivots", [])
        gaps      = directional.get("unexploited_gaps", [])

        # 1. Budget Scaling Opportunity
        if op_action == "EXECUTE" and fused_matrix.get("confidence_score", 0) > 0.70:
            if not flags.get("high_market_pressure") and fused_matrix.get("momentum") == "positive":
                opportunities.append({
                    "title":           "Aggressive Budget Scaling",
                    "dimension":       "budget",
                    "rationale":       f"Strong PGIL memory signal (confidence: {fused_matrix['confidence_score']}) with positive momentum.",
                    "signal_strength": 0.90
                })

        # 2. Creative Pivot Opportunity
        if pivots:
            opportunities.append({
                "title":           "Unsaturated Creative Archetypes",
                "dimension":       "creative",
                "rationale":       f"Found {len(pivots)} high-performing archetypes to test.",
                "signal_strength": 0.85,
                "archetype_ids":   pivots
            })

        # 3. Strategy Gap Opportunity
        for gap in gaps:
            opportunities.append({
                "title":           "Exploit Competitor Strategy Gap",
                "dimension":       "messaging",
                "rationale":       f"Gap detected: {gap}",
                "signal_strength": 0.75
            })

        return opportunities
