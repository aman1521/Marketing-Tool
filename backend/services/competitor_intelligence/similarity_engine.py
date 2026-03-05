"""
Similarity Engine
=================
Detects messaging similarity clusters across competitor content
using cosine similarity on stored embeddings.

Outputs:
  - Cluster definitions with themes and saturation scores
  - Creative saturation index per theme
  - Signals consumable by MarketPressureDetector
"""

import logging
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

from .embedding_engine import EmbeddingEngine, COLLECTION_ADS, COLLECTION_PAGES

logger = logging.getLogger(__name__)

# Similarity thresholds
CLUSTER_THRESHOLD     = 0.72   # min cosine similarity to join a cluster
SATURATION_THRESHOLD  = 0.80   # cluster is "saturated" if avg similarity > this
MIN_CLUSTER_SIZE      = 2      # min items to constitute a real cluster


class SimilarityEngine:
    """
    Detects creative similarity clusters and saturation.
    Operates purely on embeddings — no direct DB writes.
    Produces cluster signals for downstream engines.
    """

    def __init__(self):
        self.embedding_engine = EmbeddingEngine()

    # ── Pairwise cosine similarity (no scipy dependency) ─────────

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        dot    = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # ── Greedy clustering ─────────────────────────────────────────

    def cluster_texts(self, texts: List[str],
                      threshold: float = CLUSTER_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Greedy single-pass clustering by cosine similarity.
        Fast O(n²) suitable for competitor intelligence volumes (<1000 items).
        Returns list of cluster dicts.
        """
        if not texts:
            return []

        vectors    = self.embedding_engine.embed(texts)
        n          = len(texts)
        assigned   = [-1] * n
        clusters   = []

        for i in range(n):
            if assigned[i] != -1:
                continue
            cid = len(clusters)
            assigned[i] = cid
            members = [i]

            for j in range(i + 1, n):
                if assigned[j] != -1:
                    continue
                sim = self.cosine_similarity(vectors[i], vectors[j])
                if sim >= threshold:
                    assigned[j] = cid
                    members.append(j)

            # Compute intra-cluster avg similarity
            sims = []
            for a in members:
                for b in members:
                    if a < b:
                        sims.append(self.cosine_similarity(vectors[a], vectors[b]))
            avg_sim = sum(sims) / len(sims) if sims else 1.0

            clusters.append({
                "cluster_id":    cid,
                "members":       [texts[m][:120] for m in members],
                "member_count":  len(members),
                "avg_similarity": round(avg_sim, 4),
                "saturation_score": round(min(1.0, avg_sim * len(members) / max(1, n) * 3), 4),
                "theme":         self._infer_theme([texts[m] for m in members]),
                "is_saturated":  avg_sim >= SATURATION_THRESHOLD and len(members) >= MIN_CLUSTER_SIZE
            })

        # Filter trivial single-item clusters
        real = [c for c in clusters if c["member_count"] >= MIN_CLUSTER_SIZE]
        real.sort(key=lambda c: c["saturation_score"], reverse=True)
        return real

    # ── Theme inference ───────────────────────────────────────────

    def _infer_theme(self, texts: List[str]) -> str:
        """Heuristic theme label from frequent keywords."""
        combined = " ".join(texts).lower()
        theme_kw = {
            "free_trial":    ["free trial", "no credit card", "try free"],
            "pricing":       ["pricing", "per month", "per seat", "plan", "cost"],
            "trust_social":  ["trusted", "customers", "reviews", "rated", "#1", "award"],
            "speed_perf":    ["fast", "10x", "instantly", "real-time", "speed", "automate"],
            "enterprise":    ["enterprise", "compliance", "security", "scale", "sso"],
            "comparison":    ["vs", "versus", "compare", "better than", "switch"],
            "education":     ["learn", "guide", "how to", "resource", "webinar", "blog"],
        }
        scores = {theme: sum(1 for kw in kws if kw in combined) for theme, kws in theme_kw.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "general_messaging"

    # ── Ad cluster analysis ───────────────────────────────────────

    def analyze_ad_clusters(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Given a list of ad creative dicts from the capture engine,
        run clustering and return cluster intelligence.
        """
        texts = []
        for ad in ads:
            parts = [ad.get("headline",""), ad.get("body_text",""), ad.get("cta","")]
            texts.append(" | ".join(p for p in parts if p))

        if not texts:
            return {"clusters": [], "saturation_index": 0.0, "dominant_theme": "none"}

        clusters = self.cluster_texts(texts)
        total_saturated = sum(1 for c in clusters if c["is_saturated"])
        saturation_index = total_saturated / max(1, len(clusters))
        dominant = clusters[0]["theme"] if clusters else "none"

        return {
            "clusters":         clusters,
            "cluster_count":    len(clusters),
            "saturated_count":  total_saturated,
            "saturation_index": round(saturation_index, 4),
            "dominant_theme":   dominant,
        }

    # ── Website similarity queries (Qdrant-backed) ────────────────

    def find_similar_pages(self, query: str, company_id: str,
                            top_k: int = 10) -> List[Dict]:
        """Find competitor pages similar to a given query text."""
        return self.embedding_engine.search_similar(
            query_text=query,
            collection=COLLECTION_PAGES,
            company_id=company_id,
            top_k=top_k
        )

    def find_similar_ads(self, query: str, company_id: str,
                          top_k: int = 10) -> List[Dict]:
        """Find competitor ads similar to a given creative brief."""
        return self.embedding_engine.search_similar(
            query_text=query,
            collection=COLLECTION_ADS,
            company_id=company_id,
            top_k=top_k
        )
