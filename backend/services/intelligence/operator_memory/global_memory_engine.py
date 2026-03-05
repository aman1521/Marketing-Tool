"""
Global Memory Engine — Tier 3
==============================
Anonymised platform-wide pattern aggregation.

🔒 PRIVACY GUARANTEE:
  - company_id, operator_id, campaign_id, ad_name are NEVER stored
  - Only statistical/structural attributes pass through anonymise()
  - Fingerprints are computed AFTER stripping PII
  - Global patterns improve all tenants equally with zero data leakage

Decision signals produced:
  - Cross-platform win rates per strategy / industry / AOV tier
  - Statistical significance scores
  - Emerging platform patterns not yet visible at tenant level
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import math

from .context_vectorizer import ContextVectorizer

logger = logging.getLogger(__name__)

_global_store: List[Dict] = []

QDRANT_COLLECTION = "global_memory"
MIN_CONFIDENCE_THRESHOLD = 0.65
MIN_SAMPLE_COUNT         = 5    # minimum before pattern is statistically trusted


class GlobalMemoryEngine:
    """
    Platform-wide anonymised intelligence aggregator.
    All stored data is structurally anonymised before ingestion.
    """

    def __init__(self):
        self.vectorizer = ContextVectorizer()
        self._qdrant    = None

    # ── Write (anonymise first, always) ───────────────────────────

    def ingest(self, context: Dict[str, Any], outcome: str,
               lift_delta: float, risk_exposure: float = 0.0) -> str:
        """
        Ingest an anonymised pattern into global memory.
        Caller is responsible for NOT passing PII.
        This method enforces a second-pass anonymisation as a safety net.
        """
        # Double-pass anonymisation
        anon_ctx = self.vectorizer.anonymise(context)

        # Validate no PII leaked through
        forbidden = {"company_id", "operator_id", "campaign_id", "ad_name",
                     "company_name", "operator_name", "tenant_id"}
        leaked = forbidden.intersection(set(anon_ctx.keys()))
        if leaked:
            logger.error(f"[GlobalMem] PII leak blocked: {leaked}")
            anon_ctx = {k: v for k, v in anon_ctx.items() if k not in forbidden}

        fingerprint = self.vectorizer.fingerprint(anon_ctx)
        vector      = self.vectorizer.embed(anon_ctx)

        # Check for existing pattern to aggregate (upsert logic)
        existing = self._find_by_fingerprint(fingerprint)
        if existing:
            self._aggregate(existing, outcome, lift_delta, risk_exposure)
            logger.debug(f"[GlobalMem] Aggregated into existing pattern [{fingerprint}]")
            return existing["id"]

        pattern_id = str(uuid.uuid4())
        pattern = {
            "id":              pattern_id,
            "strategy_type":   anon_ctx.get("strategy_type",  "unknown"),
            "industry_bucket": anon_ctx.get("industry_bucket","other"),
            "aov_tier":        anon_ctx.get("aov_tier",       "mid"),
            "scaling_band":    anon_ctx.get("scaling_band",   "growth"),
            "avg_lift":        lift_delta,
            "avg_risk":        risk_exposure,
            "sample_count":    1,
            "win_count":       1 if outcome == "win" else 0,
            "win_rate":        1.0 if outcome == "win" else 0.0,
            "confidence":      self._wilson_lower(1 if outcome == "win" else 0, 1),
            "fingerprint":     fingerprint,
            "vector":          vector,
            "first_seen":      datetime.utcnow().isoformat(),
            "last_updated":    datetime.utcnow().isoformat(),
        }
        _global_store.append(pattern)
        self._upsert_qdrant(pattern_id, vector, pattern)
        logger.info(f"[GlobalMem] New pattern [{fingerprint}]: {anon_ctx.get('strategy_type')}")
        return pattern_id

    # ── Read ───────────────────────────────────────────────────────

    def query_similar(self, current_context: Dict[str, Any],
                       top_k: int = 5,
                       min_confidence: float = MIN_CONFIDENCE_THRESHOLD) -> List[Dict]:
        """
        Find globally-validated patterns similar to current context.
        Only returns patterns meeting min_confidence and min_sample_count.
        """
        anon_ctx = self.vectorizer.anonymise(current_context)
        vec = self.vectorizer.to_feature_vector(anon_ctx)

        candidates = [
            p for p in _global_store
            if p["confidence"] >= min_confidence
            and p["sample_count"] >= MIN_SAMPLE_COUNT
        ]

        scored = []
        for p in candidates:
            p_vec = self.vectorizer.to_feature_vector({
                "strategy_type":   p["strategy_type"],
                "industry_bucket": p["industry_bucket"],
                "aov_tier":        p["aov_tier"],
                "scaling_band":    p["scaling_band"],
            })
            sim = self._cosine(vec, p_vec)
            scored.append({**p, "similarity": round(sim, 4)})

        scored.sort(key=lambda x: (-x["similarity"], -x["confidence"]))
        return [{k: v for k, v in p.items() if k != "vector"} for p in scored[:top_k]]

    def get_global_stats(self) -> Dict[str, Any]:
        """High-level platform statistics."""
        if not _global_store:
            return {"total_patterns": 0, "total_sample_count": 0}

        total = len(_global_store)
        samples = sum(p["sample_count"] for p in _global_store)
        trusted = [p for p in _global_store if p["sample_count"] >= MIN_SAMPLE_COUNT]
        avg_win = sum(p["win_rate"] for p in trusted) / len(trusted) if trusted else 0

        by_strategy = defaultdict(list)
        for p in _global_store:
            by_strategy[p["strategy_type"]].append(p["win_rate"])
        strategy_win_rates = {
            k: round(sum(v) / len(v), 4) for k, v in by_strategy.items()
        }

        return {
            "total_patterns":     total,
            "total_sample_count": samples,
            "trusted_patterns":   len(trusted),
            "avg_win_rate":       round(avg_win, 4),
            "strategy_win_rates": strategy_win_rates,
        }

    # ── Internal ───────────────────────────────────────────────────

    def _find_by_fingerprint(self, fingerprint: str) -> Optional[Dict]:
        for p in _global_store:
            if p["fingerprint"] == fingerprint:
                return p
        return None

    def _aggregate(self, pattern: Dict, outcome: str,
                    lift_delta: float, risk_exposure: float):
        """Running Welford average update."""
        n = pattern["sample_count"] + 1
        pattern["avg_lift"]  = round(
            (pattern["avg_lift"] * pattern["sample_count"] + lift_delta) / n, 4
        )
        pattern["avg_risk"]  = round(
            (pattern["avg_risk"] * pattern["sample_count"] + risk_exposure) / n, 4
        )
        if outcome == "win":
            pattern["win_count"] += 1
        pattern["sample_count"] = n
        pattern["win_rate"]  = round(pattern["win_count"] / n, 4)
        pattern["confidence"]= self._wilson_lower(pattern["win_count"], n)
        pattern["last_updated"] = datetime.utcnow().isoformat()

    @staticmethod
    def _wilson_lower(wins: int, n: int, z: float = 1.645) -> float:
        """Wilson score lower bound — conservative confidence estimate."""
        if n == 0:
            return 0.0
        phat = wins / n
        denom = 1 + z**2 / n
        centre = phat + z**2 / (2 * n)
        spread = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
        return round(max(0.0, (centre - spread) / denom), 4)

    # ── Qdrant ──────────────────────────────────────────────────────

    def _upsert_qdrant(self, point_id: str, vector: List[float], payload: Dict):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import PointStruct, VectorParams, Distance
            if self._qdrant is None:
                self._qdrant = QdrantClient(host="localhost", port=6333, timeout=5)
                colls = [c.name for c in self._qdrant.get_collections().collections]
                if QDRANT_COLLECTION not in colls:
                    self._qdrant.create_collection(
                        collection_name=QDRANT_COLLECTION,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
            safe = {k: v for k, v in payload.items() if k not in ("vector",)}
            self._qdrant.upsert(
                collection_name=QDRANT_COLLECTION,
                points=[PointStruct(id=point_id, vector=vector, payload=safe)]
            )
        except Exception as exc:
            logger.debug(f"Qdrant unavailable (global): {exc}")

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
