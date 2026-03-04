"""
Test Suite for Captain Strategy's Execution Router
==================================================
Validates that generated actions flow correctly to Forge (aggressive) and Hawkeye (defensive).
"""

import pytest
import uuid
from backend.services.intelligence.captain_strategy.models import ActionType, RecommendedAction
from backend.services.intelligence.captain_strategy.execution_router import ExecutionRouter

# Mocks
class MockForgeHandler:
    def __init__(self):
        self.experiments_created = []
        self.scales_applied      = []
        
    def create_experiment(self, payload):
        self.experiments_created.append(payload)
        
    def apply_scale(self, payload):
        self.scales_applied.append(payload)

class MockHawkeyeHandler:
    def __init__(self):
        self.pauses_enforced = []
        self.penalties_applied = []
        
    def enforce_pause(self, payload):
        self.pauses_enforced.append(payload)
        
    def apply_penalty(self, payload):
        self.penalties_applied.append(payload)


@pytest.fixture
def f_handler():
    return MockForgeHandler()

@pytest.fixture
def h_handler():
    return MockHawkeyeHandler()

@pytest.fixture
def router(f_handler, h_handler):
    return ExecutionRouter(forge_client=f_handler, hawkeye_client=h_handler)


def test_route_to_forge(router, f_handler):
    action1 = RecommendedAction(
        id=str(uuid.uuid4()),
        strategy_id="strat_1",
        action_type=ActionType.NEW_CREATIVE_ANGLE,
        payload={"archetypes_to_test": ["abc"], "budget_allocation": "20%"},
        rationale="Opportunity detected."
    )
    
    action2 = RecommendedAction(
        id=str(uuid.uuid4()),
        strategy_id="strat_1",
        action_type=ActionType.SCALE_BUDGET,
        payload={"increase_pct": 30},
        rationale="Strong positive momentum."
    )
    
    res = router.route_strategy("strat_1", [action1, action2])
    
    assert res["forge_actions"] == 2
    assert res["hawkeye_actions"] == 0
    
    assert len(f_handler.experiments_created) == 1
    assert "abc" in f_handler.experiments_created[0]["archetypes"]
    
    assert len(f_handler.scales_applied) == 1
    assert f_handler.scales_applied[0]["scale_pct"] == 30


def test_route_to_hawkeye(router, h_handler):
    action1 = RecommendedAction(
        id=str(uuid.uuid4()),
        strategy_id="strat_1",
        action_type=ActionType.PAUSE_CAMPAIGN,
        payload={"criteria": "worst_performers", "count": 2},
        rationale="Systemic negative baseline."
    )
    
    action2 = RecommendedAction(
        id=str(uuid.uuid4()),
        strategy_id="strat_1",
        action_type=ActionType.REDUCE_BUDGET,
        payload={"decrease_pct": 10},
        rationale="Creative fatigue."
    )
    
    res = router.route_strategy("strat_1", [action1, action2])
    
    assert res["hawkeye_actions"] == 2
    assert res["forge_actions"] == 0
    
    assert len(h_handler.pauses_enforced) == 1
    assert h_handler.pauses_enforced[0]["count"] == 2
    
    assert len(h_handler.penalties_applied) == 1
    assert h_handler.penalties_applied[0]["decrease_pct"] == 10


def test_mixed_routing(router, f_handler, h_handler):
    actions = [
        RecommendedAction(id=str(uuid.uuid4()), strategy_id="s1", action_type=ActionType.SCALE_BUDGET, payload={}),
        RecommendedAction(id=str(uuid.uuid4()), strategy_id="s1", action_type=ActionType.PAUSE_CAMPAIGN, payload={}),
        RecommendedAction(id=str(uuid.uuid4()), strategy_id="s1", action_type=ActionType.OFFER_CHANGE, payload={})
    ]
    
    res = router.route_strategy("s1", actions)
    
    assert res["forge_actions"] == 2 # Scale and Offer mapped to Forge
    assert res["hawkeye_actions"] == 1
    assert len(res["dispatched"]) == 3
