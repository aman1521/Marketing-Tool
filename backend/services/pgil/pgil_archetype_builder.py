"""
PGIL Archetype Builder
======================
Crystallises validated/dominant PGIL patterns into named Strategy Archetypes.

Archetype elevation criteria:
  CANDIDATE  → pattern status ≥ validated + confidence ≥ 0.60
  CONFIRMED  → sample_count ≥ 15 + confidence ≥ 0.70 + win_rate ≥ 0.60
  RETIRED    → win_rate drops below 0.35 with sample_count > 15

Cross-industry archetypes:
  Patterns spanning ≥ 3 industries are elevated to UNIVERSAL archetypes
  with a higher bias modifier (+0.02 bonus per extra industry).

Archetype outputs fed to PGILInfluenceController:
  - bias_modifier ∈ [-0.10, +0.15]
  - lift_prior    (Bayesian prior lift estimate)
  - risk_prior    (Bayesian prior risk estimate)
  - confidence    (statistical backing score)
"""

import math
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .pgil_vector_store import PGILVectorStore

logger = logging.getLogger(__name__)

CANDIDATE_CONF  = 0.60
CONFIRMED_MIN_N = 15
CONFIRMED_CONF  = 0.70
CONFIRMED_WR    = 0.60
RETIRED_WR      = 0.35
RETIRED_MIN_N   = 15

CROSS_INDUSTRY_THRESHOLD = 3   # industries to qualify as UNIVERSAL

MAX_BIAS        =  0.15
MIN_BIAS        = -0.10
UNIVERSAL_BONUS =  0.02

_archetypes: Dict[str, Dict] = {}   # keyed by archetype id


