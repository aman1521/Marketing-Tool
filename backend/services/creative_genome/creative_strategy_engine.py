"""
Creative Strategy Engine
========================
Translates genome clusters and archetypes into actionable signals for
CaptainStrategy and Forge integration.

Detects:
  - CLUSTER_SATURATION : Current creative belongs to an overused cluster
  - NEW_ANGLE         : Recommends pivoting to an unsaturated, high-lift archetype
  - FATIGUE           : Rapid win_rate decline in a specific genome
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .genome_cluster_engine import GenomeClusterEngine
from .creative_archetype_builder import CreativeArchetypeBuilder
from .models import CreativeStrategySignal

logger = logging.getLogger(__name__)


class CreativeStrategyEngine:
    """
    Feeds creative genome insights to external execution layers.
    Generates structured recommendations based on cluster saturation and archetype performance.
    """

    def __init__(self, cluster_engine: Optional[GenomeClusterEngine] = None,
                 archetype_builder: Optional[CreativeArchetypeBuilder] = None):
        self.clusters   = cluster_engine or GenomeClusterEngine()
        self.archetypes = archetype_builder or CreativeArchetypeBuilder()

    def generate_signal(self, current_genome: Dict[str, Any],
                         industry: str = "other") -> Optional[Dict[str, Any]]:
        """
        Evaluate a current creative genome and generate a strategic recommendation.
        Returns a dict representing a CreativeStrategySignal, or None if no action needed.
        """
        # 1. Find the cluster for the current genome
        cluster = self.clusters.find_cluster(current_genome)

        if not cluster:
            logger.debug("[StrategyEngine] No matching cluster for current genome. Proceeding baseline.")
            return None

        sat_score = cluster.get("saturation_score", 0.0)
        win_rate  = cluster.get("win_rate", 0.5)
        n_samples = cluster.get("member_count", 0)

        # 2. Check for Fatigue / Saturation
        if sat_score >= 0.65 or (n_samples > 10 and win_rate < 0.35):
            signal_type = "FATIGUE" if win_rate < 0.35 else "CLUSTER_SATURATION"
            severity    = "HIGH" if sat_score >= 0.85 or win_rate < 0.25 else "MEDIUM"
            
            rec = {
                "signal_type":     signal_type,
                "severity":        severity,
                "current_cluster": cluster["name"],
                "recommended_action": f"Reduce spend on current creative group. {cluster['name']} is showing signs of {signal_type.lower()}.",
                "recommended_tests": [],
                "archetype_id":    None,
                "confidence":      round(max(0.60, sat_score), 4),
            }

            # 3. Suggest New Angle (Archetype Pivot)
            pivot_arch = self.archetypes.suggest_template(industry)
            if pivot_arch:
                rec["recommended_action"] += f" Pivot to unsaturated high-lift archetype: {pivot_arch['name']}."
                rec["archetype_id"] = pivot_arch["id"]
                rec["recommended_tests"].append({
                    "hook_type":         pivot_arch.get("hook_type"),
                    "emotion":           pivot_arch.get("emotion"),
                    "authority_signal":  pivot_arch.get("authority_signal"),
                    "structure":         pivot_arch.get("structure"),
                })
            
            logger.info(f"[StrategyEngine] Generated {signal_type} signal. Severity: {severity}")
            return rec

        # 3. Emerging Winner (Optional feedback)
        if win_rate > 0.65 and n_samples >= 5 and sat_score < 0.40:
             return {
                "signal_type":     "NEW_ANGLE",
                "severity":        "LOW",
                "current_cluster": cluster["name"],
                "recommended_action": f"{cluster['name']} is an emerging winner. Scale aggressively before saturation.",
                "recommended_tests": [],
                "archetype_id":    None,
                "confidence":      round(cluster.get("confidence", 0.5), 4),
            }

        return None
