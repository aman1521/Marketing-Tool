"""
Genome Vectorizer
=================
Converts a CreativeGenome dict into a 384-dim vector embedding
for Qdrant storage and similarity search.

Two embedding strategies:
  1. Feature vector (categorical one-hots + float fields) — deterministic, 384-dim
  2. SentenceTransformer on descriptive text — semantic, 384-dim (if available)

Both strategies are combined (avg) when both are available.

Qdrant collection: creative_genomes
"""

import hashlib
import logging
import uuid
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

VECTOR_DIM    = 384
COLLECTION    = "creative_genomes"
ARCH_COLLECTION = "creative_archetypes"

# ── Categorical encodings ─────────────────────────────────────────────────
_HOOKS      = ["problem_agitation","curiosity","authority","story","shock",
               "question","bold_claim","pattern_interrupt","unknown"]
_EMOTIONS   = ["urgency","fear","joy","trust","curiosity","pride",
               "guilt","excitement","aspirational","neutral"]
_AUTHORITY  = ["expert","celebrity","social_proof","data_stats",
               "award","media_logo","testimonial","none"]
_OFFERS     = ["discount","trial","demo","bundle","guarantee","gift","exclusivity","direct"]
_CTAS       = ["direct_command","soft_invite","question","scarcity","benefit_lead","social"]
_PACING     = ["fast","medium","slow","varied"]
_STRUCTURES = ["pain_solution_proof","hook_story_offer_cta","problem_agit_solution",
               "before_after_bridge","features_benefits_cta","testimonial_proof",
               "curiosity_reveal","direct_offer","unknown"]
_TECHNIQUES = ["scarcity","authority","social_proof","reciprocity","commitment",
               "liking","fear_fomo","curiosity","novelty","loss_aversion"]


def _oh(value: str, vocab: List[str]) -> List[float]:
    return [1.0 if value == v else 0.0 for v in vocab]


def _mock_vec(text: str) -> List[float]:
    digest = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    raw    = [(digest >> (i * 8) & 0xFF) / 255.0 for i in range(VECTOR_DIM)]
    norm   = sum(x**2 for x in raw) ** 0.5 or 1.0
    return [x / norm for x in raw]


