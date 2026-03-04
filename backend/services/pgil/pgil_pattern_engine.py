"""
PGIL Pattern Engine
===================
Detects and aggregates repeating cross-tenant success patterns
from anonymised PGILEvents.

Algorithm:
  1. Events are grouped by pattern_fingerprint
  2. Per-fingerprint: running Welford aggregation of lift/risk
  3. Wilson lower-bound confidence scoring
  4. Pattern promotion lifecycle:
       EMERGING  → min 3 events
       VALIDATED → min 8 events + confidence ≥ 0.60
       DOMINANT  → min 20 events + confidence ≥ 0.75 + win_rate ≥ 0.70
       DEPRECATED→ win_rate drops below 0.30 with sample_count > 10

  5. Cross-industry detection: patterns spanning multiple industries
     receive an industry_coverage bonus on confidence.

Outputs:
  PGILPattern dicts → consumed by PGILArchetypeBuilder
"""

import math
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from .pgil_vector_store import PGILVectorStore

logger = logging.getLogger(__name__)

EMERGING_MIN   = 3
VALIDATED_MIN  = 8
DOMINANT_MIN   = 20
VALIDATED_CONF = 0.60
DOMINANT_CONF  = 0.75
DOMINANT_WR    = 0.70
DEPRECATED_WR  = 0.30
DEPRECATED_MIN = 10

# In-memory pattern store
_patterns: Dict[str, Dict] = {}


