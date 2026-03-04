"""
CaptainStrategy — Full Test Suite
=================================
Validates the Orchestrator, Context Builder, Signal Fusion, 
Opportunities, Threats, and Strategy Generation.
"""

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.intelligence.captain_strategy.models import Base, GeneratedStrategy, RecommendedAction, ActionType
from backend.services.intelligence.captain_strategy.context_builder import ContextBuilder
from backend.services.intelligence.captain_strategy.signal_fusion import SignalFusionEngine
from backend.services.intelligence.captain_strategy.opportunity_detector import OpportunityDetector
from backend.services.intelligence.captain_strategy.threat_detector import ThreatDetector
from backend.services.intelligence.captain_strategy.strategy_generator import StrategyGenerator
from backend.services.intelligence.captain_strategy.outcome_predictor import OutcomePredictor
from backend.services.intelligence.captain_strategy.captain import CaptainStrategy


# --- 1. Mocks & Fixtures ---

class MockMemory:
    def get_influence(self, company_id, decision_context):
        return {
            "confidence": 0.85,
            "predicted_lift": 0.15,
            "action": "EXECUTE",
            "archetypes": ["19", "21"]
        }

class MockPressure:
    def detect_pressure(self, company_id, target_cluster):
        return {"saturation_score": 0.60, "cluster": target_cluster}

class MockGaps:
    def analyze_gaps(self, company_id):
        return [{"summary": "Lack of Authority Signals in vertical", "dimension": "messaging"}]

class MockCreative:
    def generate_signal(self, current_genome, industry):
        return {
            "signal_type": "FATIGUE",
            "severity": "HIGH",
            "archetype_id": "19"
        }

@pytest.fixture
def mock_context_builder():
    return ContextBuilder(
        memory_engine=MockMemory(),
        pressure_detector=MockPressure(),
        gap_analyzer=MockGaps(),
        creative_strategy=MockCreative()
    )


# --- 2. Tests ---

class TestContextBuilder:
    def test_build_snapshot(self, mock_context_builder):
        curr_campaigns = [
            {"id": "camp1", "spend": 100, "active_genomes": [{"hook_type": "shock"}]}
        ]
        snap = mock_context_builder.build_snapshot("comp1", "ecommerce", curr_campaigns)
        
        assert snap["company_id"] == "comp1"
        assert snap["current_performance"]["total_spend"] == 100
        assert snap["operator_memory"]["confidence"] == 0.85
        assert len(snap["creative_genome"]["active_campaign_signals"]) == 1


class TestSignalFusionEngine:
    def test_fusion(self, mock_context_builder):
        snap = mock_context_builder.build_snapshot("comp1", "ecommerce", [{"active_genomes": [{}]}])
        fusion = SignalFusionEngine()
        fused = fusion.fuse_context(snap)
        
        assert fused["momentum"] == "positive"
        assert fused["confidence_score"] == 0.85
        assert fused["directional_signals"]["operator_action"] == "EXECUTE"
        assert len(fused["directional_signals"]["recommended_creative_pivots"]) >= 0


class TestOpportunityDetector:
    def test_scan_opportunities(self, mock_context_builder):
        snap = mock_context_builder.build_snapshot("comp1", "ecommerce", [{"active_genomes": [{}]}])
        fused = SignalFusionEngine().fuse_context(snap)
        
        detector = OpportunityDetector()
        opps = detector.scan(fused)
        
        # Should find Budget Scaling (confidence > 0.70 & action EXECUTE & positive momentum)
        # Should find Creative Pivot (pivot id 19 inside directional_signals)
        # Should find Strategy Gap
        cats = [o["dimension"] for o in opps]
        assert "budget" in cats
        assert "creative" in cats
        assert "messaging" in cats


class TestThreatDetector:
    def test_scan_threats(self, mock_context_builder):
        snap = mock_context_builder.build_snapshot("comp1", "ecommerce", [{"active_genomes": [{}]}])
        fused = SignalFusionEngine().fuse_context(snap)
        
        # Fake a threatening fusion
        fused["momentum"] = "negative"
        fused["critical_flags"]["creative_fatigue"] = True
        fused["critical_flags"]["high_market_pressure"] = True
        
        detector = ThreatDetector()
        threats = detector.scan(fused)
        cats = [t["dimension"] for t in threats]
        
        assert "systemic" in cats  # negative baseline
        assert "market" in cats    # pressure
        assert "creative" in cats  # fatigue


class TestStrategyGenerator:
    def test_generate(self):
        gen = StrategyGenerator()
        opportunities = [
            {"dimension": "budget", "title": "Scale Budget", "rationale": "High conf"},
            {"dimension": "creative", "title": "New Angle", "rationale": "Pivot", "archetype_ids": ["12"]}
        ]
        threats = [
            {"dimension": "systemic", "severity": "high", "title": "Massive Drop", "rationale": "Bad."}
        ]
        
        payload = gen.generate(opportunities, threats)
        actions = payload["actions"]
        narrative = payload["narrative"]
        
        a_types = [a["action_type"] for a in actions]
        assert ActionType.SCALE_BUDGET in a_types
        assert ActionType.NEW_CREATIVE_ANGLE in a_types
        assert ActionType.PAUSE_CAMPAIGN in a_types
        assert "Strategic Analysis Output" in narrative


class TestOutcomePredictor:
    def test_predict_outcomes(self):
        pred = OutcomePredictor()
        action = {"action_type": "scale_budget"}
        ctx = {"operator_memory": {"predicted_lift": 0.20, "predicted_risk": 0.05, "confidence": 0.8}}
        
        res = pred.predict(action, ctx)
        assert res["expected_roas_delta"] > 0
        assert res["expected_cpa_delta"] == 0.05
        assert res["confidence"] > 0.70


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

class TestCaptainStrategyOrchestrator:
    def test_full_flow(self, db_session):
        # Re-init purely to override builder components natively without heavy patching
        captain = CaptainStrategy(db_session=db_session)
        captain.builder.memory = MockMemory()
        captain.builder.pressure = MockPressure()
        captain.builder.gaps = MockGaps()
        captain.builder.creative = MockCreative()

        # Run Brain Flow
        curr_campaigns = [{"id": "camp1", "active_genomes": [{"hook_type": "shock"}]}]
        strategy_res = captain.generate_strategy("comp1", "ecommerce", curr_campaigns)

        # Assert Data Package
        assert strategy_res["company_id"] == "comp1"
        assert len(strategy_res["actions"]) > 0
        assert "narrative" in strategy_res
        
        # Verify DB insertion
        strat_db = db_session.query(GeneratedStrategy).first()
        assert strat_db is not None
        assert strat_db.company_id == "comp1"
        assert strat_db.confidence_score > 0
        assert len(db_session.query(RecommendedAction).all()) > 0
