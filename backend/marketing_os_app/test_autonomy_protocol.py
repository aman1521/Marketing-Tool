"""
Autonomy Controller Stability Protocol — Full Test Suite
=========================================================
Covers all 6 simulation scenarios defined in the specification.
"""

import pytest
from backend.marketing_os_app.governance.autonomy_controller import (
    AutonomyController, Band, BAND_RANGES, THRESHOLDS
)

# ─── Factory helpers ─────────────────────────────────────────────────────────

def _ctrl() -> AutonomyController:
    return AutonomyController(db=None)

def _nominal() -> dict:
    """Healthy baseline metrics — no signals should trigger."""
    return {
        "drift_frequency":      0.05,
        "volatility_index":     0.20,
        "rollback_rate":        0.01,
        "roi_delta_48h":        0.05,
        "escalation_frequency": 0.05,
        "confidence_avg":       0.88,
        "confidence_trend":     "stable",
        "portfolio_exposure_pct": 30.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. VOLATILITY SPIKE
# ─────────────────────────────────────────────────────────────────────────────

class TestVolatilitySpike:
    def test_drops_exactly_one_band(self):
        ctrl = _ctrl()
        m = {**_nominal(), "volatility_index": 0.80}        # above 0.65 threshold
        result = ctrl.evaluate(50.0, m, "co_vol")           # start Balanced
        assert result["current_band"] == Band.CONSERVATIVE.value
        assert result["previous_band"] == Band.BALANCED.value

    def test_does_not_drop_two_bands_in_one_cycle(self):
        ctrl = _ctrl()
        m = {**_nominal(), "volatility_index": 0.95, "drift_frequency": 0.8}
        result = ctrl.evaluate(50.0, m, "co_vol2")
        # Must stay one band below Balanced, not two
        assert result["current_band"] in (Band.CONSERVATIVE.value,)

    def test_tightens_budget_limit(self):
        ctrl = _ctrl()
        m = {**_nominal(), "volatility_index": 0.80}
        result = ctrl.evaluate(50.0, m, "co_vol3")
        assert result["budget_change_limit_pct"] < 30.0

    def test_reduces_sandbox_allocation(self):
        ctrl = _ctrl()
        m = {**_nominal(), "volatility_index": 0.80}
        result = ctrl.evaluate(50.0, m, "co_vol4")
        assert result["sandbox_allocation_pct"] < 10.0

    def test_trigger_label_present(self):
        ctrl = _ctrl()
        m = {**_nominal(), "volatility_index": 0.80}
        result = ctrl.evaluate(50.0, m, "co_vol5")
        assert any("VOLATILITY_SPIKE" in t for t in result["triggers"])


# ─────────────────────────────────────────────────────────────────────────────
# 2. ROI DROP — stable signals → NO reduction
# ─────────────────────────────────────────────────────────────────────────────

class TestROIDrop:
    def test_significant_drop_with_stable_signals_does_not_reduce(self):
        """ROI is bad but drift+volatility are low → maintain, allow self-correction."""
        ctrl = _ctrl()
        m = {**_nominal(), "roi_delta_48h": -0.18, "drift_frequency": 0.05, "volatility_index": 0.20}
        result = ctrl.evaluate(50.0, m, "co_roi1")
        assert result["current_band"] == Band.BALANCED.value
        assert any("SIGNALS_NORMAL" in t for t in result["triggers"])

    def test_significant_drop_with_drift_corroboration_reduces(self):
        """ROI bad AND drift elevated → reduction applied."""
        ctrl = _ctrl()
        m = {**_nominal(), "roi_delta_48h": -0.18, "drift_frequency": 0.22, "volatility_index": 0.20}
        result = ctrl.evaluate(50.0, m, "co_roi2")
        assert result["new_pct"] < 50.0
        assert any("CORROBORATED" in t for t in result["triggers"])

    def test_moderate_drop_with_nominal_signals_is_monitoring_only(self):
        ctrl = _ctrl()
        m = {**_nominal(), "roi_delta_48h": -0.12}
        result = ctrl.evaluate(50.0, m, "co_roi3")
        # No band change, just a monitoring note
        assert result["current_band"] == Band.BALANCED.value
        assert any("MODERATE" in t or "monitoring" in t.lower() for t in result["triggers"])


# ─────────────────────────────────────────────────────────────────────────────
# 3. DRIFT SPIKE
# ─────────────────────────────────────────────────────────────────────────────

class TestDriftSpike:
    def test_drift_reduces_pct_within_band(self):
        ctrl = _ctrl()
        m = {**_nominal(), "drift_frequency": 0.45}
        result = ctrl.evaluate(55.0, m, "co_drift1")
        assert result["new_pct"] < 55.0

    def test_drift_does_not_cross_band_boundary(self):
        """Drift alone should stay within the current band, not trigger a band drop."""
        ctrl = _ctrl()
        m = {**_nominal(), "drift_frequency": 0.45}
        result = ctrl.evaluate(50.0, m, "co_drift2")
        lo, hi = BAND_RANGES[Band.BALANCED]
        assert lo <= result["new_pct"] <= hi

    def test_drift_trigger_label(self):
        ctrl = _ctrl()
        m = {**_nominal(), "drift_frequency": 0.50}
        result = ctrl.evaluate(55.0, m, "co_drift3")
        assert any("DRIFT_SPIKE" in t for t in result["triggers"])


# ─────────────────────────────────────────────────────────────────────────────
# 4. ROLLBACK SPIKE → STABILIZATION MODE
# ─────────────────────────────────────────────────────────────────────────────

class TestRollbackSpike:
    def test_rollback_enters_stabilization_mode(self):
        ctrl = _ctrl()
        m = {**_nominal(), "rollback_rate": 0.08}
        result = ctrl.evaluate(50.0, m, "co_rb1")
        assert result["stabilization_mode"] is True

    def test_rollback_drops_one_band(self):
        ctrl = _ctrl()
        m = {**_nominal(), "rollback_rate": 0.08}
        result = ctrl.evaluate(50.0, m, "co_rb2")
        assert result["current_band"] == Band.CONSERVATIVE.value

    def test_stabilization_exit_requires_7_consecutive_cycles(self):
        ctrl = _ctrl()
        rb_m   = {**_nominal(), "rollback_rate": 0.08}
        clean_m = {**_nominal()}  # all healthy

        ctrl.evaluate(50.0, rb_m, "co_rb3")   # enter stabilization
        for i in range(6):
            r = ctrl.evaluate(30.0, clean_m, "co_rb3")
        # After 6 cycles → still in stabilization
        assert r["stabilization_mode"] is True

        r = ctrl.evaluate(30.0, clean_m, "co_rb3")  # 7th cycle
        assert r["stabilization_mode"] is False

    def test_stabilization_reset_if_noise_returns(self):
        ctrl = _ctrl()
        rb_m   = {**_nominal(), "rollback_rate": 0.08}
        noisy_m = {**_nominal(), "volatility_index": 0.70}
        clean_m = {**_nominal()}

        ctrl.evaluate(50.0, rb_m, "co_rb4")     # enter mode
        for _ in range(5): ctrl.evaluate(30.0, clean_m, "co_rb4")  # 5 clean
        ctrl.evaluate(30.0, noisy_m, "co_rb4")  # noise resets counter
        for _ in range(6): ctrl.evaluate(30.0, clean_m, "co_rb4")  # 6 more clean
        r = ctrl.evaluate(30.0, clean_m, "co_rb4")
        # 7th clean after reset → exits now
        assert r["stabilization_mode"] is False

    def test_rollback_tightens_budget_limit(self):
        ctrl = _ctrl()
        m = {**_nominal(), "rollback_rate": 0.09}
        result = ctrl.evaluate(50.0, m, "co_rb5")
        assert result["budget_change_limit_pct"] < 30.0


# ─────────────────────────────────────────────────────────────────────────────
# 5. ESCALATION OVERLOAD
# ─────────────────────────────────────────────────────────────────────────────

class TestEscalationOverload:
    def test_widens_envelope_does_not_drop_band(self):
        """Escalation overload should widen envelope, NOT drop the band."""
        ctrl = _ctrl()
        m = {**_nominal(), "escalation_frequency": 0.30}
        result = ctrl.evaluate(50.0, m, "co_esc1")
        assert result["current_band"] == Band.BALANCED.value
        assert result["budget_change_limit_pct"] > 30.0

    def test_trigger_label_present(self):
        ctrl = _ctrl()
        m = {**_nominal(), "escalation_frequency": 0.30}
        result = ctrl.evaluate(50.0, m, "co_esc2")
        assert any("ESCALATION_OVERLOAD" in t for t in result["triggers"])

    def test_envelope_widened_message_present(self):
        ctrl = _ctrl()
        m = {**_nominal(), "escalation_frequency": 0.30}
        result = ctrl.evaluate(50.0, m, "co_esc3")
        assert any("ENVELOPE_WIDENED" in t for t in result["triggers"])


# ─────────────────────────────────────────────────────────────────────────────
# 6. CONFIDENCE DECAY
# ─────────────────────────────────────────────────────────────────────────────

class TestConfidenceDecay:
    def test_low_confidence_drops_one_band(self):
        ctrl = _ctrl()
        m = {**_nominal(), "confidence_avg": 0.55, "confidence_trend": "decaying"}
        result = ctrl.evaluate(50.0, m, "co_conf1")
        assert result["current_band"] == Band.CONSERVATIVE.value

    def test_confidence_decay_expands_sandbox(self):
        ctrl = _ctrl()
        m = {**_nominal(), "confidence_avg": 0.60, "confidence_trend": "decaying"}
        result = ctrl.evaluate(50.0, m, "co_conf2")
        assert result["sandbox_allocation_pct"] > 10.0

    def test_trigger_label_present(self):
        ctrl = _ctrl()
        m = {**_nominal(), "confidence_avg": 0.60, "confidence_trend": "decaying"}
        result = ctrl.evaluate(50.0, m, "co_conf3")
        assert any("CONFIDENCE_DECAY" in t for t in result["triggers"])

    def test_stable_confidence_causes_gradual_expansion(self):
        """7+ consecutive stable cycles → autonomy expands beyond initial pct."""
        ctrl = _ctrl()
        stable_m = {
            **_nominal(),
            "confidence_avg":   0.90,
            "confidence_trend": "stable",
        }
        pct = 50.0
        result = None
        for _ in range(10):   # run 10 cycles, feeding forward each result
            result = ctrl.evaluate(pct, stable_m, "co_conf4")
            pct = result["new_pct"]
        # After sustained stability the pct should have grown
        assert pct > 50.0, f"Expected expansion beyond 50%, got {pct}"
        # And at least one expansion trigger should have fired across cycles
        hist = ctrl.get_dashboard("co_conf4")["history"]
        expansion_fired = any(
            any("EXPANSION" in t or "PROMOTION" in t for t in h.get("triggers", []))
            for h in hist
        )
        assert expansion_fired


# ─────────────────────────────────────────────────────────────────────────────
# 7. STABILITY SCORE
# ─────────────────────────────────────────────────────────────────────────────

class TestStabilityScore:
    def test_clean_system_has_high_score(self):
        ctrl = _ctrl()
        m = _nominal()
        result = ctrl.evaluate(50.0, m, "co_score1")
        assert result["stability_score"] >= 90

    def test_stabilization_mode_lowers_score(self):
        ctrl = _ctrl()
        result = ctrl.evaluate(50.0, {**_nominal(), "rollback_rate": 0.10}, "co_score2")
        assert result["stability_score"] < 100

    def test_band_matters_for_score(self):
        ctrl = _ctrl()
        # Get into MAX band
        state = ctrl._get_or_create_state("co_score3", 90.0)
        state.current_band = Band.MAX
        score = state._stability_score()
        assert score < 100


# ─────────────────────────────────────────────────────────────────────────────
# 8. DASHBOARD OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

class TestDashboardOutput:
    def test_dashboard_has_all_required_keys(self):
        ctrl = _ctrl()
        ctrl.evaluate(50.0, _nominal(), "co_dash1")
        dash = ctrl.get_dashboard("co_dash1")
        required = [
            "current_pct", "current_band", "stabilization_mode",
            "stable_cycles", "last_adjustment_reason",
            "stability_score", "budget_change_limit_pct",
            "sandbox_allocation_pct", "history"
        ]
        for key in required:
            assert key in dash, f"Missing dashboard key: {key}"

    def test_history_grows_with_evaluations(self):
        ctrl = _ctrl()
        for _ in range(5):
            ctrl.evaluate(50.0, _nominal(), "co_dash2")
        dash = ctrl.get_dashboard("co_dash2")
        assert len(dash["history"]) == 5

    def test_unknown_company_returns_error(self):
        ctrl = _ctrl()
        dash = ctrl.get_dashboard("nonexistent_company")
        assert "error" in dash
