import pytest
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────
# 1. ESCALATION STATE MACHINE TESTS
# ──────────────────────────────────────────────────

def test_escalation_conflict_finance_approved_cmo_rejected():
    """Finance has higher priority than CMO → APPROVED."""
    from backend.marketing_os_app.governance.escalation_state_machine import EscalationStateMachine
    sm = EscalationStateMachine()
    esc = {
        "escalation_id": "esc_001",
        "created_at": datetime.utcnow(),
        "current_risk_score": 0.5,
        "envelope_modified_mid_escalation": False,
        "emergency_override": False,
        "approvals": [
            {"role": "finance", "decision": "approved", "timestamp": datetime.utcnow().isoformat()},
            {"role": "cmo",     "decision": "rejected", "timestamp": datetime.utcnow().isoformat()}
        ]
    }
    result = sm.evaluate(esc)
    assert result["resolved_state"] == "approved"

def test_escalation_cmo_approved_media_buyer_rejected():
    """CMO outranks media_buyer → APPROVED."""
    from backend.marketing_os_app.governance.escalation_state_machine import EscalationStateMachine
    sm = EscalationStateMachine()
    esc = {
        "escalation_id": "esc_002",
        "created_at": datetime.utcnow(),
        "current_risk_score": 0.4,
        "envelope_modified_mid_escalation": False,
        "emergency_override": False,
        "approvals": [
            {"role": "cmo",         "decision": "approved", "timestamp": datetime.utcnow().isoformat()},
            {"role": "media_buyer", "decision": "rejected", "timestamp": datetime.utcnow().isoformat()}
        ]
    }
    result = sm.evaluate(esc)
    assert result["resolved_state"] == "approved"

def test_escalation_timeout_no_response():
    """SLA exceeded with 0 approvals → EXPIRED."""
    from backend.marketing_os_app.governance.escalation_state_machine import EscalationStateMachine
    sm = EscalationStateMachine()
    esc = {
        "escalation_id": "esc_003",
        "created_at": datetime.utcnow() - timedelta(hours=5),  # Past SLA
        "current_risk_score": 0.3,
        "envelope_modified_mid_escalation": False,
        "emergency_override": False,
        "approvals": []
    }
    result = sm.evaluate(esc)
    assert result["resolved_state"] == "expired"

def test_escalation_emergency_override():
    """Emergency override always wins regardless."""
    from backend.marketing_os_app.governance.escalation_state_machine import EscalationStateMachine
    sm = EscalationStateMachine()
    esc = {
        "escalation_id": "esc_004",
        "created_at": datetime.utcnow(),
        "current_risk_score": 0.9,
        "envelope_modified_mid_escalation": False,
        "emergency_override": True,
        "approvals": [{"role": "cmo", "decision": "rejected", "timestamp": datetime.utcnow().isoformat()}]
    }
    result = sm.evaluate(esc)
    assert result["resolved_state"] == "overridden"

def test_escalation_envelope_modified_resets_to_pending():
    from backend.marketing_os_app.governance.escalation_state_machine import EscalationStateMachine
    sm = EscalationStateMachine()
    esc = {
        "escalation_id": "esc_005",
        "created_at": datetime.utcnow(),
        "current_risk_score": 0.4,
        "envelope_modified_mid_escalation": True,
        "emergency_override": False,
        "approvals": [{"role": "owner", "decision": "approved", "timestamp": datetime.utcnow().isoformat()}]
    }
    result = sm.evaluate(esc)
    assert result["resolved_state"] == "pending"

# ──────────────────────────────────────────────────
# 2. ADAPTIVE AUTONOMY THROTTLING TESTS
# ──────────────────────────────────────────────────

def test_autonomy_drift_spike_reduces_pct():
    from backend.marketing_os_app.governance.autonomy_controller import AutonomyController
    ctrl = AutonomyController(db=None)
    result = ctrl.evaluate(current_pct=20.0, metrics={
        "drift_frequency": 0.5,  # > 0.3 threshold
        "volatility_index": 0.2,
        "rollback_rate": 0.03,
        "confidence_avg": 0.8,
        "stable_days": 5,
        "escalation_frequency": 0.05
    })
    assert result["new_pct"] < 20.0
    assert "DRIFT_SPIKE" in result["triggers"]

def test_autonomy_stable_confidence_increases_pct():
    from backend.marketing_os_app.governance.autonomy_controller import AutonomyController
    ctrl = AutonomyController(db=None)
    result = ctrl.evaluate(current_pct=30.0, metrics={
        "drift_frequency": 0.05,
        "volatility_index": 0.1,
        "rollback_rate": 0.01,
        "confidence_avg": 0.90,  # > 0.85 threshold
        "stable_days": 15,       # > 14 threshold
        "escalation_frequency": 0.02
    })
    assert result["new_pct"] > 30.0
    assert "CONFIDENCE_STABLE" in " ".join(result["triggers"])

def test_autonomy_rollback_triggers_conservative_mode():
    from backend.marketing_os_app.governance.autonomy_controller import AutonomyController
    ctrl = AutonomyController(db=None)
    result = ctrl.evaluate(current_pct=25.0, metrics={
        "drift_frequency": 0.1,
        "volatility_index": 0.2,
        "rollback_rate": 0.15,  # > 0.08 threshold
        "confidence_avg": 0.7,
        "stable_days": 3,
        "escalation_frequency": 0.05
    })
    assert result["mode"] == "conservative"
    assert result["new_pct"] <= 5.0

