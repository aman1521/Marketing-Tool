"""
PGIL Influence Controller
=========================
Delivers PGIL intelligence as weighted influence signals
to CaptainStrategy.

Influence model:
  PGIL provides a PRIOR on top of tenant-specific memory.
  It does NOT override operator or tenant signals.
  It serves as the platform-wide Bayesian prior.

Weight blending:
  pgil_weight   = base 0.20
  Increases to 0.35 if:
    - Confirmed archetype found with high confidence
    - Sample count > 50 in the pattern
    - Cross-industry (UNIVERSAL tier)

Action vocabulary:
  EXECUTE          — PGIL strongly supports strategy, low risk
  PROCEED          — Positive but moderate support
  PROCEED_WITH_MON — Weak evidence, monitor closely
  DEFER            — Insufficient evidence, wait for operator/tenant data
  AVOID            — PGIL shows consistent negative outcomes

Access Control:
  🔒 PGIL data is accessible only to OPERATOR-LEVEL access.
  tenant_only_access=True will return a stripped signal with no archetypes.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .pgil_archetype_builder import PGILArchetypeBuilder
from .pgil_pattern_engine    import PGILPatternEngine
from .pgil_vector_store      import PGILVectorStore

logger = logging.getLogger(__name__)

BASE_PGIL_WEIGHT  = 0.20
MAX_PGIL_WEIGHT   = 0.38
UNIVERSAL_BONUS   = 0.05
MIN_PRIOR_SAMPLES = 8   # patterns need this many samples to influence

CONFIDENCE_BANDS = [
    (0.80, "HIGH"),
    (0.60, "MEDIUM"),
    (0.40, "LOW"),
    (0.00, "INSUFFICIENT"),
]


class PGILInfluenceController:
    """
    Operator-level PGIL influence signal generator.
    Read-only. Zero side effects. Zero return of identity data.
    """

    def __init__(self, vector_store: Optional[PGILVectorStore] = None):
        self.vs       = vector_store or PGILVectorStore()
        self.patterns = PGILPatternEngine(self.vs)
        self.archetypes = PGILArchetypeBuilder(self.vs)

    # ── Main signal API ───────────────────────────────────────────────────

    def get_influence(self, operator_context: Dict[str, Any],
                       operator_access: bool = True) -> Dict[str, Any]:
        """
        Generate PGIL influence signal for given strategy context.

        Args:
            operator_context: current strategy decision context (may contain tenant data)
            operator_access:  True = full archetype detail (operator)
                              False = stripped signal (tenant-only access)
        Returns:
            InfluenceSignal dict
        """
        # Anonymise context before querying PGIL
        anon_ctx = self._anonymise_context(operator_context)

        # ── Pattern signal ─────────────────────────────────────────────
        similar_patterns = self.patterns.find_similar(anon_ctx, top_k=5)
        pattern_signal   = self._aggregate_pattern_signal(similar_patterns)

        # ── Archetype signal ───────────────────────────────────────────
        archetype_matches = self.archetypes.find_matching(anon_ctx, top_k=3)
        archetype_signal  = self._aggregate_archetype_signal(archetype_matches)

        # ── Weight computation ─────────────────────────────────────────
        pgil_weight = self._compute_weight(pattern_signal, archetype_signal)

        # ── Blended PGIL signal ────────────────────────────────────────
        predicted_lift = (
            pattern_signal["avg_lift"]   * 0.40
            + archetype_signal["lift_prior"] * 0.60
            if archetype_signal["archetype_found"]
            else pattern_signal["avg_lift"]
        )
        predicted_risk = pattern_signal["avg_risk"]
        confidence     = max(pattern_signal["confidence"], archetype_signal["confidence"])
        win_rate       = (
            pattern_signal["win_rate"]   * 0.50
            + archetype_signal["win_rate"]  * 0.50
            if archetype_signal["archetype_found"]
            else pattern_signal["win_rate"]
        )

        bias_modifier  = archetype_signal.get("bias_modifier", 0.0)
        final_lift     = round(predicted_lift * (1 + bias_modifier), 4)
        action         = self._recommend(final_lift, win_rate, confidence)
        conf_band      = self._confidence_band(confidence)

        # Build signal
        signal = {
            "pgil_weight":       round(pgil_weight, 4),
            "predicted_lift":    round(predicted_lift, 4),
            "final_lift":        final_lift,
            "predicted_risk":    round(predicted_risk, 4),
            "win_rate":          round(win_rate, 4),
            "confidence":        round(confidence, 4),
            "confidence_band":   conf_band,
            "bias_modifier":     bias_modifier,
            "action":            action,
            "patterns_matched":  pattern_signal["count"],
            "pattern_signal":    pattern_signal,
            "archetype_signal":  archetype_signal if operator_access else {"archetype_found": archetype_signal["archetype_found"]},
            "notes":             self._generate_notes(pattern_signal, archetype_signal, conf_band),
            "generated_at":      datetime.utcnow().isoformat(),
        }

        logger.info(
            f"[PGIL Influence] strategy={anon_ctx.get('strategy_type')} "
            f"lift={final_lift:+.3f} action={action} "
            f"weight={pgil_weight:.2f} conf={confidence:.2f} [{conf_band}]"
        )
        return signal

    def get_global_priors(self, strategy_type: str,
                           industry_bucket: str) -> Dict[str, Any]:
        """
        Return cross-tenant statistical priors for a specific strategy+industry.
        Used by CaptainStrategy as Bayesian initialisation.
        """
        patterns = self.patterns.get_patterns(
            strategy=strategy_type,
            industry=industry_bucket,
            min_confidence=0.50
        )
        if not patterns:
            return {
                "strategy_type":  strategy_type,
                "industry_bucket":industry_bucket,
                "has_prior":      False,
                "prior_lift":     0.0,
                "prior_win_rate": 0.50,
                "prior_confidence": 0.0,
                "sample_count":   0,
            }
        total_n   = sum(p["sample_count"] for p in patterns)
        avg_lift  = sum(p["avg_lift"]  * p["sample_count"] for p in patterns) / total_n
        avg_wr    = sum(p["win_rate"]  * p["sample_count"] for p in patterns) / total_n
        avg_conf  = sum(p["confidence"]* p["sample_count"] for p in patterns) / total_n
        return {
            "strategy_type":    strategy_type,
            "industry_bucket":  industry_bucket,
            "has_prior":        True,
            "prior_lift":       round(avg_lift, 4),
            "prior_win_rate":   round(avg_wr, 4),
            "prior_confidence": round(avg_conf, 4),
            "sample_count":     total_n,
            "patterns_used":    len(patterns),
        }

    def get_platform_insights(self) -> Dict[str, Any]:
        """
        High-level platform performance statistics.
        Safe for operator dashboard display.
        """
        p_summary = self.patterns.summary()
        a_summary = self.archetypes.summary()
        confirmed = self.archetypes.get_confirmed()

        top_archetypes = [{
            "name":       a["name"],
            "tier":       a.get("archetype_tier","INDUSTRY"),
            "avg_lift":   a["avg_lift"],
            "win_rate":   a["win_rate"],
            "confidence": a["confidence"],
            "sample_count": a["sample_count"],
        } for a in sorted(confirmed, key=lambda x: -x["confidence"])[:5]]

        return {
            "patterns":    p_summary,
            "archetypes":  a_summary,
            "top_archetypes": top_archetypes,
            "vector_store":   self.vs.collection_info(),
        }

    # ── Signal aggregation helpers ────────────────────────────────────────

    @staticmethod
    def _aggregate_pattern_signal(patterns: List[Dict]) -> Dict:
        valid = [p for p in patterns if p.get("sample_count", 0) >= MIN_PRIOR_SAMPLES]
        if not valid:
            return {"count":0,"avg_lift":0.0,"avg_risk":0.0,"win_rate":0.50,"confidence":0.0}
        total     = sum(p["sample_count"] for p in valid)
        avg_lift  = sum(p["avg_lift"]  * p["sample_count"] for p in valid) / total
        avg_risk  = sum(p["avg_risk"]  * p["sample_count"] for p in valid) / total
        avg_wr    = sum(p["win_rate"]  * p["sample_count"] for p in valid) / total
        avg_conf  = sum(p["confidence"]* p["sample_count"] for p in valid) / total
        return {
            "count":      len(valid),
            "avg_lift":   round(avg_lift, 4),
            "avg_risk":   round(avg_risk, 4),
            "win_rate":   round(avg_wr, 4),
            "confidence": round(avg_conf, 4),
        }

    @staticmethod
    def _aggregate_archetype_signal(archetypes: List[Dict]) -> Dict:
        if not archetypes:
            return {"archetype_found":False, "lift_prior":0.0, "win_rate":0.50,
                    "confidence":0.0, "bias_modifier":0.0}
        best = archetypes[0]   # highest match score
        return {
            "archetype_found":  True,
            "archetype_name":   best.get("name",""),
            "archetype_tier":   best.get("archetype_tier","INDUSTRY"),
            "match_score":      best.get("match_score", 0.0),
            "lift_prior":       best.get("lift_prior", 0.0),
            "win_rate":         best.get("win_rate", 0.0),
            "confidence":       best.get("confidence", 0.0),
            "bias_modifier":    best.get("bias_modifier", 0.0),
            "sample_count":     best.get("sample_count", 0),
            "industry_coverage":best.get("industry_coverage", 1),
        }

    @staticmethod
    def _compute_weight(ps: Dict, as_: Dict) -> float:
        weight = BASE_PGIL_WEIGHT
        if as_.get("archetype_found"):
            conf = as_.get("confidence", 0)
            if conf > 0.75:
                weight += 0.10
            elif conf > 0.60:
                weight += 0.05
            if as_.get("archetype_tier") == "UNIVERSAL":
                weight += UNIVERSAL_BONUS
        return min(MAX_PGIL_WEIGHT, round(weight, 4))

    @staticmethod
    def _recommend(lift: float, win_rate: float, confidence: float) -> str:
        if confidence < 0.30 or win_rate == 0.50:
            return "DEFER"
        if lift < -0.05 and win_rate < 0.40:
            return "AVOID"
        if lift > 0.08 and win_rate >= 0.65 and confidence >= 0.65:
            return "EXECUTE"
        if lift > 0.03 and win_rate >= 0.55:
            return "PROCEED"
        return "PROCEED_WITH_MON"

    @staticmethod
    def _confidence_band(confidence: float) -> str:
        for threshold, label in CONFIDENCE_BANDS:
            if confidence >= threshold:
                return label
        return "INSUFFICIENT"

    @staticmethod
    def _generate_notes(ps: Dict, as_: Dict, band: str) -> List[str]:
        notes = []
        if ps["count"] == 0:
            notes.append("No similar patterns found in PGIL — insufficient platform data for this context.")
        elif band == "INSUFFICIENT":
            notes.append("Pattern confidence below threshold. PGIL acting as weak prior only.")
        if as_.get("archetype_found"):
            tier = as_.get("archetype_tier","INDUSTRY")
            n    = as_.get("archetype_name","")
            cov  = as_.get("industry_coverage",1)
            if tier == "UNIVERSAL":
                notes.append(
                    f"UNIVERSAL archetype '{n}' matches — validated across {cov} industries. Strong prior."
                )
            else:
                notes.append(f"Archetype '{n}' matched — industry-specific pattern.")
        if ps.get("avg_lift",0) < -0.05:
            notes.append("⚠️ PGIL pattern history shows negative lift — proceed with caution.")
        return notes

    # ── Anonymisation helper ──────────────────────────────────────────────

    @staticmethod
    def _anonymise_context(ctx: Dict) -> Dict:
        from .pgil_collector import PGILCollector
        c = PGILCollector()
        stripped = c._strip_pii(ctx)
        bucketed = c._bucket_signals(stripped)
        return c._sanitise_categoricals(bucketed)
