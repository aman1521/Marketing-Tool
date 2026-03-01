import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIImpactEngine:
    """
    Quantifies the measurable impact of the Intelligence OS vs baseline human operations.
    Exposed in Executive View and Alpha Cockpit.
    """

    def compute_impact(self, baseline_metrics: Dict[str, Any],
                        live_metrics: Dict[str, Any],
                        usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        baseline_metrics: {roas, cpa, fatigue_recovery_days, experiment_velocity}
        live_metrics: {roas, cpa, fatigue_recovery_days, experiment_velocity, drift_incidents}
        """
        baseline_roas = baseline_metrics.get("roas", 1.0)
        live_roas = live_metrics.get("roas", 1.0)
        roi_delta_pct = round(((live_roas - baseline_roas) / max(baseline_roas, 0.01)) * 100, 2)

        baseline_cpa = baseline_metrics.get("cpa", 100.0)
        live_cpa = live_metrics.get("cpa", 100.0)
        cpa_improvement_pct = round(((baseline_cpa - live_cpa) / max(baseline_cpa, 0.01)) * 100, 2)

        baseline_fatigue = baseline_metrics.get("fatigue_recovery_days", 14.0)
        live_fatigue = live_metrics.get("fatigue_recovery_days", 14.0)
        fatigue_speed_gain_pct = round(((baseline_fatigue - live_fatigue) / max(baseline_fatigue, 0.01)) * 100, 2)

        baseline_exp_velocity = baseline_metrics.get("experiment_velocity", 1)
        live_exp_velocity = live_metrics.get("experiment_velocity", 1)
        experiment_lift_rate = round(((live_exp_velocity - baseline_exp_velocity) / max(baseline_exp_velocity, 1)) * 100, 2)

        autonomy_pct = usage_data.get("autonomy_percentage", 0.0)
        executions = usage_data.get("executions_count", 0)
        escalations = usage_data.get("escalations_triggered", 0)
        total_decisions = max(executions + escalations, 1)
        autonomy_precision = round(((executions - usage_data.get("rollbacks", 0)) / max(executions, 1)) * 100, 2)

        return {
            "roi_delta_vs_baseline_pct": roi_delta_pct,
            "cpa_improvement_pct": cpa_improvement_pct,
            "fatigue_recovery_speed_gain_pct": fatigue_speed_gain_pct,
            "experiment_lift_rate_pct": experiment_lift_rate,
            "autonomy_coverage_pct": autonomy_pct,
            "autonomy_precision_score": autonomy_precision,
            "drift_incidents": live_metrics.get("drift_incidents", 0),
            "false_scaling_blocked": escalations,
            "manual_decisions_replaced": executions
        }