# ──────────────────────────────────────────────────
# 3. STRATEGY ARCHETYPE & BIAS TESTS
# ──────────────────────────────────────────────────

def test_archetype_bias_applied_when_match_found():
    from backend.marketing_os_app.intelligence.strategy_archetype_engine import StrategyArchetypeEngine
    engine = StrategyArchetypeEngine()
    archetypes = [{
        "pattern_id": "arch_001",
        "industry": "ecommerce",
        "strategy_type": "SCALE",
        "avg_lift_pct": 22.0,
        "confidence_score": 0.85,
        "sample_count": 10
    }]
    result = engine.compute_bias(
        context={"industry": "ecommerce", "strategy_type": "SCALE"},
        archetypes=archetypes
    )
    assert result["bias_modifier"] > 0
    assert result["source"] == "archetype_match"

def test_archetype_no_bias_when_no_match():
    from backend.marketing_os_app.intelligence.strategy_archetype_engine import StrategyArchetypeEngine
    engine = StrategyArchetypeEngine()
    result = engine.compute_bias(
        context={"industry": "saas", "strategy_type": "PAUSE"},
        archetypes=[]
    )
    assert result["bias_modifier"] == 0.0
    assert result["source"] == "no_match"

# ──────────────────────────────────────────────────
# 4. CROSS-TENANT AGGREGATION TEST
# ──────────────────────────────────────────────────

def test_cross_tenant_risk_stacking():
    from backend.marketing_os_app.agency.cross_tenant_analytics import ExposureStackAnalyzer
    analyzer = ExposureStackAnalyzer()
    snapshots = [
        {"total_capital_at_risk": 5000.0},
        {"total_capital_at_risk": 12000.0},
        {"total_capital_at_risk": 3000.0}
    ]
    result = analyzer.analyze(snapshots)
    assert result["total_exposure_usd"] == 20000.0
    assert result["single_tenant_worst_case"] == 12000.0
    # 12000/20000 = 0.6 > 0.4 → over-concentrated
    assert result["over_concentrated"] is True

def test_cross_tenant_dashboard_anonymized():
    from backend.marketing_os_app.agency.cross_tenant_analytics import CrossTenantDashboard
    dashboard = CrossTenantDashboard()
    snapshots = [
        {"total_capital_at_risk": 5000, "autonomy_exposure_pct": 8.0, "drift_frequency": 0.1,
         "roi_delta_pct": 14.0, "escalations_triggered": 2, "volatility_index": 0.2},
        {"total_capital_at_risk": 8000, "autonomy_exposure_pct": 12.0, "drift_frequency": 0.3,
         "roi_delta_pct": 6.0, "escalations_triggered": 5, "volatility_index": 0.7}
    ]
    result = dashboard.aggregate(snapshots)
    assert result["tenant_count"] == 2
    assert "company_id" not in str(result)   # No tenant PII
    assert result["total_capital_at_risk_usd"] == 13000.0

# ──────────────────────────────────────────────────
# 5. DECISION SPEED INDEX TESTS
# ──────────────────────────────────────────────────

def test_dsi_perfect_score_within_all_sla():
    from backend.marketing_os_app.performance.decision_speed_tracker import DecisionSpeedTracker
    tracker = DecisionSpeedTracker(db=None)
    stages = {
        "diagnose_to_strategy_ms":    1000.0,      # Well within 5s
        "strategy_to_execute_ms":     5000.0,      # Within 10s
        "execute_to_drift_eval_ms":   1_800_000.0, # Within 1h
        "escalation_to_approval_ms":  7_200_000.0, # Within 4h
        "task_create_to_complete_ms": 43_200_000.0 # Within 24h
    }
    dsi = tracker._compute_dsi(stages)
    assert dsi == 100.0

def test_dsi_degraded_by_slow_approval():
    from backend.marketing_os_app.performance.decision_speed_tracker import DecisionSpeedTracker
    tracker = DecisionSpeedTracker(db=None)
    stages = {
        "diagnose_to_strategy_ms":    1000.0,
        "strategy_to_execute_ms":     5000.0,
        "execute_to_drift_eval_ms":   1_800_000.0,
        "escalation_to_approval_ms":  72_000_000.0,  # 20h — 5× SLA
        "task_create_to_complete_ms": 43_200_000.0
    }
    dsi = tracker._compute_dsi(stages)
    assert dsi < 100.0

def test_lift_pattern_detector():
    from backend.marketing_os_app.intelligence.strategy_archetype_engine import LiftPatternDetector
    detector = LiftPatternDetector()
    archetypes = [
        {"pattern_id": "a1", "avg_lift_pct": 20.0, "confidence_score": 0.9, "sample_count": 5, "avg_risk_exposure": 0.3},
        {"pattern_id": "a2", "avg_lift_pct": -5.0, "confidence_score": 0.7, "sample_count": 3, "avg_risk_exposure": 0.4},
        {"pattern_id": "a3", "avg_lift_pct": 30.0, "confidence_score": 0.8, "sample_count": 4, "avg_risk_exposure": 0.8}
    ]
    result = detector.detect(archetypes)
    assert len(result["repeating_lift_patterns"]) == 2   # a1 + a3 > 15% with ≥3 samples
    assert len(result["strategy_failure_clusters"]) == 1  # a2 < 0
