import pytest
import asyncio
from unittest.mock import AsyncMock

from backend.services.sentinel.health_monitor import HealthMonitor
from backend.services.sentinel.drift_detector import DriftDetector
from backend.services.sentinel.anomaly_aggregator import AnomalyAggregator
from backend.services.sentinel.risk_dashboard_engine import RiskDashboardEngine
from backend.services.sentinel.execution_auditor import ExecutionAuditor

def test_health_monitor():
    hm = HealthMonitor()
    
    # Simulate errors
    executions = [
        {"status": "success"},
        {"status": "failed"},
        {"status": "failed"},
        {"status": "rollback_triggered"}
    ] # 4 total, 2 fails = 50% rate
    
    res = hm.calculate_engine_health({"avg_latency_ms": 100}, executions)
    assert res["failure_rate"] == 0.5
    assert res["rollback_frequency"] == 0.25
    assert res["status"] == "degraded"
    
def test_drift_detector():
    drift = DriftDetector()
    
    # 1. Variance logic
    res_high = drift.evaluate_model_drift(0.5, 0.1, ["SCALING", "SCALING", "SCALING"])
    assert res_high["drift_active"] == True
    assert res_high["variance_delta"] == 0.4 # Diff 0.4 > 0.3 limit 
    
    # 2. Oscillation logic 
    res_osc = drift.evaluate_model_drift(0.1, 0.15, ["SCALING", "FATIGUE", "CONVERSION"])
    assert res_osc["drift_active"] == True # Variance fine, but classes scattered!

@pytest.mark.asyncio
async def test_execution_auditor():
    mock_db = AsyncMock()
    auditor = ExecutionAuditor(mock_db)
    
    res = await auditor.audit_execution_loop(
        payload={"company_id": "test", "campaign_id": "1", "expected_delta": 0.2, "action_type": "SCALE"},
        outcome={"real_delta": 0.22}
    )
    
    assert res.company_id == "test"
    assert res.expected_delta == 0.2
    assert res.actual_delta == 0.22
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_risk_dashboard():
    dashboard = RiskDashboardEngine()
    
    # Simulate high drift frequency (2 out of 3 hits) + minimal failure rates
    res = dashboard.generate_dashboard_metrics(
         uptime_metrics={"avg_latency_ms": 40},
         execution_history=[{"status": "success"}]*10, # 0 fails
         drift_variances=[0.5, 0.8, 0.1]
    )
    
    assert res.autonomy_stability_index == 1.0 # 0% failure
    assert res.drift_frequency > 0.60 # (2 / 3) 
    assert res.execution_precision_score == 1.0 # 0 rollbacks
    
    # Risk exposure scales aggressively with drift frequency
    assert res.system_risk_exposure_score > 0.3 
