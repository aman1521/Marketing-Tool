"""
Unified Intelligence Test Suite
===============================
Runs the full orchestration pipeline:
Context -> Council -> Strategy -> Simulation -> Execution
"""

import pytest

from backend.services.intelligence.orchestrator.main_loop import UnifiedIntelligenceOrchestrator
from backend.services.intelligence.strategy_council.models import AgentRole

@pytest.fixture
def orchestrator():
    # Setup the whole stack
    orchestrator = UnifiedIntelligenceOrchestrator()
    return orchestrator

@pytest.mark.asyncio
async def test_unified_intelligence_loop_end_to_end(orchestrator, monkeypatch):
    """
    Simulates a CRON trigger running the system across all 5 built Intelligence Engine Architectures.
    """
    # 1. Mock context building deep within CaptainStrategy
    def mock_build_snapshot(cid, ind, reqs):
         return {
            "company_id": "test_corp",
            "momentum": "positive",
            "market_signals": {
                 "volatility_index": 0.20, # Low Risk
                 "cpm_trend": -0.15,
                 "platform_momentum": "tiktok"
            },
            "critical_flags": {
                 "high_market_pressure": False,
                 "creative_fatigue":     False
            },
            "directional_signals": {
                 "operator_action": "EXECUTE",
                 "recommended_creative_pivots": ["arch_19"],
                 "unexploited_gaps": ["Authority Hook in B2B SaaS"]
            },
            "competitor_intelligence": {
                 "market_pressure": {"cluster": "fear_discount"},
                 "strategy_gaps": [
                      {"summary": "Use more Authority", "dimension": "landing_page"}
                 ]
            },
            "confidence_score": 0.85
         }
         
    # Mock reality extraction so the environment loads without real DB tables. 
    def mock_fuse_context(context):
         return context
         
    # Monkeypatch the builders inside the orchestrator instances
    monkeypatch.setattr(orchestrator.captain.builder, "build_snapshot", mock_build_snapshot)
    monkeypatch.setattr(orchestrator.captain.fusion, "fuse_context", mock_fuse_context)
    
    # Also patch the simulator's environment extraction to use the mock
    def mock_env(comp, ctx):
         from backend.services.intelligence.strategy_simulation.models import EnvironmentState
         return EnvironmentState(
              average_cpm=10,
              average_ctr=0.015,
              conversion_rate=0.04,
              audience_saturation=0.50, # very scalable
              competitor_pressure=0.20
         )
    monkeypatch.setattr(orchestrator.simulator.env, "load_environment", mock_env)
    
    # 2. Execute Pipeline 
    camp_mock = [{"id": "camp1", "spend": 1000}]
    output = await orchestrator.execute_intelligence_loop("test_corp", "ecommerce", camp_mock)
    
    # 3. Assert End-to-End Mechanics
    assert output["status"] == "success"
    
    # Council should have spit out multiple actions based on Context above
    # (Growth -> Scale Budget, Creative -> Pivot, Market -> Audience Expand, etc)
    assert output["actions_simulated"] >= 3
    
    # Ensure Simulation let safe actions through to Execution routers
    # Since saturation is 0.5 and volatility 0.2, nothing should be blocked by Safety Risk bounds.
    assert output["actions_executed"] == output["actions_simulated"]
    
    assert "forge_actions" in output["execution_mapping"]
    assert "hawkeye_actions" in output["execution_mapping"]
