import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CrossTenantDashboard:
    """
    Agency-level aggregated view. Tenant isolation intact.
    Only anonymized, aggregated metrics exposed. No company-level PII.
    """

    def aggregate(self, tenant_snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        tenant_snapshots: list of per-tenant risk/usage/performance snapshots.
        No company_id exposed in output.
        """
        if not tenant_snapshots:
            return {}

        n = len(tenant_snapshots)

        total_capital_at_risk = sum(t.get("total_capital_at_risk", 0) for t in tenant_snapshots)
        avg_autonomy_pct = sum(t.get("autonomy_exposure_pct", 0) for t in tenant_snapshots) / n
        avg_drift_freq = sum(t.get("drift_frequency", 0) for t in tenant_snapshots) / n
        avg_roi_delta = sum(t.get("roi_delta_pct", 0) for t in tenant_snapshots) / n
        total_escalations = sum(t.get("escalations_triggered", 0) for t in tenant_snapshots)

        # Volatility distribution bucket
        vol_buckets = {"low": 0, "medium": 0, "high": 0}
        for t in tenant_snapshots:
            v = t.get("volatility_index", 0)
            if v < 0.3:   vol_buckets["low"] += 1
            elif v < 0.6: vol_buckets["medium"] += 1
            else:          vol_buckets["high"] += 1

        # ROI leaderboard (anonymized rank)
        ranked = sorted(
            [{"rank": i+1, "roi_delta_pct": t.get("roi_delta_pct", 0)}
             for i, t in enumerate(sorted(tenant_snapshots,
                                           key=lambda x: x.get("roi_delta_pct", 0),
                                           reverse=True))],
            key=lambda x: x["rank"]
        )

        return {
            "tenant_count": n,
            "total_capital_at_risk_usd": round(total_capital_at_risk, 2),
            "avg_autonomy_pct": round(avg_autonomy_pct, 2),
            "avg_drift_frequency": round(avg_drift_freq, 4),
            "avg_roi_delta_pct": round(avg_roi_delta, 2),
            "total_escalations": total_escalations,
            "volatility_distribution": vol_buckets,
            "roi_delta_leaderboard": ranked[:10]   # Top 10 anonymized
        }


class ExposureStackAnalyzer:
    """
    Computes total risk stacking across all managed tenants.
    Essential for agency-level capital management.
    """

    def analyze(self, tenant_snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        exposures = [t.get("total_capital_at_risk", 0) for t in tenant_snapshots]
        total = sum(exposures)
        worst = max(exposures) if exposures else 0
        concentration = round(worst / max(total, 1), 4)

        return {
            "total_exposure_usd": round(total, 2),
            "single_tenant_worst_case": round(worst, 2),
            "concentration_ratio": concentration,
            "over_concentrated": concentration > 0.4
        }


class DriftComparator:
    """Compares drift frequency across tenants grouped by industry."""

    def compare(self, tenant_snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        industry_map: Dict[str, List[float]] = {}
        for t in tenant_snapshots:
            ind = t.get("industry", "unknown")
            df  = t.get("drift_frequency", 0)
            industry_map.setdefault(ind, []).append(df)

        return {
            ind: {"avg_drift": round(sum(vals)/len(vals), 4), "count": len(vals)}
            for ind, vals in industry_map.items()
        }


class AutonomyPerformanceRanker:
    """Ranks tenants by autonomy efficiency (ROI delta per autonomy % unit)."""

    def rank(self, tenant_snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for i, t in enumerate(tenant_snapshots):
            auto = t.get("autonomy_exposure_pct", 1.0)
            roi  = t.get("roi_delta_pct", 0.0)
            efficiency = round(roi / max(auto, 0.01), 4)
            scored.append({"rank_position": 0, "autonomy_efficiency": efficiency,
                           "roi_delta_pct": roi, "autonomy_pct": auto})

        scored.sort(key=lambda x: x["autonomy_efficiency"], reverse=True)
        for i, s in enumerate(scored):
            s["rank_position"] = i + 1
        return scored
