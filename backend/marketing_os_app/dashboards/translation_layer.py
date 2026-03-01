import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# TRANSLATION LAYER
# Converts raw AI engine output into human-readable summaries
# across 3 distinct audience modes.
# ──────────────────────────────────────────────

class TranslationLayer:

    def translate(self, raw_signals: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        mode: "simple" | "pro" | "executive"
        """
        if mode == "simple":
            return self._simple_mode(raw_signals)
        elif mode == "pro":
            return self._pro_mode(raw_signals)
        elif mode == "executive":
            return self._executive_mode(raw_signals)
        return raw_signals

    def _simple_mode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Layman-readable. No technical terms."""
        risk = data.get("system_risk_exposure_score", 0.0)
        drift = data.get("drift_frequency", 0.0)
        return {
            "what_changed_today": "The AI reviewed your campaigns and made small budget adjustments to improve results.",
            "what_ai_did": f"Optimized {data.get('executions_count', 0)} campaigns automatically.",
            "what_risk_exists": "Low risk" if risk < 0.3 else ("Some risk — being monitored" if risk < 0.6 else "Elevated risk — review suggested"),
            "what_requires_attention": data.get("pending_tasks_summary", "Nothing urgent right now."),
            "ai_impact_summary": f"Estimated savings vs manual management this week: {data.get('estimated_lift_usd', '$0')}."
        }

    def _pro_mode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Marketer-level. Metrics with context."""
        return {
            "execution_summary": {
                "actions_taken": data.get("executions_count", 0),
                "rollbacks": data.get("rollback_count", 0),
                "drift_incidents": data.get("drift_incidents", 0)
            },
            "creative_layer": {
                "fatigue_detected": data.get("fatigued_creatives", 0),
                "experiments_active": data.get("active_experiments", 0),
                "top_hook_strength": data.get("top_hook_strength", "N/A")
            },
            "risk_summary": {
                "autonomy_stability": data.get("autonomy_stability_index", 0.0),
                "risk_score": data.get("system_risk_exposure_score", 0.0),
                "confidence_avg": data.get("confidence_average", 0.0)
            },
            "pending": {
                "escalations": data.get("pending_escalations", 0),
                "calibration_proposals": data.get("pending_calibration_suggestions", 0)
            }
        }

    def _executive_mode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Business owner. Capital, ROI, risk only."""
        return {
            "capital_at_risk": data.get("total_capital_at_risk", 0.0),
            "worst_case_exposure": data.get("worst_case_downside", 0.0),
            "roi_delta_vs_baseline": data.get("roi_delta_pct", "N/A"),
            "autonomy_coverage_pct": data.get("autonomy_exposure_pct", 0.0),
            "decisions_avoided_manually": data.get("executions_count", 0),
            "escalations_pending_review": data.get("pending_escalations", 0),
            "system_health": "Stable" if data.get("system_risk_exposure_score", 0) < 0.4 else "Monitoring Required"
        }
