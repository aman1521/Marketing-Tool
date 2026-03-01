import pytest
import asyncio
from unittest.mock import AsyncMock

from backend.services.pulse.seasonality_engine import SeasonalityEngine
from backend.services.pulse.volatility_engine import VolatilityEngine
from backend.services.pulse.demand_engine import DemandEngine
from backend.services.pulse.macro_drift_engine import MacroDriftEngine
from backend.services.pulse.pulse_engine import PulseEngine

# --- Logic Tests ---

def test_seasonality_engine_determinism():
    engine = SeasonalityEngine()
    
    # Peak logic test
    history_surge = [50.0]*10 + [100.0]*4 + [250.0, 300.0, 280.0]
    res_surge = engine.calculate_seasonality(history_surge, 0)
    assert res_surge["seasonality_index"] > 0.75
    assert res_surge["seasonal_phase"] == "peak"

    # Default logic test
    res_default = engine.calculate_seasonality([], 0)
    assert res_default["seasonality_index"] == 0.5

def test_volatility_engine_turbulence():
    engine = VolatilityEngine()
    
    # Stable arrays - variance should be negligible
    res_stable = engine.calculate_volatility(cpm_history=[10, 10.5, 9.8, 10.1], cpa_history=[50, 52, 49, 51])
    assert res_stable["volatility_index"] < 0.2
    assert res_stable["turbulence_flag"] == False

    # Extreme chaos array (High CoV)
    res_chaos = engine.calculate_volatility(cpm_history=[10, 50, 5, 100, 2], cpa_history=[10, 500, 20, 1000])
    assert res_chaos["volatility_index"] > 0.8
    assert res_chaos["turbulence_flag"] == True

def test_demand_engine_shifts():
    engine = DemandEngine()
    
    # Stable logic
    res_stable = engine.calculate_demand_shift(100.0, 105.0)
    assert res_stable["demand_direction"] == "stable"

    # Collapse mapping
    res_collapse = engine.calculate_demand_shift(1000.0, 300.0) 
    assert res_collapse["demand_shift_score"] < -0.2
    assert res_collapse["demand_direction"] == "down"

def test_macro_drift_engine():
    engine = MacroDriftEngine()
    
    # Platform breakdown (negative roas delta, positive cpc surge)
    res_bad = engine.evaluate_platform_drift({"meta_roas_delta": -0.30, "google_cpc_delta": +0.40})
    assert res_bad["drift_direction"] == "down"
    assert res_bad["macro_drift_score"] < -0.15

# --- Orchestrator & Integration Validation Tests ---

@pytest.mark.asyncio
async def test_pulse_engine_modifier_behavior():
    mock_db = AsyncMock()
    pulse = PulseEngine(mock_db)
    
    # Muting physical DB calls securely
    pulse.registry.log_pulse_iteration = AsyncMock()
    
    # Simulation 1: HORRIFIC MARKET (High volatility, drift collapses, demand falls)
    bad_res = await pulse.execute_macro_scan(
         company_id="test_bad",
         revenue_history=[500]*7, 
         cpm_history=[5, 9, 21, 35, 7, 50],
         cpa_history=[10, 50, 80, 10, 5],
         baseline_conversions=100.0,
         current_conversions=20.0,
         platform_drift_factors={"facebook_cpc_delta": +0.90}
    )
    
    assert bad_res["market_phase"] in ["volatile_decline", "macro_collapse"]
    # Modifiers shouldn't kill logic, but should heavily suppress confidence structurally (e.g. 0.4x to 0.6x)
    assert bad_res["confidence_modifier"] < 0.70
    
    # Simulation 2: STABLE MARKET (Perfect averages)
    good_res = await pulse.execute_macro_scan(
         company_id="test_good",
         revenue_history=[100]*30,
         cpm_history=[10]*5,
         cpa_history=[25]*5,
         baseline_conversions=100,
         current_conversions=100,
         platform_drift_factors={"meta_roas_delta": 0.0}
    )
    
    assert good_res["market_phase"] == "stable_baseline"
    # Stable phase adds to logic confidence
    assert good_res["confidence_modifier"] > 0.99
