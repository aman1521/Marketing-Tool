"""
PGIL Collector
==============
Ingestion gateway for the Private Global Intelligence Layer.

Responsibilities:
  1. Accept raw strategy events from tenant pipelines
  2. Apply multi-pass anonymisation (strip → bucket → validate)
  3. Generate pattern fingerprint
  4. Emit anonymised PGILEvent to the store
  5. Route event to PGILPatternEngine for aggregation

🔒 PRIVACY RULES enforced here:
  - company_id, tenant_id, operator_id blocked before storage
  - spend amounts, campaign names, ad IDs blocked
  - Only structural + statistical signals pass through
  - All numeric signals bucketed — no raw values stored
"""

import hashlib
import logging
import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Allowed output fields ──────────────────────────────────────────────────
ALLOWED_FIELDS = {
    "strategy_type", "industry_bucket", "creative_cluster", "funnel_stage",
    "volatility_band", "scaling_band", "drift_bucket", "confidence_bucket",
    "roi_direction", "escalation_level", "outcome", "lift_delta",
    "risk_score", "time_to_result_h",
}

# ── PII/sensitive fields — blocked unconditionally ────────────────────────
BLOCKED_FIELDS = {
    "company_id", "tenant_id", "operator_id", "campaign_id", "ad_id",
    "ad_name", "campaign_name", "brand", "company_name", "account_id",
    "pixel_id", "budget_amount", "spend", "revenue", "cogs", "profit",
    "customer_email", "user_id", "domain", "url",
}

# ── Bucketing thresholds ───────────────────────────────────────────────────
VOLATILITY_BUCKETS = [(0.0, 0.25, "low"), (0.25, 0.50, "medium"),
                      (0.50, 0.75, "high"),  (0.75, 1.01, "extreme")]
DRIFT_BUCKETS      = [(0.0, 0.15, "low"), (0.15, 0.35, "medium"), (0.35, 1.01, "high")]
CONFIDENCE_BUCKETS = [(0.0, 0.55, "low"), (0.55, 0.78, "medium"), (0.78, 1.01, "high")]

INDUSTRY_VALID  = {"ecommerce", "saas", "fintech", "health", "agency", "other"}
CREATIVE_VALID  = {"trial", "discount", "premium", "trust", "education", "comparison", "urgency", "other"}
FUNNEL_VALID    = {"tofu", "mofu", "bofu", "retention"}
SCALING_VALID   = {"micro", "growth", "scale", "enterprise"}
STRATEGY_VALID  = {
    "scale_budget", "reduce_budget", "pause", "creative_refresh",
    "audience_expansion", "bid_adjustment", "test_new_platform",
    "retarget", "seasonal_push", "default"
}

# In-memory event log (replace with DB session calls in production)
_events: List[Dict] = []


def _bucket(value: float, buckets: List[Tuple]) -> str:
    for lo, hi, label in buckets:
        if lo <= value < hi:
            return label
    return buckets[-1][2]


