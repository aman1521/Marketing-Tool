"""
PGIL Vector Store
=================
Manages all Qdrant operations for the Private Global Intelligence Layer.

Collections:
  pgil_events    — individual anonymised event embeddings
  pgil_patterns  — aggregated pattern centroids
  pgil_archetypes — high-confidence archetype embeddings

All payloads stored in Qdrant are pre-validated through PGILCollector
so this store only receives clean, anonymised data.

Namespace isolation: all collections prefixed pgil_* to prevent
cross-collection contamination with other platform vector stores.
"""

import hashlib
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

VECTOR_DIM = 384

COLLECTION_EVENTS    = "pgil_events"
COLLECTION_PATTERNS  = "pgil_patterns"
COLLECTION_ARCHETYPES= "pgil_archetypes"

_ALL_COLLECTIONS = [COLLECTION_EVENTS, COLLECTION_PATTERNS, COLLECTION_ARCHETYPES]

# Categorical encodings for structured feature vectors
_STRATEGIES = [
    "scale_budget","reduce_budget","pause","creative_refresh",
    "audience_expansion","bid_adjustment","test_new_platform",
    "retarget","seasonal_push","default"
]
_INDUSTRIES   = ["ecommerce","saas","fintech","health","agency","other"]
_CLUSTERS     = ["trial","discount","premium","trust","education","comparison","urgency","other"]
_FUNNELS      = ["tofu","mofu","bofu","retention"]
_VOLATILITY   = ["low","medium","high","extreme"]
_SCALING      = ["micro","growth","scale","enterprise"]
_OUTCOMES     = ["win","loss","neutral","pending"]
_DRIFT        = ["low","medium","high"]
_CONFIDENCE   = ["low","medium","high"]
_ROI_DIR      = ["up","flat","down"]
_ESCALATION   = ["none","low","high"]


def _oh(value: str, options: List[str]) -> List[float]:
    return [1.0 if value == o else 0.0 for o in options]


def _mock_vector(text: str) -> List[float]:
    digest = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    vec = [(digest >> (i * 8) & 0xFF) / 255.0 for i in range(VECTOR_DIM)]
    norm = sum(x**2 for x in vec)**0.5 or 1.0
    return [x/norm for x in vec]


