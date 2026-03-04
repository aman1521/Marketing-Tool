"""
Tenant Memory Engine — Tier 2
==============================
Company-level intelligence learning.
Tracks which strategy types work for this specific company
given its industry, AOV, and scaling band.

Isolation: reads are strictly scoped to company_id.
No cross-tenant reads are possible.

Decision signals produced:
  - Company-specific strategy win rates
  - Context-pattern success frequencies
  - Archetype linkage for top patterns
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .context_vectorizer import ContextVectorizer

logger = logging.getLogger(__name__)

_store: List[Dict] = []

QDRANT_COLLECTION = "tenant_memory"


class TenantMemoryEngine:
    """Company-scoped strategy intelligence. Hard tenant isolation."""

    def __init__(self):
        self.vectorizer = ContextVectorizer()
        self._qdrant    = None

    # ── Write ──────────────────────────────────────────────────────

    def record_event(self, company_id: str, strategy_type: str,
                     context: Dict[str, Any], outcome: str = "pending",
                     lift_delta: Optional[float] = None) -> str:
        """Record a strategy event for a tenant."""
        event_id    = str(uuid.uuid4())
        fingerprint = self.vectorizer.fingerprint(context)
        vector      = self.vectorizer.embed(context)

        # Strip any PII-adjacent operator data
        safe_ctx = {k: v for k, v in context.items()
                    if k not in ("operator_id", "campaign_id", "ad_name")}

        event = {
            "id":             event_id,
            "company_id":     company_id,
            "strategy_type":  strategy_type,
            "industry":       context.get("industry_bucket", "other"),
            "aov_tier":       context.get("aov_tier", "mid"),
            "scaling_band":   context.get("scaling_band", "growth"),
            "context":        safe_ctx,
            "outcome":        outcome,
            "lift_delta":     lift_delta,
            "risk_exposure":  context.get("risk_exposure", 0.0),
            "success_signal": lift_delta is not None and lift_delta > 0.05,
            "fingerprint":    fingerprint,
            "archetype_id":   None,
            "vector":         vector,
            "created_at":     datetime.utcnow().isoformat(),
        }
        _store.append(event)
        self._upsert_qdrant(event_id, vector, event)
        logger.info(f"[TenantMem] Event [{event_id}] company=[{company_id}] type=[{strategy_type}]")
        return event_id

    def link_archetype(self, event_id: str, archetype_id: str):
        """Link an event to a detected archetype."""
        for e in _store:
            if e["id"] == event_id:
                e["archetype_id"] = archetype_id
                return

    # ── Read (strictly company-scoped) ─────────────────────────────

    def query_similar(self, company_id: str, current_context: Dict[str, Any],
                       top_k: int = 8, outcome_filter: str = "win") -> List[Dict]:
        """Find similar historical events for this tenant."""
        vec = self.vectorizer.to_feature_vector(current_context)

        candidates = [
            e for e in _store
            if e["company_id"] == company_id
            and (outcome_filter is None or e["outcome"] == outcome_filter)
            and e["lift_delta"] is not None
        ]

        scored = []
        for e in candidates:
            e_vec = self.vectorizer.to_feature_vector(e["context"])
            sim   = self._cosine(vec, e_vec)
            scored.append({**e, "similarity": round(sim, 4)})

        scored.sort(key=lambda x: (-x["similarity"], -(x["lift_delta"] or 0)))
        return scored[:top_k]

    def get_strategy_stats(self, company_id: str) -> Dict[str, Any]:
        """Per-strategy-type win rates for this tenant."""
        events = [e for e in _store if e["company_id"] == company_id and e["lift_delta"] is not None]
        grouped = defaultdict(list)
        for e in events:
            grouped[e["strategy_type"]].append(e)

        stats = {}
        for stype, evts in grouped.items():
            lifts = [e["lift_delta"] for e in evts]
            wins  = [e for e in evts if e["outcome"] == "win"]
            stats[stype] = {
                "sample_count": len(evts),
                "win_rate":     round(len(wins) / len(evts), 4),
                "avg_lift":     round(sum(lifts) / len(lifts), 4),
            }
        return stats

    def get_repeating_patterns(self, company_id: str,
                                min_occurrences: int = 3) -> List[Dict]:
        """
        Find fingerprint patterns that appear >= min_occurrences times
        with positive outcomes.
        """
        events = [
            e for e in _store
            if e["company_id"] == company_id
            and e["outcome"] == "win"
            and e["lift_delta"] is not None
        ]

        by_fingerprint = defaultdict(list)
        for e in events:
            by_fingerprint[e["fingerprint"]].append(e)

        patterns = []
        for fp, evts in by_fingerprint.items():
            if len(evts) >= min_occurrences:
                lifts = [e["lift_delta"] for e in evts]
                patterns.append({
                    "fingerprint":      fp,
                    "occurrences":      len(evts),
                    "avg_lift":         round(sum(lifts) / len(lifts), 4),
                    "strategy_type":    evts[0]["strategy_type"],
                    "industry":         evts[0]["industry"],
                    "aov_tier":         evts[0]["aov_tier"],
                    "scaling_band":     evts[0]["scaling_band"],
                    "sample_events":    [e["id"] for e in evts[:3]],
                })

        patterns.sort(key=lambda p: (-p["occurrences"], -p["avg_lift"]))
        return patterns

    def get_company_events(self, company_id: str, limit: int = 100) -> List[Dict]:
        evts = [e for e in _store if e["company_id"] == company_id]
        return sorted(evts, key=lambda e: e["created_at"], reverse=True)[:limit]

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
            safe = {k: v for k, v in payload.items() if k not in ("vector", "context")}
            self._qdrant.upsert(
                collection_name=QDRANT_COLLECTION,
                points=[PointStruct(id=point_id, vector=vector, payload=safe)]
            )
        except Exception as exc:
            logger.debug(f"Qdrant unavailable (tenant): {exc}")

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
