import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from backend.services.execution.hawkeye.vision_engine import VisionEngine
from backend.services.execution.hawkeye.copy_engine import CopyEngine
from backend.services.execution.hawkeye.funnel_engine import FunnelEngine
from backend.services.execution.hawkeye.embedding_engine import EmbeddingEngine
from backend.services.execution.hawkeye.fatigue_engine import FatigueEngine
from backend.services.execution.hawkeye.hawkeye_engine import HawkeyeEngine

# --- Core Inference Logic Tests ---

def test_copy_engine_determinism():
    engine = CopyEngine()
    
    res = engine.analyze_copy("Limited time offer! Act now", "SALE EXPIRES TODAY")
    
    assert res.urgency_detected == True
    assert res.primary_emotion == "urgency"
    assert res.offer_extracted == "Standard"
    
    res_2 = engine.analyze_copy("Struggling to sleep? Our proven pill guarantees rest.", "Fix your bad sleep")
    
    assert res_2.urgency_detected == False
    assert res_2.primary_emotion == "trust" # Picks up guarantee & proven
    assert res_2.problem_framing_score > 0.5

def test_funnel_engine_friction():
    engine = FunnelEngine()
    
    res_bad = engine.extract_funnel_health("https://spam.com/form-clutter")
    res_good = engine.extract_funnel_health("https://brand.com/clear-reviews")
    
    assert res_bad.friction_indicators == 7
    assert res_bad.funnel_gap_score > res_good.funnel_gap_score
    assert res_good.trust_signals_count == 4

def test_fatigue_engine_decay_logic():
    engine = FatigueEngine()
    
    # Severe decay array
    historical_ctr = [3.0, 2.5, 1.5, 0.5] 
    
    res = engine.calculate_lifecycle_fatigue(historical_ctr, 1000.0, 0.8)
    
    # Decay = (3.0 - 0.5) / 3.0 = 83% drop | Penalty = 0.8 * 0.3 = 0.24 | Total > 1.0 (capped 1.0)
    assert res["fatigue_score"] == 1.0 
    assert res["stage"].value == "dead"
    
    # Fresh campaign array
    res_2 = engine.calculate_lifecycle_fatigue([1.2, 1.4, 1.5], 50.0, 0.0)
    
    assert res_2["fatigue_score"] == 0.0
    assert res_2["stage"].value == "fresh"

def test_embedding_engine_similarity():
    engine = EmbeddingEngine()
    
    vec_a = [0.1, 0.2, 0.3, 0.4]
    vec_b = [0.1, 0.2, 0.3, 0.4]
    vec_diff = [0.9, 0.1, 0.0, 0.0]
    
    sim_match = engine.check_similarity(vec_a, [vec_b])
    sim_diff = engine.check_similarity(vec_a, [vec_diff])
    
    assert sim_match > 0.99 # Identical
    assert sim_diff < sim_match

# --- Orchestrator Validation ---
@pytest.mark.asyncio
async def test_hawkeye_engine_complete_output_schema():
    mock_db = AsyncMock()
    # Stub the DB returning empty history
    mock_db.execute.return_value.scalar_one_or_none.return_value = None 
    
    hawkeye = HawkeyeEngine(mock_db)
    
    # Mocking internal registry so we don't need real DB connection
    hawkeye.registry.log_creative = AsyncMock()
    hawkeye.registry.get_historical_embeddings = AsyncMock(return_value=[[0.0]*16])
    
    result = await hawkeye.analyze_creative(
        company_id="comp_123",
        campaign_id="camp_999",
        creative_id="asset_hero_1",
        asset_url="https://cdn.com/fast_video.mp4",
        landing_page_url="https://site.com/clear-reviews",
        primary_text="Limited offer today!",
        headline="Hurry!",
        historical_ctr=[1.5, 1.4, 1.0],  # Mild decay
        historical_spend=2000.0
    )
    
    # Validate strictly typed output schema matches prompt requirements
    assert "creative_id" in result
    assert result["creative_id"] == "asset_hero_1"
    assert "hook_strength" in result
    assert result["emotional_tone"] == "urgency"
    assert "offer_clarity_score" in result
    assert "fatigue_score" in result
    assert result["creative_cluster"] == "urgency_Standard"
    
    hawkeye.registry.log_creative.assert_called_once()