class PGILPatternEngine:
    """
    Stateful cross-tenant pattern aggregator.
    Processes anonymised events → detected patterns.
    """

    def __init__(self, vector_store: Optional[PGILVectorStore] = None):
        self.vs = vector_store or PGILVectorStore()

    # ── Main ingestion ────────────────────────────────────────────────────

    def process_event(self, event: Dict[str, Any]) -> str:
        """
        Process one anonymised event into the pattern store.
        Returns the pattern fingerprint.
        """
        fp = event.get("pattern_fingerprint")
        if not fp:
            logger.warning("[PGIL Pattern] Event has no fingerprint — skipping")
            return ""

        outcome    = event.get("outcome", "pending")
        lift       = float(event.get("lift_delta", 0.0))
        risk       = float(event.get("risk_score",  0.0))
        is_win     = outcome == "win"

        if fp in _patterns:
            self._aggregate(_patterns[fp], is_win, lift, risk)
        else:
            _patterns[fp] = self._create_pattern(event, is_win, lift, risk)
            # Store centroid in Qdrant
            pid = self.vs.upsert_pattern(_patterns[fp])
            _patterns[fp]["qdrant_point_id"] = pid

        # Update Qdrant with refreshed stats
        self.vs.upsert_pattern(_patterns[fp])
        return fp

    def process_batch(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of events. Returns processing summary."""
        processed = 0
        skipped   = 0
        for event in events:
            fp = self.process_event(event)
            if fp:
                processed += 1
            else:
                skipped += 1
        # Run lifecycle after batch
        lifecycle = self.run_lifecycle()
        return {
            "processed": processed,
            "skipped":   skipped,
            "patterns":  len(_patterns),
            **lifecycle
        }

    # ── Lifecycle management ──────────────────────────────────────────────

    def run_lifecycle(self) -> Dict[str, int]:
        """Promote and deprecate patterns based on statistical thresholds."""
        promoted   = 0
        deprecated = 0

        for fp, p in _patterns.items():
            old_status = p["status"]
            new_status = self._compute_status(p)
            if new_status != old_status:
                p["status"]       = new_status
                p["last_updated"] = datetime.utcnow().isoformat()
                if new_status in ("validated", "dominant"):
                    promoted += 1
                    logger.info(
                        f"[PGIL Pattern] PROMOTED [{fp[:8]}] "
                        f"{old_status}→{new_status} "
                        f"n={p['sample_count']} wr={p['win_rate']:.2f} "
                        f"conf={p['confidence']:.2f}"
                    )
                elif new_status == "deprecated":
                    deprecated += 1
                    logger.info(f"[PGIL Pattern] DEPRECATED [{fp[:8]}]")

        return {"patterns_promoted": promoted, "patterns_deprecated": deprecated}

    # ── Query ─────────────────────────────────────────────────────────────

    def get_patterns(self, status: Optional[str] = None,
                     industry: Optional[str] = None,
                     strategy: Optional[str] = None,
                     min_confidence: float = 0.0) -> List[Dict]:
        patterns = list(_patterns.values())
        if status:
            patterns = [p for p in patterns if p["status"] == status]
        if industry:
            patterns = [p for p in patterns if p["industry_bucket"] == industry]
        if strategy:
            patterns = [p for p in patterns if p["strategy_type"] == strategy]
        patterns = [p for p in patterns if p["confidence"] >= min_confidence]
        patterns.sort(key=lambda p: (-p["confidence"], -p["sample_count"]))
        return patterns

    def find_similar(self, context: Dict[str, Any], top_k: int = 8) -> List[Dict]:
        """Find similar patterns via vector similarity."""
        hits = self.vs.search_similar_patterns(context, top_k=top_k)
        # Enrich with full pattern data
        return [{**_patterns.get(h["payload"].get("fingerprint",""), {}), "similarity": h["score"]}
                for h in hits if h["payload"].get("fingerprint","") in _patterns]

    def get_cross_industry_patterns(self, min_coverage: int = 2) -> List[Dict]:
        """Return patterns that appear across multiple industry buckets."""
        # Group fingerprints by base structure (strip industry)
        from hashlib import sha256
        base_groups: Dict[str, List[Dict]] = defaultdict(list)
        for fp, p in _patterns.items():
            base_key = ":".join([
                p.get("strategy_type","?"),
                p.get("creative_cluster","?"),
                p.get("funnel_stage","?"),
                p.get("volatility_band","?"),
                p.get("scaling_band","?"),
            ])
            base_key = sha256(base_key.encode()).hexdigest()[:16]
            base_groups[base_key].append(p)

        cross = []
        for base, group in base_groups.items():
            industries = set(p["industry_bucket"] for p in group)
            if len(industries) >= min_coverage:
                # Merge stats
                total_n  = sum(p["sample_count"] for p in group)
                all_lifts= [p["avg_lift"] for p in group]
                all_wrs  = [p["win_rate"]  for p in group]
                cross.append({
                    "base_key":        base,
                    "strategy_type":   group[0]["strategy_type"],
                    "industry_coverage": len(industries),
                    "industries":      list(industries),
                    "sample_count":    total_n,
                    "avg_lift":        round(sum(all_lifts)/len(all_lifts), 4),
                    "avg_win_rate":    round(sum(all_wrs)/len(all_wrs), 4),
                    "component_patterns": [p["fingerprint"] for p in group],
                    "source_patterns": group,
                })
        cross.sort(key=lambda x: (-x["industry_coverage"], -x["avg_win_rate"]))
        return cross

    def summary(self) -> Dict[str, Any]:
        all_p = list(_patterns.values())
        return {
            "total_patterns":    len(all_p),
            "by_status":         {s: sum(1 for p in all_p if p["status"]==s)
                                   for s in ("emerging","validated","dominant","deprecated")},
            "total_events":      sum(p["sample_count"] for p in all_p),
            "avg_win_rate":      round(sum(p["win_rate"] for p in all_p)/len(all_p),4) if all_p else 0,
        }

    # ── Stats helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _compute_status(p: Dict) -> str:
        n    = p["sample_count"]
        conf = p["confidence"]
        wr   = p["win_rate"]
        if n > DEPRECATED_MIN and wr < DEPRECATED_WR:
            return "deprecated"
        if n >= DOMINANT_MIN and conf >= DOMINANT_CONF and wr >= DOMINANT_WR:
            return "dominant"
        if n >= VALIDATED_MIN and conf >= VALIDATED_CONF:
            return "validated"
        return "emerging"

    @staticmethod
    def _create_pattern(event: Dict, is_win: bool, lift: float, risk: float) -> Dict:
        fp = event.get("pattern_fingerprint", str(uuid.uuid4())[:20])
        return {
            "id":              str(uuid.uuid4()),
            "fingerprint":     fp,
            "strategy_type":   event.get("strategy_type",    "default"),
            "industry_bucket": event.get("industry_bucket",  "other"),
            "creative_cluster":event.get("creative_cluster", "other"),
            "funnel_stage":    event.get("funnel_stage",     "mofu"),
            "volatility_band": event.get("volatility_band",  "medium"),
            "scaling_band":    event.get("scaling_band",     "growth"),
            "sample_count":    1,
            "win_count":       1 if is_win else 0,
            "avg_lift":        lift,
            "avg_risk":        risk,
            "stddev_lift":     0.0,
            "_m2_lift":        0.0,   # Welford M2 accumulator
            "win_rate":        1.0 if is_win else 0.0,
            "confidence":      PGILPatternEngine._wilson_lower(1 if is_win else 0, 1),
            "status":          "emerging",
            "qdrant_point_id": None,
            "first_seen":      datetime.utcnow().isoformat(),
            "last_updated":    datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _aggregate(p: Dict, is_win: bool, lift: float, risk: float):
        """Welford online variance + running mean update."""
        n    = p["sample_count"] + 1
        old_mean = p["avg_lift"]
        # Welford update
        delta          = lift - old_mean
        new_mean       = old_mean + delta / n
        delta2         = lift - new_mean
        p["_m2_lift"]  = p.get("_m2_lift", 0.0) + delta * delta2
        p["stddev_lift"]= math.sqrt(p["_m2_lift"] / n) if n > 1 else 0.0
        p["avg_lift"]  = round(new_mean, 5)
        p["avg_risk"]  = round((p["avg_risk"] * p["sample_count"] + risk) / n, 5)
        p["sample_count"] = n
        if is_win:
            p["win_count"] = p.get("win_count", 0) + 1
        p["win_rate"]  = round(p["win_count"] / n, 4)
        p["confidence"]= PGILPatternEngine._wilson_lower(p["win_count"], n)
        p["last_updated"] = datetime.utcnow().isoformat()

    @staticmethod
    def _wilson_lower(wins: int, n: int, z: float = 1.96) -> float:
        if n == 0:
            return 0.0
        phat   = wins / n
        denom  = 1 + z**2 / n
        centre = phat + z**2 / (2*n)
        spread = z * math.sqrt(max(0.0, phat*(1-phat)/n + z**2/(4*n**2)))
        return round(max(0.0, (centre - spread) / denom), 4)
