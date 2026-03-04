"""
Test Suite for Strategy Simulation Engine
=========================================
Verifies generation of variants, risk estimators, 
and correct scenario ranking algorithms.
"""

import pytest
import uuid

from backend.services.intelligence.strategy_simulation.models import Scenario, EnvironmentState, RiskProfile, OutcomePrediction
from backend.services.intelligence.strategy_simulation.scenario_builder import ScenarioBuilder
from backend.services.intelligence.strategy_simulation.environment_model import EnvironmentModel
from backend.services.intelligence.strategy_simulation.campaign_predictor import CampaignPredictor
from backend.services.intelligence.strategy_simulation.risk_estimator import RiskEstimator
from backend.services.intelligence.strategy_simulation.outcome_analyzer import OutcomeAnalyzer
from backend.services.intelligence.strategy_simulation.scenario_ranker import ScenarioRanker
from backend.services.intelligence.strategy_simulation.simulator import StrategySimulationEngine

def test_scenario_builder():
    sb = ScenarioBuilder()
    action = {"type": "SCALE_BUDGET", "payload": {"target_entity": "camp1"}}
    scenarios = sb.build_scenarios("strat123", action)
    
    assert len(scenarios) == 3
    assert scenarios[0].action_type == "SCALE_BUDGET"
    assert "increase_pct" in scenarios[0].parameter_variations
    
def test_environment_model():
    em = EnvironmentModel()
    ctx = { # Base context output mock
        "current_performance": {"avg_cpa": 30.0},
        "market_signals": {"cpm_trend": 0.10},
        "critical_flags": {"creative_fatigue": True},
        "competitor_intelligence": {"market_pressure": {"saturation_score": 0.9}}
    }
    
    env = em.load_environment("comp1", ctx)
    assert env.audience_saturation == 0.85 # mapped fatigue logic
    assert env.competitor_pressure == 0.90
    assert env.average_cpm == 11.0 # 10.0 base + 10%
    
def test_predictor_and_risk():
    env = EnvironmentState(average_cpm=10, average_ctr=0.015, conversion_rate=0.03, audience_saturation=0.90, competitor_pressure=0.50)
    scen1 = Scenario(id="s1", strategy_reference="a", action_type="SCALE_BUDGET", parameter_variations={"increase_pct": 30})
    
    pred = CampaignPredictor()
    predictions = pred.predict([scen1], env)
    
    assert "s1" in predictions
    assert predictions["s1"]["cpa_change"] > 0 # High saturation scaling punishes CPA
    
    risk_est = RiskEstimator()
    risk = risk_est.estimate_risks([scen1], predictions, env)
    
    assert risk["s1"].volatility_score > 0.40 # Triggered high aggresive scaling boundary

def test_ranker():
    scen1 = Scenario(id="s1", strategy_reference="a", action_type="DUMMY", parameter_variations={})
    scen2 = Scenario(id="s2", strategy_reference="a", action_type="DUMMY", parameter_variations={})
    
    preds = {"s1": {"cpa_change": 0.0, "ctr_change": 0.1, "revenue_change": 0.1}, "s2": {"cpa_change": -0.1, "ctr_change": 0.2, "revenue_change": 0.3}}
    outcomes = [
        OutcomePrediction(scenario_id="s1", expected_growth=0.1, expected_cpa_change=0, expected_roi=0.1, confidence_score=0.9, risk_profile=RiskProfile(risk_score=0.1, volatility_score=0, uncertainty_score=0, risk_factors=[])),
        OutcomePrediction(scenario_id="s2", expected_growth=0.3, expected_cpa_change=-0.1, expected_roi=0.4, confidence_score=0.8, risk_profile=RiskProfile(risk_score=0.5, volatility_score=0.6, uncertainty_score=0.4, risk_factors=[]))
    ]
    
    ranker = ScenarioRanker()
    # Scenario 1 = (0.1 * 0.45) + (0.9 * 0.35) - (0.1 * 0.20) = 0.045 + 0.315 - 0.02 = 0.34
    # Scenario 2 = (0.3 * 0.45) + (0.8 * 0.35) - (0.5 * 0.20) = 0.135 + 0.280 - 0.10 = 0.315
    # Therefore, Scenario 1 should win because excessive risk (0.5) degrades too much score.
    res = ranker.rank_scenarios([scen1, scen2], outcomes, preds)
    assert res.best_scenario.id == "s1"
    
def test_engine_orchestration():
    eng = StrategySimulationEngine()
    
    action = {"type": "PAUSE_CAMPAIGN", "payload": {"target_entity": "camp2"}}
    ctx = {
        "current_performance": {"avg_cpa": 30.0},
        "market_signals": {"cpm_trend": 0.10},
        "critical_flags": {"creative_fatigue": True},
        "competitor_intelligence": {"market_pressure": {"saturation_score": 0.9}}
    }
    
    res = eng.simulate_strategy("comp1", "strat1", action, ctx)
    assert res.confidence > 0
    assert "cpa_change" in res.predicted_metrics
    assert res.all_scenarios_evaluated > 0
