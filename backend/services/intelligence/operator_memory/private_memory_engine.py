"""
Private Memory Engine — Tier 1
================================
Full-fidelity operator-private strategy learning.
Only the owning operator can read their own memory.
Stores complete context, action, and outcome at event resolution.

Decision signals produced:
  - Most successful past strategies in this exact signal context
  - Operator-specific risk preferences
  - Historical lift distribution for proposed action
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from .context_vectorizer import ContextVectorizer

logger = logging.getLogger(__name__)

# In-memory store (replace with DB session in production)
_store: List[Dict] = []

QDRANT_COLLECTION = "private_memory"
MIN_OUTCOME_CONFIDENCE = 0.60


class PrivateMemoryEngine:
    """
    Operator-private strategy memory.
    All reads are gated by operator_id.
    """

    def __init__(self):
        self.vectorizer = ContextVectorizer()
        self._qdrant    = None    # lazy init

    # ── Write ──────────────────────────────────────────────────────

    def record_event(self, operator_id: str, company_id: str,
                     strategy_type: str, context: Dict[str, Any],
                     action_taken: Dict[str, Any]) -> str:
        """Record a new strategy execution event. Outcome resolved later."""
        event_id = str(uuid.uuid4())
        vector   = self.vectorizer.embed(context)
        fingerprint = self.vectorizer.fingerprint(context)

        event = {
            "id":           event_id,
            "operator_id":  operator_id,
            "company_id":   company_id,
            "strategy_type": strategy_type,
            "context":      context,
            "action_taken": action_taken,
            "outcome":      "pending",
            "lift_delta":   None,
            "risk_exposure":context.get("risk_exposure", 0.0),
            "confidence_at":context.get("confidence_avg", 0.0),
            "volatility_at":context.get("volatility_index", 0.0),
            "fingerprint":  fingerprint,
            "vector":       vector,
            "created_at":   datetime.utcnow().isoformat(),
            "resolved_at":  None,
        }
        _store.append(event)
        self._upsert_qdrant(event_id, vector, event)
        logger.info(f"[PrivateMem] Recorded event [{event_id}] op=[{operator_id}]")
        return event_id

    def resolve_event(self, event_id: str, operator_id: str,
                       outcome: str, lift_delta: float):
        """Resolve outcome of a previously recorded event."""
        for e in _store:
            if e["id"] == event_id and e["operator_id"] == operator_id:
                e["outcome"]     = outcome
                e["lift_delta"]  = lift_delta
                e["resolved_at"] = datetime.utcnow().isoformat()
                logger.info(f"[PrivateMem] Resolved [{event_id}] → {outcome} lift={lift_delta:+.2%}")
                return True
        logger.warning(f"[PrivateMem] Event not found or access denied: {event_id}")
        return False

    # ── Read ───────────────────────────────────────────────────────

    def query_similar(self, operator_id: str, current_context: Dict[str, Any],
                       top_k: int = 5, min_similarity: float = 0.70) -> List[Dict]:
        """
        Find the most similar past strategy events for this operator.
        Returns only resolved WIN events for positive signal.
        """
        vec = self.vectorizer.to_feature_vector(current_context)

        wins = [
            e for e in _store
            if e["operator_id"] == operator_id
            and e["outcome"] == "win"
            and e["lift_delta"] is not None
        ]

        scored = []
        for e in wins:
            e_vec = self.vectorizer.to_feature_vector(e["context"])
            sim   = self._cosine(vec, e_vec)
            if sim >= min_similarity:
                scored.append({**e, "similarity": round(sim, 4)})

        scored.sort(key=lambda x: (-x["similarity"], -(x["lift_delta"] or 0)))
        return scored[:top_k]

    def get_operator_lift_stats(self, operator_id: str,
                                 strategy_type: str) -> Dict[str, Any]:
        """Stats on past lift for a specific strategy type."""
        events = [
            e for e in _store
            if e["operator_id"] == operator_id
            and e["strategy_type"] == strategy_type
            and e["lift_delta"] is not None
        ]
        if not events:
            return {"sample_count": 0, "avg_lift": 0.0, "win_rate": 0.0, "avg_risk": 0.0}

        lifts = [e["lift_delta"] for e in events]
        risks = [e.get("risk_exposure", 0.0) for e in events]
        wins  = [e for e in events if e["outcome"] == "win"]
        return {
            "sample_count": len(events),
            "avg_lift":     round(sum(lifts) / len(lifts), 4),
            "win_rate":     round(len(wins) / len(events), 4),
            "avg_risk":     round(sum(risks) / len(risks), 4),
            "max_lift":     round(max(lifts), 4),
        }

    def get_operator_events(self, operator_id: str, limit: int = 50) -> List[Dict]:
        """Return all events for an operator (most recent first)."""
        evts = [e for e in _store if e["operator_id"] == operator_id]
        return sorted(evts, key=lambda e: e["created_at"], reverse=True)[:limit]

    # ── Qdrant integration ─────────────────────────────────────────

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
            safe = {k: v for k, v in payload.items() if k not in ("vector", "context", "action_taken")}
            self._qdrant.upsert(
                collection_name=QDRANT_COLLECTION,
                points=[PointStruct(id=point_id, vector=vector, payload=safe)]
            )
        except Exception as exc:
            logger.debug(f"Qdrant unavailable (private): {exc}")

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
