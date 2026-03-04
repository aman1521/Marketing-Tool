"""
Creative Archetype Builder
==========================
Analyzes top-performing Genome Clusters and builds reusable creative templates.

Archetype lifecycle:
  CANDIDATE  → Promising cluster (high lift, low saturation)
  CONFIRMED  → Statistically significant win rate & confidence > 0.70
  RETIRED    → Cluster saturated or performance declining

Output provides templates for creative generation via Forge
and influence modifiers for CaptainStrategy.
"""

import math
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from collections import Counter

from .genome_vectorizer import GenomeVectorizer
from .genome_cluster_engine import GenomeClusterEngine, _clusters as gs_clusters

logger = logging.getLogger(__name__)

CONFIRMED_MIN_SAMPLES = 10
CONFIRMED_CONFIDENCE  = 0.70
CONFIRMED_WIN_RATE    = 0.60
SATURATED_THRESHOLD   = 0.75

MAX_BIAS = 0.15
MIN_BIAS = -0.10

# In-memory store
_archetypes: Dict[str, Dict] = {}


class CreativeArchetypeBuilder:
    """
    Transforms winning genome clusters into actionable creative archetypes.
    """

    def __init__(self, vectorizer: Optional[GenomeVectorizer] = None,
                 cluster_engine: Optional[GenomeClusterEngine] = None):
        self.vectorizer = vectorizer or GenomeVectorizer()
        self.clusters   = cluster_engine or GenomeClusterEngine()

    def build_from_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """
        Evaluate clusters and generate or update candidate/confirmed archetypes.
        """
        created = updated = 0
        for c in clusters:
            if c.get("avg_ctr_lift", 0) <= 0.0 or c["member_count"] < 3:
                continue

            existing = self._find_by_cluster(c["id"])
            if existing:
                self._update(existing, c)
                updated += 1
            else:
                arch = self._create(c)
                _archetypes[arch["id"]] = arch
                self.vectorizer.store_archetype(arch)
                created += 1

        logger.info(f"[CreativeArchetypes] Built: created={created} updated={updated}")
        return list(_archetypes.values())

    def run_lifecycle(self) -> Dict[str, int]:
        """Promote/retire archetypes based on updated evidence."""
        promoted = retired = 0
        for arch in _archetypes.values():
            old = arch["status"]
            new = self._compute_status(arch)
            
            if new != old:
                arch["status"] = new
                arch["bias_modifier"] = self._compute_bias(arch) if new == "confirmed" else 0.0
                arch["last_updated"]  = datetime.now(timezone.utc).isoformat()
                self.vectorizer.store_archetype(arch)
                
                if new == "confirmed":
                    promoted += 1
                    logger.info(f"[CreativeArchetypes] CONFIRMED [{arch['name']}] bias={arch['bias_modifier']:+.3f}")
                elif new == "retired":
                    retired += 1
                    logger.info(f"[CreativeArchetypes] RETIRED [{arch['name']}]")

        return {"promoted": promoted, "retired": retired, "total": len(_archetypes)}

    def get_confirmed(self) -> List[Dict]:
        return [a for a in _archetypes.values() if a["status"] == "confirmed"]

    def suggest_template(self, industry: str) -> Optional[Dict]:
        """Suggest highest performing unsaturated archetype for an industry."""
        confirmed = self.get_confirmed()
        valid = [
            a for a in confirmed
            if (industry in a.get("industry_fit", {}) or "other" in a.get("industry_fit", {}))
            and a.get("status") == "confirmed"
        ]
        if not valid:
            return None
        valid.sort(key=lambda a: -(a["expected_ctr_lift"] * a["confidence"]))
        return valid[0]

    def _create(self, c: Dict) -> Dict:
        status = "candidate"
        if c["member_count"] >= CONFIRMED_MIN_SAMPLES and \
           c["confidence"] >= CONFIRMED_CONFIDENCE and \
           c["win_rate"] >= CONFIRMED_WIN_RATE and \
           c["saturation_score"] < SATURATED_THRESHOLD:
            status = "confirmed"

        avg_lift = c.get("avg_ctr_lift", 0.0)
        win_rate = c.get("win_rate", 0.0)
        conf     = c.get("confidence", 0.0)

        industry_fit = {ind: 1.0 for ind in c.get("industries", ["other"])}

        name = f"{c['dominant_emotion'].title()} {c['dominant_hook'].title()}"
        if c.get("dominant_authority") and c["dominant_authority"] != "none":
            name += f" + {c['dominant_authority'].title()}"

        arch = {
            "id":                str(uuid.uuid4()),
            "name":              name,
            "description":       f"Winning cluster pattern. Expected CTR lift: {avg_lift:+.1%}",
            "status":            status,
            "hook_type":         c.get("dominant_hook"),
            "emotion":           c.get("dominant_emotion"),
            "authority_signal":  c.get("dominant_authority"),
            "structure":         c.get("dominant_structure"),
            "sample_count":      c["member_count"],
            "avg_ctr_lift":      round(avg_lift, 4),
            "expected_ctr_lift": round(avg_lift, 4),
            "win_rate":          round(win_rate, 4),
            "confidence":        round(conf, 4),
            "bias_modifier":     0.0,
            "industry_fit":      industry_fit,
            "source_cluster_id": c["id"],
            "created_at":        datetime.now(timezone.utc).isoformat(),
            "last_updated":      datetime.now(timezone.utc).isoformat(),
        }

        if status == "confirmed":
            arch["bias_modifier"] = self._compute_bias(arch)
            
        return arch

    def _update(self, arch: Dict, c: Dict):
        arch["sample_count"]      = c["member_count"]
        arch["avg_ctr_lift"]      = round(c.get("avg_ctr_lift", 0.0), 4)
        arch["expected_ctr_lift"] = arch["avg_ctr_lift"]
        arch["win_rate"]          = round(c.get("win_rate", 0.0), 4)
        arch["confidence"]        = round(c.get("confidence", 0.0), 4)
        
        for ind in c.get("industries", []):
            arch["industry_fit"][ind] = 1.0

        arch["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.vectorizer.store_archetype(arch)

    def _find_by_cluster(self, cluster_id: str) -> Optional[Dict]:
        for a in _archetypes.values():
            if a["source_cluster_id"] == cluster_id:
                return a
        return None

    def _compute_status(self, arch: Dict) -> str:
        # Check source cluster saturation
        c = gs_clusters.get(arch["source_cluster_id"])
        sat = c.get("saturation_score", 0.0) if c else 0.0

        n    = arch.get("sample_count", 0)
        conf = arch.get("confidence", 0.0)
        wr   = arch.get("win_rate", 0.0)
        
        if sat >= SATURATED_THRESHOLD or wr < 0.40:
            return "retired"
        if n >= CONFIRMED_MIN_SAMPLES and conf >= CONFIRMED_CONFIDENCE and wr >= CONFIRMED_WIN_RATE:
            return "confirmed"
        return "candidate"

    @staticmethod
    def _compute_bias(arch: Dict) -> float:
        lift = arch.get("avg_ctr_lift", 0.0)
        wr   = arch.get("win_rate", 0.0)
        conf = arch.get("confidence", 0.0)
        perf = lift * 0.50 + (wr - 0.50) * 0.35 + conf * 0.15
        bias = perf * MAX_BIAS if perf >= 0 else perf * abs(MIN_BIAS)
        return round(max(MIN_BIAS, min(MAX_BIAS, bias)), 4)
