"""
Archetype Builder
=================
Detects repeating success patterns across all three memory tiers
and crystallises them into named Strategy Archetypes.

Archetype lifecycle:
  CANDIDATE  → 3+ occurrences with positive lift
  CONFIRMED  → 7+ occurrences AND statistical confidence > 0.65
  DEPRECATED → win rate drops below 0.35 over last 10 events

Archetypes are the "institutional memory" of the platform.
They bias Captain Strategy decisions via the InfluenceController.
"""

import logging
import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .context_vectorizer import ContextVectorizer

logger = logging.getLogger(__name__)

_archetypes: List[Dict] = []

# Lifecycle thresholds
CANDIDATE_MIN_SAMPLES  = 3
CONFIRMED_MIN_SAMPLES  = 7
CONFIRMED_MIN_CONF     = 0.65
DEPRECATED_WIN_RATE    = 0.35
MAX_BIAS_MODIFIER      = 0.15
MIN_BIAS_MODIFIER      = -0.10


class ArchetypeBuilder:
    """
    Converts repeating strategy patterns into validated archetypes.
    Consumes pattern lists from TenantMemoryEngine and GlobalMemoryEngine.
    """

    def __init__(self):
        self.vectorizer = ContextVectorizer()

    # ── Build archetypes from tenant patterns ─────────────────────

    def build_from_tenant_patterns(self, patterns: List[Dict],
                                    tier: str = "tenant") -> List[Dict]:
        """
        Takes repeating pattern dicts from TenantMemoryEngine.get_repeating_patterns()
        and creates or updates archetypes.
        """
        created, updated = 0, 0
        for pattern in patterns:
            fp = pattern["fingerprint"]
            existing = self._find_by_fingerprint(fp)

            if existing:
                self._update_archetype(existing, pattern)
                updated += 1
            else:
                arch = self._create_archetype(pattern, tier)
                _archetypes.append(arch)
                created += 1

        logger.info(f"[ArchetypeBuilder] Created={created} Updated={updated} from {tier} patterns")
        return _archetypes

    def build_from_global_patterns(self, global_patterns: List[Dict]) -> List[Dict]:
        """Process globally-validated patterns into archetypes."""
        for pat in global_patterns:
            if pat.get("confidence", 0) < CONFIRMED_MIN_CONF:
                continue   # Only elevate high-confidence global patterns
            fp = pat.get("fingerprint", "")
            existing = self._find_by_fingerprint(fp)
            if existing:
                self._update_archetype(existing, pat)
            else:
                _archetypes.append(self._create_archetype(pat, tier="global"))
        return _archetypes

    # ── Lifecycle management ─────────────────────────────────────

    def run_lifecycle(self) -> Dict[str, int]:
        """Promote candidates → confirmed, deprecate underperformers."""
        promoted, deprecated = 0, 0
        for arch in _archetypes:
            if arch["status"] == "candidate":
                if (arch["sample_count"] >= CONFIRMED_MIN_SAMPLES
                        and arch["confidence"] >= CONFIRMED_MIN_CONF):
                    arch["status"] = "confirmed"
                    arch["bias_modifier"] = self._compute_bias(arch)
                    promoted += 1
                    logger.info(f"[Archetype] PROMOTED [{arch['name']}] bias={arch['bias_modifier']:+.3f}")

            elif arch["status"] == "confirmed":
                if arch["win_rate"] < DEPRECATED_WIN_RATE and arch["sample_count"] > 10:
                    arch["status"] = "deprecated"
                    arch["bias_modifier"] = 0.0
                    deprecated += 1
                    logger.info(f"[Archetype] DEPRECATED [{arch['name']}]")

        return {"promoted": promoted, "deprecated": deprecated, "total": len(_archetypes)}

    # ── Query ─────────────────────────────────────────────────────

    def get_confirmed_archetypes(self) -> List[Dict]:
        return [a for a in _archetypes if a["status"] == "confirmed"]

    def find_matching_archetypes(self, context: Dict[str, Any],
                                  top_k: int = 3) -> List[Dict]:
        """Find confirmed archetypes that match the current context."""
        if not _archetypes:
            return []
        ctx_vec = self.vectorizer.to_feature_vector(context)
        confirmed = [a for a in _archetypes if a["status"] == "confirmed"]
        scored = []
        for arch in confirmed:
            a_vec = self.vectorizer.to_feature_vector(arch.get("representative_context", context))
            sim   = self._cosine(ctx_vec, a_vec)
            scored.append({**arch, "match_score": round(sim, 4)})
        scored.sort(key=lambda x: -x["match_score"])
        return scored[:top_k]

    def get_all_archetypes(self) -> List[Dict]:
        return list(_archetypes)

    # ── Internal factory ─────────────────────────────────────────

    def _create_archetype(self, pattern: Dict, tier: str) -> Dict:
        strategy = pattern.get("strategy_type", "unknown")
        industry = pattern.get("industry",      pattern.get("industry_bucket", "other"))
        aov      = pattern.get("aov_tier",      "mid")
        band     = pattern.get("scaling_band",  "growth")
        occ      = pattern.get("occurrences",   pattern.get("sample_count", 1))
        avg_lift = pattern.get("avg_lift", 0.0)
        win_rate = pattern.get("win_rate", 1.0 if avg_lift > 0 else 0.0)

        name = f"{strategy.replace('_',' ').title()} | {industry.title()} | {aov.upper()} AOV"
        conf = self._wilson_lower(int(win_rate * occ), occ)
        status = "confirmed" if occ >= CONFIRMED_MIN_SAMPLES and conf >= CONFIRMED_MIN_CONF else "candidate"

        rep_ctx = {
            "strategy_type":   strategy,
            "industry_bucket": industry,
            "aov_tier":        aov,
            "scaling_band":    band,
            "outcome":         "win",
        }

        return {
            "id":                     str(uuid.uuid4()),
            "name":                   name,
            "tier":                   tier,
            "strategy_type":          strategy,
            "industry_bucket":        industry,
            "aov_tier":               aov,
            "scaling_band":           band,
            "avg_lift":               round(avg_lift, 4),
            "avg_risk":               pattern.get("avg_risk", 0.0),
            "win_rate":               round(win_rate, 4),
            "sample_count":           occ,
            "confidence":             conf,
            "bias_modifier":          self._compute_bias({"win_rate": win_rate, "avg_lift": avg_lift, "confidence": conf}) if status == "confirmed" else 0.0,
            "status":                 status,
            "fingerprint":            pattern.get("fingerprint", ""),
            "representative_context": rep_ctx,
            "description":            self._describe(strategy, industry, aov, avg_lift, win_rate),
            "created_at":             datetime.utcnow().isoformat(),
            "last_updated":           datetime.utcnow().isoformat(),
        }

    def _update_archetype(self, arch: Dict, pattern: Dict):
        n = arch["sample_count"] + pattern.get("occurrences", 1)
        new_lift = pattern.get("avg_lift", 0.0)
        arch["avg_lift"]    = round((arch["avg_lift"] * arch["sample_count"] + new_lift) / n, 4)
        arch["sample_count"] = n
        arch["win_rate"]    = round(
            (arch["win_rate"] * (n-1) + pattern.get("win_rate", 1.0)) / n, 4
        )
        arch["confidence"]  = self._wilson_lower(int(arch["win_rate"] * n), n)
        arch["last_updated"] = datetime.utcnow().isoformat()

    def _find_by_fingerprint(self, fingerprint: str) -> Optional[Dict]:
        for a in _archetypes:
            if a.get("fingerprint") == fingerprint:
                return a
        return None

    # ── Bias & scoring ───────────────────────────────────────────

    def _compute_bias(self, arch: Dict) -> float:
        """
        Compute bias_modifier ∈ [-0.10, +0.15].
        Positive lift + high win rate → positive bias.
        Formula: scale performance above neutral (win_rate 0.5, lift 0)
                 to the allowed bias range.
        """
        lift     = arch.get("avg_lift", 0.0)
        win_rate = arch.get("win_rate", 0.0)
        conf     = arch.get("confidence", 0.0)

        # Performance above neutral: 0 = neutral, +1 = perfect
        perf = (lift * 0.50) + ((win_rate - 0.50) * 0.35) + (conf * 0.15)
        # Scale to bias range: perf > 0 → positive bias, perf < 0 → negative
        if perf >= 0:
            bias = perf * MAX_BIAS_MODIFIER
        else:
            bias = perf * abs(MIN_BIAS_MODIFIER)
        return round(max(MIN_BIAS_MODIFIER, min(MAX_BIAS_MODIFIER, bias)), 4)

    @staticmethod
    def _wilson_lower(wins: int, n: int, z: float = 1.645) -> float:
        if n == 0:
            return 0.0
        phat   = wins / n
        denom  = 1 + z**2 / n
        centre = phat + z**2 / (2 * n)
        spread = z * math.sqrt(max(0, phat*(1-phat)/n + z**2/(4*n**2)))
        return round(max(0.0, (centre - spread) / denom), 4)

    @staticmethod
    def _describe(strategy: str, industry: str, aov: str,
                   avg_lift: float, win_rate: float) -> str:
        return (
            f"'{strategy}' applied in {industry} with {aov.upper()} AOV context. "
            f"Historical avg lift {avg_lift:+.1%}, win rate {win_rate:.0%}."
        )

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot    = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