class GenomeVectorizer:
    """
    Converts a full creative genome into a 384-dim embedding.
    Stores in Qdrant with structured payload.
    """

    def __init__(self):
        self._qdrant = None
        self._model  = None
        self._ensured: set = set()

    # ── Embedding ─────────────────────────────────────────────────────────

    def embed(self, genome: Dict[str, Any]) -> List[float]:
        """Embed genome. Falls back to feature vector if no model."""
        feat_vec = self.feature_vector(genome)
        try:
            sem_vec = self._semantic_vector(genome)
            # Blend 50/50
            blended = [(f + s) / 2 for f, s in zip(feat_vec, sem_vec)]
            norm    = sum(x**2 for x in blended) ** 0.5 or 1.0
            return [x / norm for x in blended]
        except Exception:
            return feat_vec

    def feature_vector(self, genome: Dict[str, Any]) -> List[float]:
        """
        Deterministic 384-dim feature vector from genome components.
        Layout:
          9  hook OH
          10 emotion OH
          8  authority OH
          8  offer OH
          6  CTA OH
          4  pacing OH
          9  structure OH
          10 persuasion techniques OH (multi-hot)
          2  performance floats (ctr_lift, cvr_lift normalised)
          --- total 66 categorical + 2 float = 68, padded to 384
        """
        vec: List[float] = []
        vec.extend(_oh(genome.get("hook_type",        "unknown"),       _HOOKS))
        vec.extend(_oh(genome.get("emotion",          "neutral"),       _EMOTIONS))
        vec.extend(_oh(genome.get("authority_signal", "none"),          _AUTHORITY))
        vec.extend(_oh(genome.get("offer_type",       "direct"),        _OFFERS))
        vec.extend(_oh(genome.get("cta_style",        "direct_command"),_CTAS))
        vec.extend(_oh(genome.get("pacing",           "medium"),        _PACING))
        vec.extend(_oh(genome.get("structure",        "unknown"),       _STRUCTURES))
        # Multi-hot persuasion techniques
        techs = set(genome.get("persuasion_techniques", []))
        vec.extend([1.0 if t in techs else 0.0 for t in _TECHNIQUES])
        # Performance floats
        vec.append(max(0.0, min(1.0, (float(genome.get("ctr_lift", 0.0)) + 1) / 3)))
        vec.append(max(0.0, min(1.0, float(genome.get("cvr_lift", 0.0)))))
        # Pad to VECTOR_DIM
        while len(vec) < VECTOR_DIM:
            vec.append(0.0)
        vec = vec[:VECTOR_DIM]
        norm = sum(x**2 for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]

    def embed_batch(self, genomes: List[Dict]) -> List[List[float]]:
        return [self.embed(g) for g in genomes]

    # ── Qdrant storage ────────────────────────────────────────────────────

    def store(self, genome: Dict[str, Any], company_id: str = "",
               creative_id: str = "") -> str:
        """Embed genome and upsert to Qdrant. Returns point_id."""
        point_id = creative_id or str(uuid.uuid4())
        vector   = self.embed(genome)
        payload  = {
            "creative_id":      creative_id,
            "company_id":       company_id,
            "hook_type":        genome.get("hook_type"),
            "emotion":          genome.get("emotion"),
            "authority_signal": genome.get("authority_signal"),
            "offer_type":       genome.get("offer_type"),
            "cta_style":        genome.get("cta_style"),
            "pacing":           genome.get("pacing"),
            "structure":        genome.get("structure"),
            "persuasion_techniques": genome.get("persuasion_techniques", []),
            "ctr_lift":         genome.get("ctr_lift"),
            "cvr_lift":         genome.get("cvr_lift"),
            "outcome":          genome.get("outcome"),
        }
        self._upsert(COLLECTION, point_id, vector, payload)
        logger.info(f"[GenomeVectorizer] Stored genome [{point_id}] hook={genome.get('hook_type')}")
        return point_id

    def store_archetype(self, archetype: Dict[str, Any]) -> str:
        point_id = archetype.get("id", str(uuid.uuid4()))
        vector   = self.embed(archetype)
        payload  = {k: v for k, v in archetype.items()
                    if k not in ("created_at","last_updated","industry_fit")}
        self._upsert(ARCH_COLLECTION, point_id, vector, payload)
        return point_id

    def search_similar(self, genome: Dict[str, Any],
                        top_k: int = 10,
                        score_threshold: float = 0.68) -> List[Dict]:
        """Find creatives with similar genetic profiles."""
        vec = self.embed(genome)
        client = self._get_qdrant()
        if client is None:
            return []
        try:
            hits = client.search(
                collection_name=COLLECTION,
                query_vector=vec,
                limit=top_k,
                score_threshold=score_threshold,
            )
            return [{"id": h.id, "score": round(h.score, 4), "payload": h.payload}
                    for h in hits]
        except Exception as exc:
            logger.debug(f"[GenomeVectorizer] Search failed: {exc}")
            return []

    def fingerprint(self, genome: Dict[str, Any]) -> str:
        key = ":".join([
            genome.get("hook_type",        "?"),
            genome.get("emotion",          "?"),
            genome.get("authority_signal", "?"),
            genome.get("offer_type",       "?"),
            genome.get("cta_style",        "?"),
            genome.get("structure",        "?"),
        ])
        return hashlib.md5(key.encode()).hexdigest()[:16]

    # ── Qdrant internals ─────────────────────────────────────────────────

    def _get_qdrant(self):
        if self._qdrant is not None:
            return self._qdrant
        try:
            from qdrant_client import QdrantClient
            self._qdrant = QdrantClient(host="localhost", port=6333, timeout=5)
            return self._qdrant
        except Exception:
            return None

    def _ensure_collection(self, name: str, size: int):
        if name in self._ensured:
            return
        client = self._get_qdrant()
        if client is None:
            return
        try:
            from qdrant_client.models import VectorParams, Distance
            cols = [c.name for c in client.get_collections().collections]
            if name not in cols:
                client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=size, distance=Distance.COSINE)
                )
            self._ensured.add(name)
        except Exception as exc:
            logger.debug(f"Collection ensure failed [{name}]: {exc}")

    def _upsert(self, collection: str, point_id: str,
                 vector: List[float], payload: Dict):
        client = self._get_qdrant()
        if client is None:
            return
        try:
            from qdrant_client.models import PointStruct
            self._ensure_collection(collection, VECTOR_DIM)
            client.upsert(
                collection_name=collection,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)]
            )
        except Exception as exc:
            logger.debug(f"[GenomeVectorizer] Upsert failed: {exc}")

    def _semantic_vector(self, genome: Dict) -> List[float]:
        """Natural language embedding via sentence-transformers."""
        from sentence_transformers import SentenceTransformer
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        text = (
            f"hook:{genome.get('hook_type','?')} "
            f"emotion:{genome.get('emotion','?')} "
            f"authority:{genome.get('authority_signal','?')} "
            f"offer:{genome.get('offer_type','?')} "
            f"cta:{genome.get('cta_style','?')} "
            f"pacing:{genome.get('pacing','?')} "
            f"structure:{genome.get('structure','?')}"
        )
        return self._model.encode([text], normalize_embeddings=True)[0].tolist()
