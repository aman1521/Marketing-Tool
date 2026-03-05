"""
Genome Cluster Engine
=====================
Clusters creative genomes by DNA similarity.

Algorithm:
  1. Greedy cosine-similarity clustering (threshold-based, O(n²))
  2. Each cluster tracks dominant genome component values
  3. Saturation scoring: high cluster density = saturated market signal
  4. Performance aggregation: avg CTR / CVR lift per cluster
  5. Lifecycle: GROWING → STABLE → SATURATED → DECLINING

Cluster saturation formula:
  saturation = (member_count / max_size) * 0.5
              + (age_days / 90) * 0.3
              + (win_rate_decline) * 0.2

Outputs fed to:
  - CreativeArchetypeBuilder (high-performance clusters)
  - CreativeStrategyEngine   (saturation alerts)
"""

import math
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict, Counter

from .genome_vectorizer import GenomeVectorizer

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.72
SATURATION_MEMBER_CAP = 20
MIN_PERFORMANCE_SAMPLES = 3

# In-memory stores
_clusters: Dict[str, Dict]  = {}
_genome_store: List[Dict]    = []


class GenomeClusterEngine:
    """
    Greedy DNA cluster engine for creative genomes.
    """

    def __init__(self):
        self.vectorizer = GenomeVectorizer()

    # ── Main clustering ────────────────────────────────────────────────────

    def add_genome(self, genome: Dict[str, Any],
                    ctr_lift: Optional[float] = None,
                    cvr_lift: Optional[float] = None,
                    outcome: str = "pending",
                    industry: str = "other") -> str:
        """
        Add a genome to the cluster engine.
        Returns the cluster_id it was assigned to.
        """
        genome_entry = {
            **genome,
            "id":        str(uuid.uuid4()),
            "ctr_lift":  ctr_lift,
            "cvr_lift":  cvr_lift,
            "outcome":   outcome,
            "industry":  industry,
            "added_at":  datetime.now(timezone.utc).isoformat(),
        }
        _genome_store.append(genome_entry)

        vec = self.vectorizer.feature_vector(genome)
        cluster_id = self._assign_cluster(genome_entry, vec)
        genome_entry["cluster_id"] = cluster_id
        return cluster_id

    def cluster_all(self, genomes: List[Dict],
                     performance_map: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        Cluster a batch of genomes from scratch.
        Returns list of cluster dicts.
        """
        _clusters.clear()
        _genome_store.clear()

        for g in genomes:
            perf = performance_map or {}
            self.add_genome(
                g,
                ctr_lift=perf.get("ctr_lift"),
                cvr_lift=perf.get("cvr_lift"),
                outcome=g.get("outcome","pending"),
                industry=g.get("industry","other"),
            )
        return self.get_clusters()

    # ── Cluster lifecycle ─────────────────────────────────────────────────

    def update_cluster_performance(self, cluster_id: str,
                                    ctr_lift: float, cvr_lift: float,
                                    outcome: str = "win"):
        """Update running performance stats for a cluster."""
        c = _clusters.get(cluster_id)
        if not c:
            return
        n = c["member_count"]
        c["avg_ctr_lift"] = round((c.get("avg_ctr_lift",0) * (n-1) + ctr_lift) / n, 4)
        c["avg_cvr_lift"] = round((c.get("avg_cvr_lift",0) * (n-1) + cvr_lift) / n, 4)
        if outcome == "win":
            c["win_count"] = c.get("win_count", 0) + 1
        c["win_rate"] = round(c.get("win_count",0) / c["member_count"], 4)
        c["confidence"] = self._wilson_lower(c.get("win_count",0), n)
        c["saturation_score"] = self._saturation(c)
        c["status"] = self._status(c)
        c["last_updated"] = datetime.now(timezone.utc).isoformat()

    def run_lifecycle(self) -> Dict[str, int]:
        """Recompute status for all clusters."""
        for c in _clusters.values():
            c["saturation_score"] = self._saturation(c)
            c["status"] = self._status(c)
        status_counts = Counter(c["status"] for c in _clusters.values())
        logger.info(f"[ClusterEngine] Lifecycle: {dict(status_counts)}")
        return dict(status_counts)

    # ── Query ─────────────────────────────────────────────────────────────

    def get_clusters(self, status: Optional[str] = None,
                      min_members: int = 1) -> List[Dict]:
        clusters = [c for c in _clusters.values() if c["member_count"] >= min_members]
        if status:
            clusters = [c for c in clusters if c["status"] == status]
        return sorted(clusters, key=lambda c: -(c.get("avg_ctr_lift") or 0.0))

    def find_cluster(self, genome: Dict[str, Any]) -> Optional[Dict]:
        """Find the closest cluster for a genome (no assignment)."""
        vec = self.vectorizer.feature_vector(genome)
        best_id, best_sim = None, 0.0
        for cid, c in _clusters.items():
            sim = self._cosine(vec, c["centroid"])
            if sim > best_sim:
                best_sim, best_id = sim, cid
        if best_id and best_sim >= SIMILARITY_THRESHOLD:
            return {**_clusters[best_id], "match_score": round(best_sim, 4)}
        return None

    def get_saturated_clusters(self, threshold: float = 0.65) -> List[Dict]:
        return [c for c in _clusters.values() if c.get("saturation_score",0) >= threshold]

    def get_top_performing(self, top_k: int = 5,
                            min_samples: int = MIN_PERFORMANCE_SAMPLES) -> List[Dict]:
        valid = [c for c in _clusters.values()
                  if c["member_count"] >= min_samples
                  and c.get("avg_ctr_lift") is not None]
        return sorted(valid, key=lambda c: -(c.get("avg_ctr_lift",0)))[:top_k]

    def cluster_summary(self) -> Dict[str, Any]:
        clusters = list(_clusters.values())
        if not clusters:
            return {"total": 0}
        return {
            "total":     len(clusters),
            "by_status": dict(Counter(c["status"] for c in clusters)),
            "saturated": sum(1 for c in clusters if c.get("saturation_score",0) >= 0.65),
            "avg_size":  round(sum(c["member_count"] for c in clusters)/len(clusters), 1),
            "total_genomes": len(_genome_store),
        }

    # ── Internals ──────────────────────────────────────────────────────────

    def _assign_cluster(self, genome: Dict, vec: List[float]) -> str:
        """Greedy assignment: find closest cluster above threshold or create new."""
        best_id, best_sim = None, 0.0
        for cid, c in _clusters.items():
            sim = self._cosine(vec, c["centroid"])
            if sim > best_sim and sim >= SIMILARITY_THRESHOLD:
                best_sim, best_id = sim, cid

        if best_id:
            self._add_to_cluster(best_id, genome, vec)
            return best_id
        else:
            return self._create_cluster(genome, vec)

    def _create_cluster(self, genome: Dict, vec: List[float]) -> str:
        cid  = str(uuid.uuid4())
        name = self._cluster_name(genome)
        _clusters[cid] = {
            "id":               cid,
            "name":             name,
            "centroid":         vec,
            "member_count":     1,
            "dominant_hook":    genome.get("hook_type"),
            "dominant_emotion": genome.get("emotion"),
            "dominant_structure":genome.get("structure"),
            "dominant_authority":genome.get("authority_signal"),
            "industries":       [genome.get("industry","other")],
            "avg_ctr_lift":     genome.get("ctr_lift"),
            "avg_cvr_lift":     genome.get("cvr_lift"),
            "win_count":        1 if genome.get("outcome")=="win" else 0,
            "win_rate":         1.0 if genome.get("outcome")=="win" else 0.0,
            "confidence":       0.0,
            "saturation_score": 0.0,
            "status":           "growing",
            "first_seen":       datetime.now(timezone.utc).isoformat(),
            "last_updated":     datetime.now(timezone.utc).isoformat(),
        }
        logger.debug(f"[ClusterEngine] New cluster [{cid[:8]}]: {name}")
        return cid

    def _add_to_cluster(self, cid: str, genome: Dict, vec: List[float]):
        """Update cluster centroid (running average) and stats."""
        c = _clusters[cid]
        n = c["member_count"] + 1
        # Update centroid (incremental mean)
        old_c = c["centroid"]
        new_c = [(old_c[i] * (n-1) + vec[i]) / n for i in range(len(old_c))]
        norm  = sum(x**2 for x in new_c)**0.5 or 1.0
        c["centroid"]     = [x/norm for x in new_c]
        c["member_count"] = n

        # Update dominant components (simple mode tracking)
        c["industries"] = list(set(c.get("industries",[]) + [genome.get("industry","other")]))

        # Performance update
        if genome.get("ctr_lift") is not None:
            old_ctr = c.get("avg_ctr_lift") or 0.0
            c["avg_ctr_lift"] = round((old_ctr * (n-1) + genome["ctr_lift"]) / n, 4)
        if genome.get("cvr_lift") is not None:
            old_cvr = c.get("avg_cvr_lift") or 0.0
            c["avg_cvr_lift"] = round((old_cvr * (n-1) + genome["cvr_lift"]) / n, 4)
        if genome.get("outcome") == "win":
            c["win_count"] = c.get("win_count",0) + 1
        c["win_rate"]   = round(c.get("win_count",0) / n, 4)
        c["confidence"] = self._wilson_lower(c.get("win_count",0), n)
        c["saturation_score"] = self._saturation(c)
        c["status"]     = self._status(c)
        c["last_updated"] = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _cluster_name(genome: Dict) -> str:
        hook   = genome.get("hook_type",        "").replace("_"," ").title()
        emotion= genome.get("emotion",          "").replace("_"," ").title()
        auth   = genome.get("authority_signal", "")
        name   = f"{emotion} {hook}"
        if auth and auth != "none":
            name += f" + {auth.replace('_',' ').title()}"
        return name.strip()

    @staticmethod
    def _saturation(c: Dict) -> float:
        """Score 0–1: how saturated this cluster is."""
        size_score = min(1.0, c["member_count"] / SATURATION_MEMBER_CAP)
        # Penalise declining win rate
        wr_score   = max(0.0, 1.0 - c.get("win_rate", 0.5) * 2)
        return round(size_score * 0.65 + wr_score * 0.35, 4)

    @staticmethod
    def _status(c: Dict) -> str:
        sat  = c.get("saturation_score", 0)
        size = c["member_count"]
        wr   = c.get("win_rate", 0.5)
        if sat >= 0.75 or (size > 10 and wr < 0.30):
            return "saturated"
        if wr < 0.30 and size > 5:
            return "declining"
        if sat >= 0.50:
            return "stable"
        return "growing"

    @staticmethod
    def _wilson_lower(wins: int, n: int, z: float = 1.645) -> float:
        if n == 0: return 0.0
        phat   = wins / n
        denom  = 1 + z**2 / n
        centre = phat + z**2 / (2*n)
        spread = z * math.sqrt(max(0.0, phat*(1-phat)/n + z**2/(4*n**2)))
        return round(max(0.0, (centre - spread) / denom), 4)

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x*y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a)**0.5
        norm_b = sum(x**2 for x in b)**0.5
        return dot/(norm_a*norm_b) if norm_a and norm_b else 0.0
