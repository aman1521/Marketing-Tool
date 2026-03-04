"""
Test Suite for the Multi-Agent Strategy Council
===============================================
Ensures that all agents (Growth, Creative, Market, Competitor, Risk) 
analyze the fused matrix context and correctly execute or override each other via the DebateEngine.
"""

import pytest
from backend.services.intelligence.strategy_council.models import AgentRole
from backend.services.intelligence.strategy_council.growth_agent import GrowthAgent
from backend.services.intelligence.strategy_council.creative_agent import CreativeAgent
from backend.services.intelligence.strategy_council.market_agent import MarketAgent
from backend.services.intelligence.strategy_council.competitor_agent import CompetitorAgent
from backend.services.intelligence.strategy_council.risk_agent import RiskAgent
from backend.services.intelligence.strategy_council.debate_engine import DebateEngine
from backend.services.intelligence.strategy_council.synthesis_engine import SynthesisEngine
from backend.services.intelligence.strategy_council.council_orchestrator import StrategyCouncil

# --- 1. Base Context Definition ---
@pytest.fixture
def mock_context():
    return {
        "momentum":         "positive",
        "market_signals": {
             "volatility_index": 0.40,
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

# --- 2. Tests ---

def test_growth_agent(mock_context):
    ga = GrowthAgent().analyze(mock_context)
    assert ga.agent_role == AgentRole.GROWTH
    actions = [a.action_type for a in ga.proposed_actions]
    assert "SCALE_BUDGET" in actions
    assert "PLATFORM_SHIFT" in actions


def test_creative_agent(mock_context):
    # Base Context
    ca = CreativeAgent().analyze(mock_context)
    assert "NEW_CREATIVE_ANGLE" in [a.action_type for a in ca.proposed_actions]

    # Fatigue Context
    mock_context["critical_flags"]["creative_fatigue"] = True
    ca2 = CreativeAgent().analyze(mock_context)
    assert "REDUCE_BUDGET" in [a.action_type for a in ca2.proposed_actions]


def test_market_agent(mock_context):
    # Base: Good CPM trend (-15%)
    ma = MarketAgent().analyze(mock_context)
    assert "AUDIENCE_EXPANSION" in [a.action_type for a in ma.proposed_actions]
    
    # Volatility Risk
    mock_context["market_signals"]["volatility_index"] = 0.80
    ma2 = MarketAgent().analyze(mock_context)
    assert "PAUSE_CAMPAIGN" in [a.action_type for a in ma2.proposed_actions]


def test_risk_overrides_growth(mock_context):
    # Provide a context where Growth wants to Scale but Risk wants to Block
    mock_context["momentum"] = "positive" # Growth scales
    mock_context["directional_signals"]["operator_action"] = "AVOID" # Risk panics
    
    ga = GrowthAgent().analyze(mock_context)
    ra = RiskAgent().analyze(mock_context)
    assert "SCALE_BUDGET" in [a.action_type for a in ga.proposed_actions]
    assert "REDUCE_BUDGET" in [a.action_type for a in ra.proposed_actions]
    
    # Debate Engine
    de = DebateEngine()
    debates = de.run_debate([ga, ra])
    assert len(debates) == 1
    assert debates[0].interaction_type == "challenge"
    assert debates[0].source_agent == AgentRole.RISK


def test_market_restricts_creative(mock_context):
    mock_context["critical_flags"]["creative_fatigue"] = True 
    mock_context["directional_signals"]["recommended_creative_pivots"] = ["arch_99"]  # Creative pivots
    mock_context["market_signals"]["volatility_index"] = 0.80 # Market pauses
    
    ca = CreativeAgent().analyze(mock_context)
    ma = MarketAgent().analyze(mock_context)
    
    de = DebateEngine()
    debates = de.run_debate([ca, ma])
    assert len(debates) == 1
    assert debates[0].interaction_type == "refine"
    assert debates[0].proposed_adjustment["parameters"]["budget_allocation"] == "5%"


def test_council_orchestrator(mock_context):
    """E2E Workflow Test."""
    council = StrategyCouncil()
    final_output = council.run_council(mock_context)
    
    assert final_output.overall_confidence > 0
    assert len(final_output.final_actions) > 0 # Scale + Platform + Creative Pivot + Gap
    
    a_types = [a.action_type for a in final_output.final_actions]
    assert "SCALE_BUDGET" in a_types
    assert "NEW_CREATIVE_ANGLE" in a_types
    assert "OFFER_CHANGE" in a_types
