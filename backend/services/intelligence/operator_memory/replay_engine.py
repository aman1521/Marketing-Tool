"""
Replay Engine
=============
Simulates strategy execution against historical contexts
to predict likely outcome before committing capital.

Replay modes:
  ARCHETYPE_MATCH  — find closest archetype, project its stats
  HISTORICAL_SIM   — replay exact historical events in context order
  STRESS_TEST      — vary key signals to find performance envelope

Output: ReplayReport (JSON-safe dict)
  → consumed by CaptainStrategy for pre-execution validation
  → does NOT trigger execution
"""

import logging
import random
import copy
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .context_vectorizer    import ContextVectorizer
from .archetype_builder     import ArchetypeBuilder
from .private_memory_engine import PrivateMemoryEngine
from .tenant_memory_engine  import TenantMemoryEngine

logger = logging.getLogger(__name__)

STRESS_VARS = {
    "volatility_index":   [0.20, 0.40, 0.60, 0.80],
    "drift_frequency":    [0.05, 0.20, 0.35, 0.55],
    "confidence_avg":     [0.95, 0.80, 0.65, 0.50],
}


class ReplayEngine:
    """
    Pre-execution strategy simulation using memory tiers.
    Read-only. No side effects on any memory store.
    """

    def __init__(self):
        self.vectorizer  = ContextVectorizer()
        self.archetypes  = ArchetypeBuilder()
        self.private_mem = PrivateMemoryEngine()
        self.tenant_mem  = TenantMemoryEngine()

    # ── Main replay entry point ────────────────────────────────────

    def simulate(self, operator_id: str, company_id: str,
                 proposed_context: Dict[str, Any],
                 mode: str = "archetype_match") -> Dict[str, Any]:
        """
        Run replay simulation for a proposed strategy.

        Modes:
          archetype_match  — match to closest confirmed archetype
          historical_sim   — replay against similar past events
          stress_test      — run across volatility envelope
        """
        if mode == "archetype_match":
            return self._archetype_match(operator_id, company_id, proposed_context)
        elif mode == "historical_sim":
            return self._historical_sim(operator_id, company_id, proposed_context)
        elif mode == "stress_test":
            return self._stress_test(operator_id, company_id, proposed_context)
        else:
            return {"error": f"Unknown mode: {mode}"}

    # ── Mode 1: Archetype match ────────────────────────────────────

    def _archetype_match(self, operator_id: str, company_id: str,
                          ctx: Dict[str, Any]) -> Dict[str, Any]:
        matches = self.archetypes.find_matching_archetypes(ctx, top_k=3)

        if not matches:
            return self._no_data_report(ctx, "archetype_match")

        best = matches[0]
        confidence = best.get("confidence", 0.0) * best.get("match_score", 1.0)

        recommendation = self._build_recommendation(
            best["strategy_type"], best["avg_lift"], best["win_rate"], confidence
        )

        return {
            "mode":              "archetype_match",
            "proposed_strategy": ctx.get("strategy_type"),
            "best_match":        best["name"],
            "match_score":       best.get("match_score", 0),
            "predicted_lift":    round(best["avg_lift"], 4),
            "predicted_risk":    round(best.get("avg_risk", 0.0), 4),
            "win_rate":          round(best["win_rate"], 4),
            "confidence":        round(confidence, 4),
            "archetype_status":  best["status"],
            "bias_modifier":     best.get("bias_modifier", 0.0),
            "top_matches":       [{
                "name":       m["name"],
                "match_score":m.get("match_score", 0),
                "avg_lift":   m.get("avg_lift", 0),
                "win_rate":   m.get("win_rate", 0),
            } for m in matches],
            "recommendation":    recommendation,
            "simulated_at":      datetime.utcnow().isoformat(),
        }

    # ── Mode 2: Historical simulation ─────────────────────────────

    def _historical_sim(self, operator_id: str, company_id: str,
                         ctx: Dict[str, Any]) -> Dict[str, Any]:
        private_hits = self.private_mem.query_similar(operator_id, ctx, top_k=5)
        tenant_hits  = self.tenant_mem.query_similar(company_id, ctx, top_k=5, outcome_filter=None)

        all_hits = private_hits + tenant_hits
        if not all_hits:
            return self._no_data_report(ctx, "historical_sim")

        lifts     = [h["lift_delta"] for h in all_hits if h.get("lift_delta") is not None]
        wins      = [h for h in all_hits if h.get("outcome") == "win"]
        risks     = [h.get("risk_exposure", 0.0) for h in all_hits]

        if not lifts:
            return self._no_data_report(ctx, "historical_sim")

        avg_lift  = sum(lifts) / len(lifts)
        win_rate  = len(wins) / len(all_hits)
        avg_risk  = sum(risks) / len(risks)
        avg_sim   = sum(h.get("similarity", 0) for h in all_hits) / len(all_hits)
        confidence = win_rate * avg_sim     # joint confidence

        recommendation = self._build_recommendation(
            ctx.get("strategy_type", "unknown"), avg_lift, win_rate, confidence
        )

        return {
            "mode":              "historical_sim",
            "proposed_strategy": ctx.get("strategy_type"),
            "events_matched":    len(all_hits),
            "private_hits":      len(private_hits),
            "tenant_hits":       len(tenant_hits),
            "predicted_lift":    round(avg_lift, 4),
            "predicted_risk":    round(avg_risk, 4),
            "win_rate":          round(win_rate, 4),
            "avg_similarity":    round(avg_sim, 4),
            "confidence":        round(confidence, 4),
            "recommendation":    recommendation,
            "top_events":        [{
                "strategy_type": h.get("strategy_type"),
                "lift_delta":    h.get("lift_delta"),
                "outcome":       h.get("outcome"),
                "similarity":    h.get("similarity"),
            } for h in all_hits[:5]],
            "simulated_at":      datetime.utcnow().isoformat(),
        }

    # ── Mode 3: Stress test ────────────────────────────────────────

    def _stress_test(self, operator_id: str, company_id: str,
                      ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vary key stress variables across predefined envelope.
        Returns performance envelope to show CaptainStrategy
        at what signal levels this strategy becomes unsafe.
        """
        results = []
        for var, values in STRESS_VARS.items():
            for val in values:
                stressed = copy.deepcopy(ctx)
                stressed[var] = val

                # Quick archetype match for each stressed variant
                matches = self.archetypes.find_matching_archetypes(stressed, top_k=1)
                if matches:
                    m = matches[0]
                    results.append({
                        "var":          var,
                        "value":        val,
                        "predicted_lift": m["avg_lift"],
                        "win_rate":     m["win_rate"],
                        "confidence":   m["confidence"],
                        "safe":         m["win_rate"] >= 0.50 and m["avg_lift"] > -0.05,
                    })
                else:
                    results.append({
                        "var": var, "value": val,
                        "predicted_lift": 0.0, "win_rate": 0.0,
                        "confidence": 0.0, "safe": False,
                    })

        safe_count   = sum(1 for r in results if r["safe"])
        total        = len(results)
        safety_ratio = safe_count / total if total else 0.0

        return {
            "mode":              "stress_test",
            "proposed_strategy": ctx.get("strategy_type"),
            "safety_ratio":      round(safety_ratio, 4),
            "safe_scenarios":    safe_count,
            "total_scenarios":   total,
            "recommendation":    (
                "✅ Strategy is robust across signal envelope."
                if safety_ratio >= 0.65 else
                "⚠️ Strategy has material vulnerability in stressed scenarios — reduce exposure."
            ),
            "scenario_results":  results,
            "simulated_at":      datetime.utcnow().isoformat(),
        }

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _build_recommendation(strategy: str, avg_lift: float,
                                win_rate: float, confidence: float) -> str:
        if win_rate >= 0.70 and avg_lift > 0.05 and confidence >= 0.60:
            return (f"PROCEED: Historical data strongly supports '{strategy}'. "
                    f"Expected lift {avg_lift:+.1%}, win rate {win_rate:.0%}.")
        elif win_rate >= 0.50 and avg_lift > 0:
            return (f"PROCEED WITH MONITORING: '{strategy}' has moderate support. "
                    f"Expected lift {avg_lift:+.1%}, win rate {win_rate:.0%}. "
                    f"Confidence {confidence:.0%} — increase observation frequency.")
        elif avg_lift < -0.05:
            return (f"CAUTION: '{strategy}' has historically produced negative lift "
                    f"({avg_lift:+.1%}) in similar contexts. Consider alternative.")
        else:
            return (f"INSUFFICIENT DATA: '{strategy}' has limited history in this context. "
                    f"Consider sandbox test first.")

    @staticmethod
    def _no_data_report(ctx: Dict, mode: str) -> Dict[str, Any]:
        return {
            "mode": mode,
            "proposed_strategy": ctx.get("strategy_type"),
            "events_matched":    0,
            "predicted_lift":    0.0,
            "confidence":        0.0,
            "recommendation":    "NO_DATA: No historical reference found. Recommend sandbox test at reduced scale.",
            "simulated_at":      datetime.utcnow().isoformat(),
        }