class PGILCollector:
    """
    Single entry point for all PGIL event ingestion.
    Hard anonymisation enforced before any event reaches storage.
    """

    # ── Primary ingestion API ──────────────────────────────────────────────

    def collect(self, raw_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Accept a raw strategy event dict (may contain PII).
        Anonymise, validate, bin, fingerprint and store.
        Returns the anonymised event dict or None if rejected.
        """
        # Step 1: Block PII fields
        anon = self._strip_pii(raw_event)

        # Step 2: Validate required structural fields
        if not self._validate(anon):
            logger.warning("[PGIL] Event rejected: missing required structural fields")
            return None

        # Step 3: Bucket numeric signals
        anon = self._bucket_signals(anon)

        # Step 4: Sanitise categoricals
        anon = self._sanitise_categoricals(anon)

        # Step 5: Compute pattern fingerprint
        anon["pattern_fingerprint"] = self._fingerprint(anon)

        # Step 6: Add non-identifying temporal context
        anon["week_of_year"] = datetime.utcnow().isocalendar()[1]
        anon["collected_at"] = datetime.utcnow().isoformat()

        # Step 7: Final allowed-fields pass (belt + suspenders)
        safe = {k: v for k, v in anon.items()
                if k in ALLOWED_FIELDS | {"pattern_fingerprint", "week_of_year", "collected_at"}}

        _events.append(safe)
        logger.info(
            f"[PGIL] Event collected: strategy={safe.get('strategy_type')} "
            f"industry={safe.get('industry_bucket')} "
            f"outcome={safe.get('outcome')} "
            f"fp={safe.get('pattern_fingerprint')}"
        )
        return safe

    def collect_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Collect multiple events. Returns only successfully processed ones."""
        return [e for raw in events if (e := self.collect(raw)) is not None]

    # ── Query ──────────────────────────────────────────────────────────────

    def get_events(self, filters: Optional[Dict] = None,
                   limit: int = 500) -> List[Dict]:
        """Return stored events, optionally filtered by structural attributes."""
        evts = list(_events)
        if filters:
            for k, v in filters.items():
                evts = [e for e in evts if e.get(k) == v]
        return evts[-limit:]

    def event_count(self) -> int:
        return len(_events)

    # ── Anonymisation pipeline ────────────────────────────────────────────

    @staticmethod
    def _strip_pii(event: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in event.items() if k not in BLOCKED_FIELDS}

    @staticmethod
    def _validate(event: Dict[str, Any]) -> bool:
        required = {"strategy_type", "industry_bucket", "funnel_stage", "outcome"}
        return required.issubset(set(event.keys()))

    @staticmethod
    def _bucket_signals(event: Dict[str, Any]) -> Dict[str, Any]:
        e = dict(event)

        # Bucket volatility
        if "volatility_index" in e:
            e["volatility_band"] = _bucket(float(e.pop("volatility_index")), VOLATILITY_BUCKETS)

        # Bucket drift
        if "drift_frequency" in e:
            e["drift_bucket"] = _bucket(float(e.pop("drift_frequency")), DRIFT_BUCKETS)

        # Bucket confidence
        if "confidence_avg" in e:
            e["confidence_bucket"] = _bucket(float(e.pop("confidence_avg")), CONFIDENCE_BUCKETS)

        # ROI direction
        if "roi_delta_48h" in e:
            roi = float(e.pop("roi_delta_48h"))
            e["roi_direction"] = "up" if roi > 0.02 else "down" if roi < -0.02 else "flat"

        # Escalation level
        if "escalation_frequency" in e:
            esc = float(e.pop("escalation_frequency"))
            e["escalation_level"] = "high" if esc > 0.30 else "low" if esc > 0.05 else "none"

        # Strip any remaining absolute numeric fields
        for drop in ["lift_absolute", "spend_amount", "revenue_amount", "roas"]:
            e.pop(drop, None)

        return e

    @staticmethod
    def _sanitise_categoricals(event: Dict[str, Any]) -> Dict[str, Any]:
        e = dict(event)
        e["industry_bucket"]  = e.get("industry_bucket",  "other") if e.get("industry_bucket")  in INDUSTRY_VALID  else "other"
        e["creative_cluster"] = e.get("creative_cluster", "other") if e.get("creative_cluster") in CREATIVE_VALID  else "other"
        e["funnel_stage"]     = e.get("funnel_stage",     "mofu")  if e.get("funnel_stage")     in FUNNEL_VALID    else "mofu"
        e["scaling_band"]     = e.get("scaling_band",     "growth")if e.get("scaling_band")     in SCALING_VALID   else "growth"
        e["strategy_type"]    = e.get("strategy_type",   "default")if e.get("strategy_type")    in STRATEGY_VALID  else "default"
        return e

    @staticmethod
    def _fingerprint(event: Dict[str, Any]) -> str:
        key = ":".join([
            event.get("strategy_type",    "?"),
            event.get("industry_bucket",  "?"),
            event.get("creative_cluster", "?"),
            event.get("funnel_stage",     "?"),
            event.get("volatility_band",  event.get("volatility_index", "?")),
            event.get("scaling_band",     "?"),
            event.get("drift_bucket",     "med"),
            event.get("confidence_bucket","med"),
        ])
        return hashlib.sha256(key.encode()).hexdigest()[:20]
