"""
Signal Fusion Engine
====================
Understanding Layer: Weights and merges conflicting signals across
Operator Memory, Creative Genome, and Market forces.
"""

from typing import Dict, Any

class SignalFusionEngine:
    """
    Transforms raw Perception Data into a focused, weighted 
    Signal Matrix for Decision Layer processing.
    """

    def fuse_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw context builder output and creates weighted vectors.
        """
        # 1. Competitor Pressure Weighting
        pressure = context.get("competitor_intelligence", {}).get("market_pressure")
        gaps     = context.get("competitor_intelligence", {}).get("strategy_gaps", [])
        
        # 2. Extract specific scores
        op_mem       = context.get("operator_memory", {})
        mem_conf     = op_mem.get("confidence", 0.0)
        mem_lift     = op_mem.get("predicted_lift", 0.0)
        action_rec   = op_mem.get("action", "MONITOR")
        
        # 3. Assess Creative Fatigue & Momentum
        creative_issues = []
        creative_pivots = []
        for cs in context.get("creative_genome", {}).get("active_campaign_signals", []):
            sig  = cs.get("signal", {})
            stpt = sig.get("signal_type")
            if stpt in ("CLUSTER_SATURATION", "FATIGUE"):
                creative_issues.append({"campaign_id": cs.get("campaign_id"), "severity": sig.get("severity")})
                if sig.get("archetype_id"):
                    creative_pivots.append(sig["archetype_id"])

        # 4. Synthesize weights
        # Memory base logic
        overall_confidence = mem_conf
        global_momentum    = "positive" if mem_lift > 0.05 else ("negative" if mem_lift < -0.05 else "flat")
        
        fused = {
            "company_id":       context["company_id"],
            "industry":         context["industry"],
            "momentum":         global_momentum,
            "confidence_score": overall_confidence,
            
            "critical_flags": {
                "high_market_pressure": pressure and "saturation_score" in pressure and float(pressure["saturation_score"] or 0) > 0.8,
                "creative_fatigue":     len(creative_issues) > 0
            },
            
            "directional_signals": {
                "operator_action":      action_rec,     # EXECUTE, MONITOR, SANDBOX, etc.
                "recommended_creative_pivots": list(set(creative_pivots)),
                "unexploited_gaps":     [g["summary"] for g in gaps]
            },
            
            "raw_metrics_snapshot": context.get("current_performance", {})
        }

        return fused
