"""
Embedding Engine
================
Generates sentence embeddings for competitor content and stores
them in Qdrant with structured payloads.

Embedding model: sentence-transformers/all-MiniLM-L6-v2  (local, no API cost)
Qdrant: http://localhost:6333 (from docker-compose)

Collections:
  competitor_pages  — website page chunks
  competitor_ads    — ad creative embeddings
"""

import logging
import uuid
import hashlib
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Lazy imports (heavy deps loaded only when needed) ─────────────────────

_model       = None
_qdrant      = None
_VECTOR_DIM  = 384   # all-MiniLM-L6-v2 output dimension

QDRANT_HOST        = "localhost"
QDRANT_PORT        = 6333
COLLECTION_PAGES   = "competitor_pages"
COLLECTION_ADS     = "competitor_ads"


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer loaded: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence_transformers not installed — using mock embeddings")
    return _model


def _get_qdrant():
    global _qdrant
    if _qdrant is None:
        try:
            from qdrant_client import QdrantClient
            _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=10)
            logger.info(f"Qdrant client connected: {QDRANT_HOST}:{QDRANT_PORT}")
        except Exception as exc:
            logger.warning(f"Qdrant not available: {exc}")
    return _qdrant


def _mock_vector(text: str) -> List[float]:
    """Deterministic mock vector derived from text hash (for testing without GPU/Qdrant)."""
    digest = int(hashlib.md5(text.encode()).hexdigest(), 16)
    rng = [(digest >> i & 0xFF) / 255.0 for i in range(0, _VECTOR_DIM * 8, 8)]
    # Normalise
    norm = sum(x**2 for x in rng) ** 0.5 or 1.0
    return [x / norm for x in rng]


class EmbeddingEngine:
    """Generates and stores competitor content embeddings."""

    def __init__(self):
        self._collections_ensured: set = set()

    # ── Embedding generation ─────────────────────────────────────

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings. Falls back to deterministic mock if model unavailable."""
        model = _get_model()
        if model:
            return model.encode(texts, normalize_embeddings=True).tolist()
        return [_mock_vector(t) for t in texts]

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]

    # ── Qdrant collection setup ──────────────────────────────────

    def _ensure_collection(self, name: str):
        if name in self._collections_ensured:
            return
        client = _get_qdrant()
        if client is None:
            return
        try:
            from qdrant_client.models import VectorParams, Distance
            existing = [c.name for c in client.get_collections().collections]
            if name not in existing:
                client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=_VECTOR_DIM, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {name}")
            self._collections_ensured.add(name)
        except Exception as exc:
            logger.warning(f"Qdrant collection ensure failed [{name}]: {exc}")

    # ── Upsert page chunks ───────────────────────────────────────

    def store_page_chunks(self, competitor_id: str, company_id: str,
                           chunks: List[str], metadata: Dict[str, Any]) -> List[str]:
        """
        Embed and upsert page text chunks into Qdrant.
        Returns list of point IDs stored.
        """
        if not chunks:
            return []

        vectors = self.embed(chunks)
        point_ids = []
        client = _get_qdrant()
        self._ensure_collection(COLLECTION_PAGES)

        if client:
            try:
                from qdrant_client.models import PointStruct
                points = []
                for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
                    pid = str(uuid.uuid4())
                    points.append(PointStruct(
                        id=pid,
                        vector=vec,
                        payload={
                            "competitor_id": competitor_id,
                            "company_id":    company_id,
                            "chunk_index":   i,
                            "text":          chunk[:500],   # store first 500 chars
                            **metadata
                        }
                    ))
                    point_ids.append(pid)
                client.upsert(collection_name=COLLECTION_PAGES, points=points)
                logger.info(f"Stored {len(points)} page chunks in Qdrant [{competitor_id}]")
            except Exception as exc:
                logger.warning(f"Qdrant upsert failed: {exc}")
                point_ids = [str(uuid.uuid4()) for _ in chunks]   # mock IDs
        else:
            point_ids = [str(uuid.uuid4()) for _ in chunks]

        return point_ids

    # ── Upsert ad creatives ──────────────────────────────────────

    def store_ad_creative(self, competitor_id: str, company_id: str,
                           ad: Dict[str, Any], text: str) -> str:
        """Embed and store a single ad creative. Returns point_id."""
        vector = self.embed_one(text)
        point_id = str(uuid.uuid4())
        client = _get_qdrant()
        self._ensure_collection(COLLECTION_ADS)

        if client:
            try:
                from qdrant_client.models import PointStruct
                client.upsert(
                    collection_name=COLLECTION_ADS,
                    points=[PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "competitor_id": competitor_id,
                            "company_id":    company_id,
                            "platform":      ad.get("platform", "unknown"),
                            "headline":      ad.get("headline", "")[:200],
                            "body_text":     ad.get("body_text", "")[:400],
                            "cta":           ad.get("cta", ""),
                            "offer_type":    ad.get("offer_type", ""),
                            "emotional_tone":ad.get("emotional_tone", ""),
                            "captured_at":   ad.get("captured_at", ""),
                        }
                    )]
                )
            except Exception as exc:
                logger.warning(f"Qdrant ad upsert failed: {exc}")

        return point_id

    # ── Query vectors ─────────────────────────────────────────────

    def search_similar(self, query_text: str, collection: str,
                        company_id: str, top_k: int = 20,
                        score_threshold: float = 0.60) -> List[Dict]:
        """Find similar vectors in Qdrant for a query text."""
        vec = self.embed_one(query_text)
        client = _get_qdrant()
        if client is None:
            return []
        try:
            hits = client.search(
                collection_name=collection,
                query_vector=vec,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter={
                    "must": [{"key": "company_id", "match": {"value": company_id}}]
                } if company_id else None
            )
            return [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]
        except Exception as exc:
            logger.warning(f"Qdrant search failed: {exc}")
            return []
