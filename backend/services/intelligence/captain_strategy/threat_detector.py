"""
Threat Detector
===============
Understanding Layer: Scans fused signals for decay, fatigue, 
and negative asymmetries indicating risk.
"""

from typing import Dict, Any, List

class ThreatDetector:
    """
    Detects critical risks from a fused signal matrix.
    """

    def scan(self, fused_matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns a list of structured threats representing downside risks.
        """
        threats = []
        flags = fused_matrix.get("critical_flags", {})
        directional = fused_matrix.get("directional_signals", {})
        
        op_action = directional.get("operator_action")

        # 1. Negative Memory Prior / Bad Pattern
        if fused_matrix.get("momentum") == "negative" and fused_matrix.get("confidence_score", 0) > 0.60:
            threats.append({
                "title":           "Negative Strategy Baseline",
                "dimension":       "systemic",
                "rationale":       f"Operator memory shows consistent loss probability (action: {op_action}).",
                "severity":        "high" if op_action in ("BLOCK", "AVOID") else "medium"
            })

        # 2. Market Saturation / Burn
        if flags.get("high_market_pressure"):
            threats.append({
                "title":           "High Competitor Saturation",
                "dimension":       "market",
                "rationale":       "Market is flooded with similar strategies and high density competition.",
                "severity":        "high"
            })

        # 3. Creative Fatigue & Rotation Crisis
        if flags.get("creative_fatigue"):
            threats.append({
                "title":           "Creative Fatigue Detected",
                "dimension":       "creative",
                "rationale":       "Active campaigns are signaling cluster saturation and dropping win rates.",
                "severity":        "medium" 
            })

        # 4. Low Confidence Baseline (Risk of Unknowns)
        if fused_matrix.get("confidence_score", 0) < 0.35 and op_action == "MONITOR":
            threats.append({
                "title":           "Low System Confidence",
                "dimension":       "predictability",
                "rationale":       "Insufficient global memory patterns to predict outcomes reliably.",
                "severity":        "low" 
            })

        return threats
