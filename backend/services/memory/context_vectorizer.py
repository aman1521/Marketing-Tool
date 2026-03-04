"""
Context Vectorizer
==================
Converts raw strategy execution contexts into dense vector
representations for Qdrant storage and similarity search.

Context schema (input):
  {
    strategy_type:   str       # scale_budget, pause, creative_refresh, ...
    drift_frequency: float
    volatility_index: float
    confidence_avg:  float
    roi_delta_48h:   float
    escalation_freq: float
    portfolio_exposure: float
    industry_bucket: str       # ecommerce, saas, fintech, health, other
    aov_tier:        str       # low / mid / high
    scaling_band:    str       # micro / growth / scale
    outcome:         str       # win / loss / neutral
    lift_delta:      float
    risk_exposure:   float
  }
"""

import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

VECTOR_DIM = 384   # all-MiniLM-L6-v2

# ── Numerical fields and their normalisation ranges ───────────────────────
NUMERIC_FIELDS = {
    "drift_frequency":    (0.0, 1.0),
    "volatility_index":   (0.0, 1.0),
    "confidence_avg":     (0.0, 1.0),
    "roi_delta_48h":      (-1.0, 1.0),
    "escalation_freq":    (0.0, 1.0),
    "portfolio_exposure": (0.0, 100.0),
    "lift_delta":         (-1.0, 2.0),
    "risk_exposure":      (0.0, 1.0),
}

# ── Categorical one-hot maps ──────────────────────────────────────────────
STRATEGY_TYPES = [
    "scale_budget", "reduce_budget", "pause", "creative_refresh",
    "audience_expansion", "bid_adjustment", "test_new_platform",
    "retarget", "seasonal_push", "default"
]
INDUSTRY_BUCKETS = ["ecommerce", "saas", "fintech", "health", "agency", "other"]
AOV_TIERS        = ["low", "mid", "high"]
SCALING_BANDS    = ["micro", "growth", "scale"]
OUTCOMES         = ["win", "loss", "neutral", "pending"]


def _one_hot(value: str, options: List[str]) -> List[float]:
    return [1.0 if value == o else 0.0 for o in options]


def _normalise(value: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


class ContextVectorizer:
    """
    Converts strategy execution contexts to:
      1. Embedding-ready text (for SentenceTransformer)
      2. Structured feature vector (for direct numeric similarity)
      3. Pattern fingerprint hash (for deduplication)
    """

    # ── Text representation (for embedding model) ─────────────────────────

    def to_text(self, ctx: Dict[str, Any]) -> str:
        """Produce a readable natural-language summary of the context."""
        strategy  = ctx.get("strategy_type",  "unknown")
        industry  = ctx.get("industry_bucket","unknown")
        aov       = ctx.get("aov_tier",       "unknown")
        band      = ctx.get("scaling_band",   "unknown")
        drift     = ctx.get("drift_frequency", 0.0)
        vol       = ctx.get("volatility_index", 0.0)
        conf      = ctx.get("confidence_avg", 0.0)
        roi       = ctx.get("roi_delta_48h",  0.0)
        lift      = ctx.get("lift_delta",     0.0)
        outcome   = ctx.get("outcome",        "pending")

        text = (
            f"Strategy: {strategy}. "
            f"Industry: {industry}. AOV: {aov}. Scale band: {band}. "
            f"Drift: {drift:.2f}. Volatility: {vol:.2f}. Confidence: {conf:.2f}. "
            f"ROI delta: {roi:+.2f}. Lift: {lift:+.2f}. Outcome: {outcome}."
        )
        return text

    # ── Feature vector (numeric, for direct cosine search) ────────────────

    def to_feature_vector(self, ctx: Dict[str, Any]) -> List[float]:
        """
        Build a fixed-length feature vector for direct numeric similarity.
        Dimension: 8 numeric + 10 strategy OH + 6 industry OH + 3 AOV OH
                   + 3 scaling OH + 4 outcome OH = 34 dims
        """
        vec: List[float] = []

        # Numeric signals (normalised)
        for field, (lo, hi) in NUMERIC_FIELDS.items():
            vec.append(_normalise(float(ctx.get(field, 0.0)), lo, hi))

        # Categorical one-hots
        vec.extend(_one_hot(ctx.get("strategy_type",  "default"), STRATEGY_TYPES))
        vec.extend(_one_hot(ctx.get("industry_bucket","other"),    INDUSTRY_BUCKETS))
        vec.extend(_one_hot(ctx.get("aov_tier",       "mid"),      AOV_TIERS))
        vec.extend(_one_hot(ctx.get("scaling_band",   "growth"),   SCALING_BANDS))
        vec.extend(_one_hot(ctx.get("outcome",        "pending"),  OUTCOMES))

        return vec  # length 34

    # ── Embedding (via sentence-transformers or mock) ─────────────────────

    def embed(self, ctx: Dict[str, Any]) -> List[float]:
        """Produce VECTOR_DIM embedding from context text."""
        text = self.to_text(ctx)
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            vec = model.encode([text], normalize_embeddings=True)[0].tolist()
            return vec
        except ImportError:
            return self._mock_embed(text)

    def embed_batch(self, contexts: List[Dict[str, Any]]) -> List[List[float]]:
        texts = [self.to_text(c) for c in contexts]
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model.encode(texts, normalize_embeddings=True).tolist()
        except ImportError:
            return [self._mock_embed(t) for t in texts]

    # ── Pattern fingerprint (deduplication) ───────────────────────────────

    def fingerprint(self, ctx: Dict[str, Any]) -> str:
        """
        Hash of the context's categorical + bucketed numeric attributes.
        Two contexts with the same pattern profile produce the same fingerprint.
        """
        DRIFT_BUCKETS = [(0.0, 0.2, "low"), (0.2, 0.5, "med"), (0.5, 1.0, "high")]
        VOL_BUCKETS   = [(0.0, 0.3, "low"), (0.3, 0.6, "med"), (0.6, 1.0, "high")]

        def _bucket(v, buckets):
            for lo, hi, label in buckets:
                if lo <= v < hi:
                    return label
            return "high"

        key = ":".join([
            ctx.get("strategy_type",  "unknown"),
            ctx.get("industry_bucket","unknown"),
            ctx.get("aov_tier",       "unknown"),
            ctx.get("scaling_band",   "unknown"),
            _bucket(float(ctx.get("drift_frequency",  0)), DRIFT_BUCKETS),
            _bucket(float(ctx.get("volatility_index", 0)), VOL_BUCKETS),
        ])
        return hashlib.md5(key.encode()).hexdigest()[:16]

    # ── Anonymisation (Tier 3) ────────────────────────────────────────────

    def anonymise(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strip ALL identifiable fields. Returns only statistical/structural
        attributes safe for global memory storage.
        """
        SAFE_FIELDS = {
            "strategy_type", "industry_bucket", "aov_tier", "scaling_band",
            "drift_frequency", "volatility_index", "confidence_avg",
            "roi_delta_48h", "escalation_freq", "lift_delta",
            "risk_exposure", "outcome",
        }
        return {k: v for k, v in ctx.items() if k in SAFE_FIELDS}

    # ── Mock embed (deterministic, no GPU) ───────────────────────────────

    @staticmethod
    def _mock_embed(text: str) -> List[float]:
        digest = int(hashlib.md5(text.encode()).hexdigest(), 16)
        vec = [(digest >> (i * 4) & 0xF) / 15.0 for i in range(VECTOR_DIM)]
        norm = sum(x**2 for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]
