"""
Influence Controller
====================
Blends intelligence signals from all three memory tiers
into a single weighted strategy recommendation for CaptainStrategy.

Influence model:
  Private  (Tier 1): highest weight when sample count ≥ threshold
  Tenant   (Tier 2): medium weight, company-proven patterns
  Global   (Tier 3): baseline prior, attenuated by sample confidence

Weights dynamically shift:
  - If operator has rich private history → private weight increases
  - If tenant patterns are confirmed     → tenant weight increases
  - If global confidence is high         → global acts as strong prior
  - All weights normalised to sum = 1.0

Output: InfluenceSignal (JSON)
  → consumed directly by CaptainStrategy (read-only signal)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .private_memory_engine  import PrivateMemoryEngine
from .tenant_memory_engine   import TenantMemoryEngine
from .global_memory_engine   import GlobalMemoryEngine
from .archetype_builder      import ArchetypeBuilder

logger = logging.getLogger(__name__)

# Base influence weights
BASE_WEIGHTS = {
    "private": 0.45,
    "tenant":  0.35,
    "global":  0.20,
}

# Private weight floor/ceiling
PRIVATE_WEIGHT_MAX = 0.65
PRIVATE_WEIGHT_MIN = 0.20
TENANT_WEIGHT_MAX  = 0.55
GLOBAL_WEIGHT_MAX  = 0.40

PRIVATE_MIN_SAMPLES = 5    # private becomes dominant above this
GLOBAL_TRUST_SAMPLES = 10   # global confidence threshold


class InfluenceController:
    """
    Single point of truth for memory-weighted strategy influence.
    CaptainStrategy calls this before any strategy decision.
    """

    def __init__(self):
        self.private_mem = PrivateMemoryEngine()
        self.tenant_mem  = TenantMemoryEngine()
        self.global_mem  = GlobalMemoryEngine()
        self.archetypes  = ArchetypeBuilder()

    # ── Main signal generation ─────────────────────────────────────

    def get_influence_signal(self, operator_id: str, company_id: str,
                              current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute blended strategy influence for a given context.
        Returns InfluenceSignal for CaptainStrategy consumption.
        """
        # ── Gather raw signals from each tier ─────────────────────
        private_signal = self._private_signal(operator_id, current_context)
        tenant_signal  = self._tenant_signal(company_id, current_context)
        global_signal  = self._global_signal(current_context)
        archetype_signal = self._archetype_signal(current_context)

        # ── Compute dynamic weights ────────────────────────────────
        weights = self._compute_weights(private_signal, tenant_signal, global_signal)

        # ── Blend lift predictions ─────────────────────────────────
        blended_lift = (
            private_signal["predicted_lift"] * weights["private"]
            + tenant_signal["predicted_lift"] * weights["tenant"]
            + global_signal["predicted_lift"] * weights["global"]
        )

        blended_win_rate = (
            private_signal["win_rate"] * weights["private"]
            + tenant_signal["win_rate"] * weights["tenant"]
            + global_signal["win_rate"] * weights["global"]
        )

        blended_confidence = (
            private_signal["confidence"] * weights["private"]
            + tenant_signal["confidence"] * weights["tenant"]
            + global_signal["confidence"] * weights["global"]
        )

        # ── Apply archetype bias modifier ─────────────────────────
        bias = archetype_signal.get("bias_modifier", 0.0)
        final_lift = round(blended_lift + (blended_lift * bias), 4)

        # ── Compute action recommendation ─────────────────────────
        action = self._recommend_action(final_lift, blended_win_rate, blended_confidence)

        signal = {
            "operator_id":      operator_id,
            "company_id":       company_id,
            "strategy_type":    current_context.get("strategy_type", "unknown"),
            "blended_lift":     round(blended_lift, 4),
            "final_lift":       final_lift,
            "blended_win_rate": round(blended_win_rate, 4),
            "blended_confidence": round(blended_confidence, 4),
            "archetype_bias":   bias,
            "weights":          weights,
            "action":           action,
            "tier_signals": {
                "private": private_signal,
                "tenant":  tenant_signal,
                "global":  global_signal,
            },
            "archetype_signal": archetype_signal,
            "generated_at":     datetime.utcnow().isoformat(),
        }

        logger.info(
            f"[InfluenceCtrl] company=[{company_id}] strategy=[{current_context.get('strategy_type')}] "
            f"lift={final_lift:+.3f} conf={blended_confidence:.2f} action={action}"
        )
        return signal

    # ── Per-tier signal extraction ─────────────────────────────────

    def _private_signal(self, operator_id: str, ctx: Dict) -> Dict:
        hits = self.private_mem.query_similar(operator_id, ctx, top_k=5)
        stats = self.private_mem.get_operator_lift_stats(
            operator_id, ctx.get("strategy_type", "unknown")
        )
        if not hits:
            return {"predicted_lift": 0.0, "win_rate": 0.5, "confidence": 0.0, "sample_count": 0}
        lifts = [h["lift_delta"] for h in hits if h.get("lift_delta")]
        wins  = [h for h in hits if h.get("outcome") == "win"]
        return {
            "predicted_lift":  round(sum(lifts)/len(lifts), 4) if lifts else 0.0,
            "win_rate":        round(len(wins)/len(hits), 4),
            "confidence":      round(min(1.0, len(hits) / 10.0), 4),
            "sample_count":    stats.get("sample_count", 0),
        }

    def _tenant_signal(self, company_id: str, ctx: Dict) -> Dict:
        hits  = self.tenant_mem.query_similar(company_id, ctx, top_k=8, outcome_filter=None)
        stats = self.tenant_mem.get_strategy_stats(company_id)
        stype = ctx.get("strategy_type", "unknown")
        type_stats = stats.get(stype, {})

        if not hits:
            return {"predicted_lift": 0.0, "win_rate": 0.5, "confidence": 0.0, "sample_count": 0}

        lifts = [h["lift_delta"] for h in hits if h.get("lift_delta") is not None]
        wins  = [h for h in hits if h.get("outcome") == "win"]
        return {
            "predicted_lift": round(sum(lifts)/len(lifts), 4) if lifts else 0.0,
            "win_rate":       round(type_stats.get("win_rate", len(wins)/max(1,len(hits))), 4),
            "confidence":     round(min(1.0, len(hits) / 15.0), 4),
            "sample_count":   type_stats.get("sample_count", len(hits)),
        }

    def _global_signal(self, ctx: Dict) -> Dict:
        hits = self.global_mem.query_similar(ctx, top_k=5)
        if not hits:
            return {"predicted_lift": 0.0, "win_rate": 0.5, "confidence": 0.0, "sample_count": 0}
        lifts = [h["avg_lift"] for h in hits]
        wins  = [h["win_rate"] for h in hits]
        confs = [h["confidence"] for h in hits]
        return {
            "predicted_lift": round(sum(lifts)/len(lifts), 4),
            "win_rate":       round(sum(wins)/len(wins), 4),
            "confidence":     round(sum(confs)/len(confs), 4),
            "sample_count":   sum(h.get("sample_count", 0) for h in hits),
        }

    def _archetype_signal(self, ctx: Dict) -> Dict:
        matches = self.archetypes.find_matching_archetypes(ctx, top_k=1)
        if not matches:
            return {"archetype_found": False, "bias_modifier": 0.0}
        m = matches[0]
        return {
            "archetype_found": True,
            "archetype_name":  m["name"],
            "archetype_status":m["status"],
            "match_score":     m.get("match_score", 0.0),
            "bias_modifier":   m.get("bias_modifier", 0.0),
        }

    # ── Dynamic weight computation ─────────────────────────────────

    def _compute_weights(self, private: Dict, tenant: Dict,
                          global_: Dict) -> Dict[str, float]:
        """
        Dynamically shift weights based on data richness of each tier.
        Private dominates when rich; global acts as strong prior when scarce.
        """
        w = dict(BASE_WEIGHTS)

        # Private boost if operator has meaningful history
        p_samples = private.get("sample_count", 0)
        if p_samples >= PRIVATE_MIN_SAMPLES:
            boost = min(0.20, p_samples / 100)
            w["private"] = min(PRIVATE_WEIGHT_MAX, w["private"] + boost)
            w["global"]  = max(0.05, w["global"] - boost * 0.5)
            w["tenant"]  = max(0.10, w["tenant"]  - boost * 0.5)

        # Global boost if global signal is trust-worthy
        g_samples = global_.get("sample_count", 0)
        if g_samples >= GLOBAL_TRUST_SAMPLES:
            g_conf  = global_.get("confidence", 0.0)
            g_boost = g_conf * 0.10
            w["global"] = min(GLOBAL_WEIGHT_MAX, w["global"] + g_boost)

        # Normalise to sum = 1.0
        total = sum(w.values())
        return {k: round(v / total, 4) for k, v in w.items()}

    # ── Action recommendation ──────────────────────────────────────

    @staticmethod
    def _recommend_action(lift: float, win_rate: float, confidence: float) -> str:
        if confidence < 0.20:
            return "SANDBOX_FIRST"
        if lift > 0.08 and win_rate >= 0.65:
            return "EXECUTE"
        if lift > 0.03 and win_rate >= 0.50:
            return "EXECUTE_WITH_MONITORING"
        if lift < -0.05:
            return "BLOCK"
        return "REVIEW"
