import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Maximum bias modifier magnitude (±15%)
MAX_BIAS = 0.15
MIN_CONFIDENCE_TO_APPLY = 0.65


class StrategyArchetypeEngine:
    """
    Converts high-confidence knowledge patterns into simulation weight biases
    for CaptainStrategy. Does NOT auto-modify core execution logic.
    Bias only — human remains in control of the envelope.
    """

    def compute_bias(self, context: Dict[str, Any],
                     archetypes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        context: {industry, strategy_type, aov_tier, creative_archetype, scaling_band}
        archetypes: list from KnowledgeRegistry.get_high_confidence_archetypes()
        """
        # Find matching archetypes
        matches = [
            a for a in archetypes
            if a["industry"] == context.get("industry")
            and a["strategy_type"] == context.get("strategy_type")
            and a["confidence_score"] >= MIN_CONFIDENCE_TO_APPLY
        ]

        if not matches:
            return {"bias_modifier": 0.0, "source": "no_match", "applied_pattern": None}

        # Highest confidence match drives the bias
        best = max(matches, key=lambda a: a["confidence_score"])
        raw_lift = best["avg_lift_pct"] / 100.0   # normalize

        # Scale bias: confident pattern → stronger positive weighting
        bias = round(min(MAX_BIAS, raw_lift * best["confidence_score"]), 4)

        logger.info(f"Archetype bias applied: {bias:+.4f} from pattern {best['pattern_id']}")

        return {
            "bias_modifier": bias,
            "source": "archetype_match",
            "applied_pattern": best["pattern_id"],
            "confidence": best["confidence_score"],
            "avg_lift_pct": best["avg_lift_pct"]
        }


class LiftPatternDetector:
    """
    Scans archetype registry to detect repeating high-lift and high-risk patterns.
    Emits structured detection reports.
    """

    def detect(self, archetypes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not archetypes:
            return {"repeating_lift": [], "risk_clusters": [], "failure_clusters": []}

        repeating_lift = [
            a for a in archetypes
            if a["avg_lift_pct"] > 15.0 and a["sample_count"] >= 3
        ]

        risk_clusters = [
            a for a in archetypes
            if a.get("avg_risk_exposure", 0) > 0.6 and a["sample_count"] >= 2
        ]

        failure_clusters = [
            a for a in archetypes
            if a["avg_lift_pct"] < 0 and a["sample_count"] >= 2
        ]

        return {
            "repeating_lift_patterns": [{
                "pattern_id": a["pattern_id"],
                "avg_lift_pct": a["avg_lift_pct"],
                "confidence": a["confidence_score"],
                "samples": a["sample_count"]
            } for a in repeating_lift],

            "risk_heavy_clusters": [{
                "pattern_id": a["pattern_id"],
                "avg_risk": a.get("avg_risk_exposure", "N/A")
            } for a in risk_clusters],

            "strategy_failure_clusters": [{
                "pattern_id": a["pattern_id"],
                "avg_lift_pct": a["avg_lift_pct"]
            } for a in failure_clusters]
        }