class PGILArchetypeBuilder:
    """
    Converts validated PGIL patterns into operator-accessible strategy archetypes.
    """

    def __init__(self, vector_store: Optional[PGILVectorStore] = None):
        self.vs = vector_store or PGILVectorStore()

    # ── Build from patterns ───────────────────────────────────────────────

    def build_from_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """
        Ingest a list of PGILPattern dicts and create / update archetypes.
        Returns full current archetype list.
        """
        created = updated = 0

        for p in patterns:
            if p.get("confidence", 0) < CANDIDATE_CONF:
                continue
            fp = p.get("fingerprint", "")
            existing = self._find_by_fingerprint(fp)
            if existing:
                self._update(existing, p)
                updated += 1
            else:
                arch = self._create(p)
                _archetypes[arch["id"]] = arch
                self.vs.upsert_archetype(arch)
                created += 1

        logger.info(f"[PGIL Archetype] Built: created={created} updated={updated}")
        return list(_archetypes.values())

    def build_from_cross_industry(self,
                                   cross_patterns: List[Dict]) -> List[Dict]:
        """
        Elevate cross-industry patterns to UNIVERSAL archetypes.
        cross_patterns from PGILPatternEngine.get_cross_industry_patterns()
        """
        for cp in cross_patterns:
            if cp.get("industry_coverage", 0) < CROSS_INDUSTRY_THRESHOLD:
                continue
            base = cp["base_key"]
            existing = self._find_by_base(base)
            if existing:
                existing["industry_coverage"] = cp["industry_coverage"]
                existing["sample_count"]      = cp["sample_count"]
                existing["archetype_tier"]    = "UNIVERSAL"
                bias_bonus = UNIVERSAL_BONUS * max(0, cp["industry_coverage"] - CROSS_INDUSTRY_THRESHOLD)
                existing["bias_modifier"] = min(MAX_BIAS, existing["bias_modifier"] + bias_bonus)
                existing["last_updated"]  = datetime.utcnow().isoformat()
            else:
                arch = self._create_universal(cp)
                _archetypes[arch["id"]] = arch
                self.vs.upsert_archetype(arch)

        return list(_archetypes.values())

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def run_lifecycle(self) -> Dict[str, int]:
        """Promote candidates → confirmed, retire underperformers."""
        promoted = retired = 0
        for arch in _archetypes.values():
            old = arch["status"]
            new = self._compute_status(arch)
            if new != old:
                arch["status"]        = new
                arch["bias_modifier"] = self._compute_bias(arch) if new == "confirmed" else 0.0
                arch["lift_prior"]    = arch["avg_lift"] if new == "confirmed" else 0.0
                arch["risk_prior"]    = arch["avg_risk"]
                arch["last_updated"]  = datetime.utcnow().isoformat()
                self.vs.upsert_archetype(arch)
                if new == "confirmed":
                    promoted += 1
                    logger.info(
                        f"[PGIL Archetype] CONFIRMED [{arch['name']}] "
                        f"n={arch['sample_count']} conf={arch['confidence']:.2f} "
                        f"bias={arch['bias_modifier']:+.3f}"
                    )
                elif new == "retired":
                    retired += 1
                    logger.info(f"[PGIL Archetype] RETIRED [{arch['name']}]")
        return {"promoted": promoted, "retired": retired, "total": len(_archetypes)}

    # ── Query ─────────────────────────────────────────────────────────────

    def get_confirmed(self) -> List[Dict]:
        return [a for a in _archetypes.values() if a["status"] == "confirmed"]

    def find_matching(self, context: Dict[str, Any], top_k: int = 3) -> List[Dict]:
        """Find confirmed archetypes matching current strategy context."""
        confirmed = self.get_confirmed()
        if not confirmed:
            return []
        hits = self.vs.search_matching_archetypes(context, top_k=top_k, score_threshold=0.60)
        result = []
        for h in hits:
            aid = h["payload"].get("id","")
            if aid in _archetypes and _archetypes[aid]["status"] == "confirmed":
                result.append({**_archetypes[aid], "match_score": h["score"]})
        return result[:top_k]

    def get_all(self) -> List[Dict]:
        return list(_archetypes.values())

    def summary(self) -> Dict[str, Any]:
        archs = list(_archetypes.values())
        return {
            "total":     len(archs),
            "by_status": {s: sum(1 for a in archs if a["status"]==s)
                          for s in ("candidate","confirmed","retired")},
            "universal": sum(1 for a in archs if a.get("archetype_tier")=="UNIVERSAL"),
        }

    # ── Internal factories ────────────────────────────────────────────────

    def _create(self, p: Dict) -> Dict:
        strategy = p.get("strategy_type",    "default")
        industry = p.get("industry_bucket",  "other")
        funnel   = p.get("funnel_stage",     "mofu")
        cluster  = p.get("creative_cluster", "other")
        scaling  = p.get("scaling_band",     "growth")
        vol      = p.get("volatility_band",  "medium")
        n        = p.get("sample_count",     1)
        avg_lift = p.get("avg_lift",         0.0)
        avg_risk = p.get("avg_risk",         0.0)
        win_rate = p.get("win_rate",         0.0)
        conf     = p.get("confidence",       0.0)

        status = self._compute_status({
            "sample_count": n, "confidence": conf, "win_rate": win_rate
        })

        return {
            "id":               str(uuid.uuid4()),
            "name":             self._name(strategy, industry, funnel, cluster),
            "description":      self._describe(strategy, industry, funnel, avg_lift, win_rate),
            "archetype_tier":   "INDUSTRY",   # vs UNIVERSAL
            "strategy_type":    strategy,
            "industry_bucket":  industry,
            "funnel_stage":     funnel,
            "creative_cluster": cluster,
            "scaling_band":     scaling,
            "volatility_band":  vol,
            "sample_count":     n,
            "avg_lift":         round(avg_lift, 4),
            "avg_risk":         round(avg_risk, 4),
            "win_rate":         round(win_rate, 4),
            "confidence":       round(conf, 4),
            "industry_coverage":1,
            "bias_modifier":    self._compute_bias({"avg_lift": avg_lift, "win_rate": win_rate, "confidence": conf}),
            "lift_prior":       round(avg_lift, 4) if status == "confirmed" else 0.0,
            "risk_prior":       round(avg_risk, 4),
            "status":           status,
            "fingerprint":      p.get("fingerprint", ""),
            "pattern_ids":      [p.get("id", "")],
            "created_at":       datetime.utcnow().isoformat(),
            "last_updated":     datetime.utcnow().isoformat(),
        }

    def _create_universal(self, cp: Dict) -> Dict:
        group    = cp.get("source_patterns", [{}])
        strategy = group[0].get("strategy_type", "default") if group else "default"
        n        = cp.get("sample_count", 0)
        avg_lift = cp.get("avg_lift", 0.0)
        avg_wr   = cp.get("avg_win_rate", 0.0)
        coverage = cp.get("industry_coverage", CROSS_INDUSTRY_THRESHOLD)

        bias = min(MAX_BIAS, self._compute_bias({"avg_lift":avg_lift,"win_rate":avg_wr,"confidence":0.65})
                   + UNIVERSAL_BONUS * (coverage - CROSS_INDUSTRY_THRESHOLD))

        return {
            "id":               str(uuid.uuid4()),
            "name":             f"Universal: {strategy.replace('_',' ').title()} Across {coverage} Industries",
            "description":      (
                f"Cross-industry pattern spanning {cp.get('industries',[])}. "
                f"Strategy '{strategy}' consistently outperforms with avg lift {avg_lift:+.1%}."
            ),
            "archetype_tier":   "UNIVERSAL",
            "strategy_type":    strategy,
            "industry_bucket":  None,
            "funnel_stage":     group[0].get("funnel_stage", "mofu") if group else "mofu",
            "creative_cluster": group[0].get("creative_cluster","other") if group else "other",
            "scaling_band":     group[0].get("scaling_band","growth") if group else "growth",
            "volatility_band":  group[0].get("volatility_band","medium") if group else "medium",
            "sample_count":     n,
            "avg_lift":         round(avg_lift, 4),
            "avg_risk":         0.0,
            "win_rate":         round(avg_wr, 4),
            "confidence":       0.65,
            "industry_coverage":coverage,
            "bias_modifier":    round(bias, 4),
            "lift_prior":       round(avg_lift, 4),
            "risk_prior":       0.0,
            "status":           "confirmed",
            "fingerprint":      cp.get("base_key",""),
            "pattern_ids":      cp.get("component_patterns", []),
            "created_at":       datetime.utcnow().isoformat(),
            "last_updated":     datetime.utcnow().isoformat(),
        }

    def _update(self, arch: Dict, p: Dict):
        n = arch["sample_count"] + p.get("sample_count", 1)
        arch["avg_lift"]    = round((arch["avg_lift"]*arch["sample_count"] + p.get("avg_lift",0)*p.get("sample_count",1))/n, 4)
        arch["avg_risk"]    = round((arch["avg_risk"]*arch["sample_count"] + p.get("avg_risk",0)*p.get("sample_count",1))/n, 4)
        arch["sample_count"]= n
        arch["win_rate"]    = round((arch["win_rate"]*(n-p.get("sample_count",1)) + p.get("win_rate",0)*p.get("sample_count",1))/n, 4)
        arch["confidence"]  = p.get("confidence", arch["confidence"])
        arch["last_updated"]= datetime.utcnow().isoformat()
        if p.get("id"):
            arch.setdefault("pattern_ids", []).append(p["id"])
        self.vs.upsert_archetype(arch)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_by_fingerprint(self, fp: str) -> Optional[Dict]:
        for a in _archetypes.values():
            if a.get("fingerprint") == fp:
                return a
        return None

    def _find_by_base(self, base: str) -> Optional[Dict]:
        for a in _archetypes.values():
            if a.get("fingerprint") == base and a.get("archetype_tier") == "UNIVERSAL":
                return a
        return None

    @staticmethod
    def _compute_status(arch: Dict) -> str:
        n    = arch.get("sample_count", 0)
        conf = arch.get("confidence",   0)
        wr   = arch.get("win_rate",     0)
        if n > RETIRED_MIN_N and wr < RETIRED_WR:
            return "retired"
        if n >= CONFIRMED_MIN_N and conf >= CONFIRMED_CONF and wr >= CONFIRMED_WR:
            return "confirmed"
        return "candidate"

    @staticmethod
    def _compute_bias(arch: Dict) -> float:
        lift = arch.get("avg_lift", 0.0)
        wr   = arch.get("win_rate", 0.0)
        conf = arch.get("confidence", 0.0)
        perf = lift * 0.50 + (wr - 0.50) * 0.35 + conf * 0.15
        bias = perf * MAX_BIAS if perf >= 0 else perf * abs(MIN_BIAS)
        return round(max(MIN_BIAS, min(MAX_BIAS, bias)), 4)

    @staticmethod
    def _name(strategy: str, industry: str, funnel: str, cluster: str) -> str:
        return (
            f"{strategy.replace('_',' ').title()} | "
            f"{industry.title()} | "
            f"{funnel.upper()} | "
            f"{cluster.title()} Creative"
        )

    @staticmethod
    def _describe(strategy, industry, funnel, lift, wr) -> str:
        return (
            f"Strategy '{strategy}' in {industry} targeting {funnel} stage. "
            f"Cross-tenant avg lift {lift:+.1%}, win rate {wr:.0%}."
        )
