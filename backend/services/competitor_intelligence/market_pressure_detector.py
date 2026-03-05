"""
Market Pressure Detector
========================
Computes a 0–100 market pressure score for a company based on
competitor intelligence signals.

Inputs (from similarity engine + registry):
  - Number of active competitors crawled
  - Average ad saturation index
  - Dominant messaging theme saturation
  - Cluster count and concentration
  - Creative overlap density

Output: MarketPressureSignal (JSON-serialisable)
  → consumed by CaptainStrategy (read-only signal, no execution)
"""

import logging
import math
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketPressureDetector:
    """
    Deterministic pressure scoring algorithm.
    All weights are documented and traceable.
    """

    # ── Scoring weights ──────────────────────────────────────────
    WEIGHTS = {
        "competitor_density"  : 0.25,   # How many active competitors
        "saturation_index"    : 0.30,   # How saturated dominant themes are
        "cluster_concentration": 0.20,  # Are competitors all saying the same thing?
        "ad_volume_proxy"     : 0.15,   # Total ad count (proxy for spend pressure)
        "creative_diversity"  : 0.10,   # Inverse: low diversity = high pressure
    }

    # ── Normalisation caps ───────────────────────────────────────
    MAX_COMPETITORS = 20   # saturates at 20 active competitors
    MAX_ADS         = 100  # saturates at 100 captured ads

    def compute(self, competitor_count: int, cluster_data: Dict[str, Any],
                 ad_list: List[Dict]) -> Dict[str, Any]:
        """
        Compute market pressure score.

        Args:
            competitor_count: actively tracked competitors for this company
            cluster_data: output from SimilarityEngine.analyze_ad_clusters()
            ad_list: full list of captured ad creative dicts

        Returns:
            MarketPressureSignal dict
        """
        clusters         = cluster_data.get("clusters", [])
        saturation_index = cluster_data.get("saturation_index", 0.0)
        cluster_count    = cluster_data.get("cluster_count", 0)
        dominant_theme   = cluster_data.get("dominant_theme", "unknown")
        total_ads        = len(ad_list)

        # ── Sub-scores (each 0–1) ────────────────────────────────

        # 1. Competitor density
        density_score = min(1.0, competitor_count / self.MAX_COMPETITORS)

        # 2. Saturation — directly from cluster engine
        saturation_score = saturation_index

        # 3. Cluster concentration
        # High concentration (few large clusters) = more pressure
        if cluster_count == 0:
            concentration_score = 0.0
        else:
            avg_size = sum(c["member_count"] for c in clusters) / cluster_count
            concentration_score = min(1.0, avg_size / max(1, total_ads) * 5)

        # 4. Ad volume proxy
        volume_score = min(1.0, total_ads / self.MAX_ADS)

        # 5. Creative diversity (inverse of saturation)
        # If there are many distinct clusters, diversity is high → less pressure
        if total_ads == 0:
            diversity_score = 1.0
        else:
            unique_themes = len(set(c["theme"] for c in clusters))
            diversity_score = 1.0 - min(1.0, unique_themes / max(1, cluster_count))

        # ── Weighted composite ───────────────────────────────────
        raw_pressure = (
            density_score      * self.WEIGHTS["competitor_density"]
            + saturation_score * self.WEIGHTS["saturation_index"]
            + concentration_score * self.WEIGHTS["cluster_concentration"]
            + volume_score     * self.WEIGHTS["ad_volume_proxy"]
            + diversity_score  * self.WEIGHTS["creative_diversity"]
        )

        # Sigmoid squeeze to 0–100
        pressure_score = round(100 * (2 / (1 + math.exp(-4 * raw_pressure)) - 1), 1)
        pressure_score = max(0.0, min(100.0, pressure_score))

        # ── Opportunity flag ─────────────────────────────────────
        # Opportunity exists when pressure is high but dominant theme is saturated
        # → gap for differentiated angle
        unique_angle_opportunity = (
            pressure_score > 55
            and saturation_score > 0.65
        )

        # ── Pressure tier ────────────────────────────────────────
        if pressure_score < 25:
            tier = "LOW"
        elif pressure_score < 50:
            tier = "MODERATE"
        elif pressure_score < 75:
            tier = "HIGH"
        else:
            tier = "CRITICAL"

        signal = {
            "pressure_score":           pressure_score,
            "pressure_tier":            tier,
            "competitor_count_active":  competitor_count,
            "total_ads_captured":       total_ads,
            "cluster_count":            cluster_count,
            "saturation_index":         round(saturation_score, 4),
            "dominant_theme":           dominant_theme,
            "unique_angle_opportunity": unique_angle_opportunity,
            "sub_scores": {
                "competitor_density":    round(density_score, 4),
                "saturation":            round(saturation_score, 4),
                "cluster_concentration": round(concentration_score, 4),
                "ad_volume_proxy":       round(volume_score, 4),
                "creative_diversity":    round(diversity_score, 4),
            },
            "computed_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Market pressure computed: {pressure_score}/100 [{tier}] "
            f"| competitors={competitor_count} | clusters={cluster_count} "
            f"| opportunity={unique_angle_opportunity}"
        )
        return signal

    def interpret(self, signal: Dict[str, Any]) -> str:
        """Return a human-readable summary for dashboard display."""
        tier  = signal["pressure_tier"]
        score = signal["pressure_score"]
        theme = signal["dominant_theme"]
        opp   = signal["unique_angle_opportunity"]

        lines = [f"Market pressure: {score}/100 ({tier})"]
        if tier in ("HIGH", "CRITICAL"):
            lines.append(f"Dominant messaging: '{theme}' is saturated across competitors.")
        if opp:
            lines.append("⚡ Unique angle opportunity detected — competitors are converging on the same message.")
        elif tier == "LOW":
            lines.append("Market is relatively uncrowded. Current creative strategy has room to breathe.")
        return " ".join(lines)
