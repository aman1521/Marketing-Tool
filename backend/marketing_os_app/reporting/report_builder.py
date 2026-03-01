import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Assembles structured report payloads for PDF generation.
    Output is a structured dict that can be rendered by any PDF engine
    (e.g. ReportLab, WeasyPrint, Playwright headless).
    """

    def build_executive_report(self, company_id: str,
                                 impact_data: Dict[str, Any],
                                 risk_data: Dict[str, Any],
                                 usage_data: Dict[str, Any],
                                 dsi_data: Dict[str, Any],
                                 period: str = "Monthly") -> Dict[str, Any]:
        return {
            "report_type": "Executive AI Performance Report",
            "company_id": company_id,
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {
                "ai_impact": {
                    "roi_delta_vs_baseline_pct": impact_data.get("roi_delta_vs_baseline_pct"),
                    "cpa_improvement_pct":        impact_data.get("cpa_improvement_pct"),
                    "fatigue_recovery_speed_pct": impact_data.get("fatigue_recovery_speed_gain_pct"),
                    "experiment_lift_rate_pct":   impact_data.get("experiment_lift_rate_pct"),
                    "autonomy_precision_score":   impact_data.get("autonomy_precision_score"),
                    "manual_decisions_replaced":  impact_data.get("manual_decisions_replaced")
                },
                "capital_risk": {
                    "total_capital_at_risk":     risk_data.get("total_capital_at_risk"),
                    "worst_case_downside":        risk_data.get("worst_case_downside"),
                    "cross_campaign_exposure":    risk_data.get("cross_campaign_exposure"),
                    "volatility_adjusted_index":  risk_data.get("volatility_adjusted_risk_index"),
                    "autonomy_exposure_pct":      risk_data.get("autonomy_exposure_pct")
                },
                "autonomy_summary": {
                    "executions_count":           usage_data.get("executions_count"),
                    "escalations_triggered":      usage_data.get("escalations_triggered"),
                    "calibration_runs":           usage_data.get("calibration_runs"),
                    "autonomy_percentage":        usage_data.get("autonomy_percentage"),
                    "avg_approval_latency_min":   usage_data.get("avg_approval_latency_minutes")
                },
                "decision_speed": {
                    "dsi_7day_avg":          dsi_data.get("dsi_7day_avg"),
                    "dsi_30day_avg":         dsi_data.get("dsi_30day_avg"),
                    "trend":                 dsi_data.get("trend"),
                    "approval_latency_by_role": dsi_data.get("approval_latency_by_role_minutes")
                },
                "system_health": {
                    "drift_incidents":    impact_data.get("drift_incidents"),
                    "rollback_count":     usage_data.get("rollbacks", 0),
                    "false_scaling_blocked": impact_data.get("false_scaling_blocked")
                }
            }
        }

    def build_autonomy_report(self, company_id: str,
                               history: List[Dict[str, Any]],
                               current_pct: float,
                               period: str = "Monthly") -> Dict[str, Any]:
        return {
            "report_type": "Autonomy Level Report",
            "company_id": company_id,
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "current_autonomy_pct": current_pct,
            "adjustment_history": history,
            "summary": {
                "total_adjustments": len(history),
                "reductions": len([h for h in history if h.get("delta", 0) < 0]),
                "expansions": len([h for h in history if h.get("delta", 0) > 0])
            }
        }
