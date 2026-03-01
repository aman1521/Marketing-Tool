import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pprint import pprint

from backend.services.forge.significance_engine import SignificanceEngine
from backend.services.forge.allocation_manager import AllocationManager
from backend.services.forge.sandbox_controller import SandboxController
from backend.services.forge.variation_generator import VariationGenerator
from backend.services.forge.experiment_engine import ForgeExperimentEngine

# --- Engine Determinism Tests ---

def test_significance_engine_math():
    engine = SignificanceEngine()
    
    # 1. Clear Winner scenario
    control = {"clicks": 1000, "conversions": 10} # 1%
    variation = {"clicks": 1000, "conversions": 25} # 2.5%
    
    res = engine.evaluate_experiment(control, variation)
    assert res["significant"] == True
    assert res["lift_percentage"] == 150.0  # (2.5 - 1.0) / 1.0 = 150%
    assert res["p_value"] <= 0.05
    assert res["z_score"] > 1.96
    
    # 2. Inconclusive Scenario (No real difference)
    control_2 = {"clicks": 1000, "conversions": 15}
    variation_2 = {"clicks": 1000, "conversions": 16}
    
    res_2 = engine.evaluate_experiment(control_2, variation_2)
    assert res_2["significant"] == False
    assert res_2["p_value"] == 0.5  # Represents generic fail to reject
    
    # 3. Insufficient Data Fail-safe Check
    res_3 = engine.evaluate_experiment({"clicks": 50, "conversions": 2}, {"clicks": 50, "conversions": 5})
    assert res_3["significant"] == False
    assert "reason" in res_3
    
def test_allocation_manager_risks():
    allocator = AllocationManager()
    
    # Aggressive
    assert allocator.allocate_sandbox_budget(1000.0, "Aggressive") == 150.0
    
    # Moderate
    assert allocator.allocate_sandbox_budget(1000.0, "Moderate") == 100.0
    
def test_variation_generator_mapping():
    gen = VariationGenerator()
    
    var_1 = gen.generate_variations("CREATIVE_FATIGUE", {})
    assert var_1["experiment_type"] == "CREATIVE_ANGLE_SHIFT"
    assert "creative_asset" in var_1["variations"]["variation_1"]
    
    var_2 = gen.generate_variations("SCALING_OPPORTUNITY", {})
    assert var_2["experiment_type"] == "AUDIENCE_EXPANSION"
    assert "audience_type" in var_2["variations"]["control"]

def test_sandbox_governance_block():
    sandbox = SandboxController()
    
    # Max Cap Enforced Check
    genesis_env = {"max_daily_budget": 1000.0}
    
    assert sandbox.check_sandbox_safe(150.0, 900.0, genesis_env) == False # Total = 1050 (Fails > 1000)
    assert sandbox.check_sandbox_safe(100.0, 800.0, genesis_env) == True # Total = 900 (Passes < 1000)

@pytest.mark.asyncio
async def test_forge_experiment_launch_orchestration():
    mock_db = AsyncMock()
    forge = ForgeExperimentEngine(mock_db)
    
    # Mock deeply nested dependencies logically
    forge.allocator.allocate_sandbox_budget = MagicMock(return_value=150.0)
    forge.sandbox.check_sandbox_safe = MagicMock(return_value=True)
    forge.registry.register_experiment = AsyncMock(return_value="exp_123_test")
    
    genesis_env = {
        "mappings": {"aggression_tier": "Aggressive"},
        "constraints": {"creative_sandbox_required": True, "max_daily_budget": 2000.0}
    }
    
    res = await forge.launch_experiment("cmp_fatigued", "cmp_abc", "CREATIVE_FATIGUE", 1000.0, genesis_env)
    
    assert res["status"] == "launched"
    assert res["experiment_id"] == "exp_123_test"
    assert res["captain_action_payload"]["action_type"] == "INITIATE_FORGE_SANDBOX"
    
    # Validate DB recording executed dynamically
    forge.registry.register_experiment.assert_called_once()