class PGILVectorStore:
    """
    Qdrant interface for all PGIL vector operations.
    Gracefully degrades to mock mode if Qdrant is unavailable.
    """

    def __init__(self):
        self._client          = None
        self._mock_mode       = False
        self._mock_store: Dict[str, List[Dict]] = {c: [] for c in _ALL_COLLECTIONS}
        self._ensured: set    = set()
        self._try_connect()

    # ── Connection ───────────────────────────────────────────────────────

    def _try_connect(self):
        try:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host="localhost", port=6333, timeout=5)
            self._client.get_collections()   # ping
            logger.info("[PGIL VectorStore] Connected to Qdrant")
        except Exception as exc:
            logger.warning(f"[PGIL VectorStore] Qdrant unavailable — mock mode active: {exc}")
            self._mock_mode = True

    def _ensure_collection(self, name: str):
        if name in self._ensured or self._mock_mode:
            return
        try:
            from qdrant_client.models import VectorParams, Distance
            existing = [c.name for c in self._client.get_collections().collections]
            if name not in existing:
                self._client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
                )
                logger.info(f"[PGIL VectorStore] Created collection: {name}")
            self._ensured.add(name)
        except Exception as exc:
            logger.warning(f"[PGIL VectorStore] Collection ensure failed [{name}]: {exc}")

    # ── Embedding ────────────────────────────────────────────────────────

    def embed(self, event: Dict[str, Any]) -> List[float]:
        """Generate embedding from anonymised event dict."""
        try:
            from sentence_transformers import SentenceTransformer
            text = self._to_text(event)
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model.encode([text], normalize_embeddings=True)[0].tolist()
        except ImportError:
            return self.feature_vector(event)

    def feature_vector(self, event: Dict[str, Any]) -> List[float]:
        """
        Deterministic 384-dim feature vector from categorical + float fields.
        Pads to VECTOR_DIM with zeros for compatibility.
        """
        vec: List[float] = []
        vec.extend(_oh(event.get("strategy_type",    "default"),  _STRATEGIES))
        vec.extend(_oh(event.get("industry_bucket",  "other"),    _INDUSTRIES))
        vec.extend(_oh(event.get("creative_cluster", "other"),    _CLUSTERS))
        vec.extend(_oh(event.get("funnel_stage",     "mofu"),     _FUNNELS))
        vec.extend(_oh(event.get("volatility_band",  "medium"),   _VOLATILITY))
        vec.extend(_oh(event.get("scaling_band",     "growth"),   _SCALING))
        vec.extend(_oh(event.get("outcome",          "pending"),  _OUTCOMES))
        vec.extend(_oh(event.get("drift_bucket",     "medium"),   _DRIFT))
        vec.extend(_oh(event.get("confidence_bucket","medium"),   _CONFIDENCE))
        vec.extend(_oh(event.get("roi_direction",    "flat"),     _ROI_DIR))
        vec.extend(_oh(event.get("escalation_level", "none"),     _ESCALATION))
        # Numeric lift/risk (normalised)
        vec.append(max(0.0, min(1.0, (float(event.get("lift_delta", 0.0)) + 1.0) / 3.0)))
        vec.append(max(0.0, min(1.0, float(event.get("risk_score", 0.0)))))
        # Pad to VECTOR_DIM
        while len(vec) < VECTOR_DIM:
            vec.append(0.0)
        vec = vec[:VECTOR_DIM]
        # Normalise
        norm = sum(x**2 for x in vec)**0.5 or 1.0
        return [x/norm for x in vec]

    # ── Upsert operations ────────────────────────────────────────────────

    def upsert_event(self, event: Dict[str, Any]) -> str:
        point_id = str(uuid.uuid4())
        vector   = self.embed(event)
        payload  = {k: v for k, v in event.items()
                    if k not in ("collected_at",) and v is not None}
        self._upsert(COLLECTION_EVENTS, point_id, vector, payload)
        return point_id

    def upsert_pattern(self, pattern: Dict[str, Any]) -> str:
        point_id = pattern.get("id", str(uuid.uuid4()))
        vector   = self.embed(pattern)
        payload  = {k: v for k, v in pattern.items()
                    if k not in ("first_seen", "last_updated")}
        self._upsert(COLLECTION_PATTERNS, point_id, vector, payload)
        return point_id

    def upsert_archetype(self, archetype: Dict[str, Any]) -> str:
        point_id = archetype.get("id", str(uuid.uuid4()))
        vector   = self.embed(archetype)
        payload  = {k: v for k, v in archetype.items()
                    if k not in ("created_at", "last_updated", "pattern_ids")}
        self._upsert(COLLECTION_ARCHETYPES, point_id, vector, payload)
        return point_id

    # ── Search operations ────────────────────────────────────────────────

    def search_similar_events(self, query: Dict[str, Any],
                               top_k: int = 20,
                               score_threshold: float = 0.62) -> List[Dict]:
        return self._search(COLLECTION_EVENTS, query, top_k, score_threshold)

    def search_similar_patterns(self, query: Dict[str, Any],
                                 top_k: int = 10,
                                 score_threshold: float = 0.70) -> List[Dict]:
        return self._search(COLLECTION_PATTERNS, query, top_k, score_threshold)

    def search_matching_archetypes(self, query: Dict[str, Any],
                                    top_k: int = 5,
                                    score_threshold: float = 0.70) -> List[Dict]:
        return self._search(COLLECTION_ARCHETYPES, query, top_k, score_threshold)

    # ── Collection stats ────────────────────────────────────────────────

    def collection_info(self) -> Dict[str, Any]:
        if self._mock_mode:
            return {c: len(self._mock_store[c]) for c in _ALL_COLLECTIONS}
        try:
            info = {}
            for name in _ALL_COLLECTIONS:
                try:
                    col = self._client.get_collection(name)
                    info[name] = col.vectors_count
                except Exception:
                    info[name] = 0
            return info
        except Exception as exc:
            return {"error": str(exc)}

    # ── Internals ────────────────────────────────────────────────────────

    def _upsert(self, collection: str, point_id: str,
                 vector: List[float], payload: Dict):
        if self._mock_mode:
            # Remove existing point with same ID
            self._mock_store[collection] = [
                p for p in self._mock_store[collection] if p["id"] != point_id
            ]
            self._mock_store[collection].append({
                "id": point_id, "vector": vector, "payload": payload
            })
            return
        try:
            from qdrant_client.models import PointStruct
            self._ensure_collection(collection)
            self._client.upsert(
                collection_name=collection,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)]
            )
        except Exception as exc:
            logger.debug(f"[PGIL VectorStore] Upsert failed [{collection}]: {exc}")

    def _search(self, collection: str, query: Dict,
                 top_k: int, score_threshold: float) -> List[Dict]:
        vec = self.embed(query)
        if self._mock_mode:
            return self._mock_search(collection, vec, top_k, score_threshold)
        try:
            hits = self._client.search(
                collection_name=collection,
                query_vector=vec,
                limit=top_k,
                score_threshold=score_threshold,
            )
            return [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]
        except Exception as exc:
            logger.debug(f"[PGIL VectorStore] Search failed [{collection}]: {exc}")
            return self._mock_search(collection, vec, top_k, score_threshold)

    def _mock_search(self, collection: str, query_vec: List[float],
                      top_k: int, threshold: float) -> List[Dict]:
        results = []
        for pt in self._mock_store[collection]:
            sim = self._cosine(query_vec, pt["vector"])
            if sim >= threshold:
                results.append({"id": pt["id"], "score": sim, "payload": pt["payload"]})
        results.sort(key=lambda x: -x["score"])
        return results[:top_k]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x*y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a)**0.5
        norm_b = sum(x**2 for x in b)**0.5
        return dot/(norm_a*norm_b) if norm_a and norm_b else 0.0

    @staticmethod
    def _to_text(event: Dict) -> str:
        return (
            f"strategy:{event.get('strategy_type','?')} "
            f"industry:{event.get('industry_bucket','?')} "
            f"cluster:{event.get('creative_cluster','?')} "
            f"funnel:{event.get('funnel_stage','?')} "
            f"volatility:{event.get('volatility_band','?')} "
            f"scaling:{event.get('scaling_band','?')} "
            f"outcome:{event.get('outcome','?')} "
            f"lift:{event.get('lift_delta',0.0):.3f} "
            f"risk:{event.get('risk_score',0.0):.3f}"
        )
