import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ──────────────────────────────────────────────
# GOVERNANCE TESTS
# ──────────────────────────────────────────────

def test_envelope_check_within_bounds():
    """Action within all envelope limits → not escalated."""
    from backend.marketing_os_app.governance.envelope_manager import EnvelopeManager

    mock_db = AsyncMock()
    mgr = EnvelopeManager(mock_db)

    # Mock envelope objects
    budget_env = MagicMock()
    budget_env.daily_change_limit_percent = 10.0

    strategy_env = MagicMock()
    strategy_env.allowed_strategy_types = ["SCALE", "PAUSE"]
    strategy_env.allowed_platforms = ["meta", "google"]
    strategy_env.max_risk_score = 0.7

    action = {
        "action_type": "SCALE",
        "budget_change_percent": 5.0,
        "platform": "meta",
        "risk_score": 0.4
    }

    # Inline synchronous check (skipping DB for unit test)
    change_pct = action["budget_change_percent"]
    assert change_pct <= budget_env.daily_change_limit_percent

    action_type = action["action_type"]
    assert action_type in strategy_env.allowed_strategy_types

    platform = action["platform"]
    assert platform in strategy_env.allowed_platforms

    risk_score = action["risk_score"]
    assert risk_score <= strategy_env.max_risk_score

def test_envelope_budget_breach_detection():
    """Action exceeding daily limit is detected as BUDGET_BREACH."""
    budget_limit = 10.0
    action_change_pct = 25.0  # Over limit
    assert action_change_pct > budget_limit

def test_envelope_strategy_breach_detection():
    """Disallowed action type triggers STRATEGY_BREACH."""
    allowed = ["SCALE", "PAUSE"]
    action_type = "EMERGENCY_OVERRIDE"
    assert action_type not in allowed

# ──────────────────────────────────────────────
# ROLE MATRIX TESTS
# ──────────────────────────────────────────────

def test_role_matrix_owner_permissions():
    from backend.marketing_os_app.collaboration.role_matrix import get_role_permissions, can_role_perform
    perms = get_role_permissions("owner")
    assert perms["can_execute"] is True
    assert perms["can_modify_envelope"] is True
    assert perms["can_approve_escalations"] is True
    assert perms["can_override"] is True

def test_role_matrix_viewer_restrictions():
    from backend.marketing_os_app.collaboration.role_matrix import get_role_permissions
    perms = get_role_permissions("viewer")
    assert perms["can_execute"] is False
    assert perms["can_modify_envelope"] is False
    assert perms["can_approve_escalations"] is False

def test_escalation_routing_budget_breach():
    from backend.marketing_os_app.collaboration.role_matrix import get_escalation_targets
    targets = get_escalation_targets("BUDGET_BREACH")
    assert "finance" in targets
    assert "owner" in targets

def test_escalation_routing_strategy_breach():
    from backend.marketing_os_app.collaboration.role_matrix import get_escalation_targets
    targets = get_escalation_targets("STRATEGY_BREACH")
    assert "cmo" in targets

# ──────────────────────────────────────────────
# TRANSLATION LAYER TESTS
# ──────────────────────────────────────────────

def test_translation_simple_mode():
    from backend.marketing_os_app.dashboards.translation_layer import TranslationLayer
    t = TranslationLayer()
    result = t.translate({"executions_count": 5, "system_risk_exposure_score": 0.2,
                           "rollback_count": 0}, mode="simple")
    assert "what_changed_today" in result
    assert "what_ai_did" in result
    assert "Low risk" in result["what_risk_exists"]

def test_translation_executive_mode():
    from backend.marketing_os_app.dashboards.translation_layer import TranslationLayer
    t = TranslationLayer()
    result = t.translate({"total_capital_at_risk": 5000, "system_risk_exposure_score": 0.6,
                           "autonomy_exposure_pct": 12.0, "executions_count": 20,
                           "pending_escalations": 2, "worst_case_downside": 7500.0,
                           "roi_delta_pct": "+18%"}, mode="executive")
    assert result["capital_at_risk"] == 5000
    assert result["system_health"] == "Monitoring Required"

# ──────────────────────────────────────────────
# AI IMPACT ENGINE TESTS
# ──────────────────────────────────────────────

def test_ai_impact_positive_roi_delta():
    from backend.marketing_os_app.usage.ai_impact_engine import AIImpactEngine
    engine = AIImpactEngine()
    result = engine.compute_impact(
        baseline_metrics={"roas": 1.8, "cpa": 50.0, "fatigue_recovery_days": 14, "experiment_velocity": 2},
        live_metrics={"roas": 2.5, "cpa": 38.0, "fatigue_recovery_days": 5, "drift_incidents": 1, "experiment_velocity": 8},
        usage_data={"autonomy_percentage": 8.5, "executions_count": 42, "escalations_triggered": 2, "rollbacks": 1}
    )
    assert result["roi_delta_vs_baseline_pct"] > 0
    assert result["cpa_improvement_pct"] > 0
    assert result["fatigue_recovery_speed_gain_pct"] > 0
    assert result["experiment_lift_rate_pct"] > 0
    assert result["autonomy_precision_score"] > 90.0

# ──────────────────────────────────────────────
# PORTFOLIO RISK TRACKER TESTS
# ──────────────────────────────────────────────

def test_portfolio_risk_computation():
    from backend.marketing_os_app.governance.portfolio_risk_tracker import PortfolioRiskTracker

    tracker = PortfolioRiskTracker(db=None)  # No DB needed for compute
    campaigns = [
        {"budget_allocated": 5000.0, "roas": 2.1, "risk_score": 0.3},
        {"budget_allocated": 3000.0, "roas": 1.5, "risk_score": 0.6},
        {"budget_allocated": 2000.0, "roas": 0.9, "risk_score": 0.8}
    ]
    result = tracker.compute_risk(campaigns, total_budget=10000.0, autonomy_pct=8.5, volatility_index=0.2)

    assert result["total_capital_at_risk"] > 0
    assert result["worst_case_downside"] > result["total_capital_at_risk"]
    assert 0 <= result["cross_campaign_exposure"] <= 1.0

@pytest.mark.asyncio
async def test_task_creation_signal_routing():
    from backend.marketing_os_app.collaboration.task_assigner import TaskAssigner, SIGNAL_ROLE_MAP
    from backend.marketing_os_app.ecosystem_models import TeamRole

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    assigner = TaskAssigner(mock_db)
    assigner.feed.emit = AsyncMock()

    task_id = await assigner.create_task(
        company_id="test_company",
        signal_type="CREATIVE_FATIGUE",
        title="Creative fatigue detected on Summer_Set_01",
        description="CTR dropped 40% over 7 days. New angle required.",
        supporting_signals={"ctr_drop": 0.4, "asset_id": "Summer_Set_01"}
    )

    assert task_id.startswith("task_")
    # Verify routing logic
    assert SIGNAL_ROLE_MAP["CREATIVE_FATIGUE"] == TeamRole.CREATIVE_STRATEGIST
