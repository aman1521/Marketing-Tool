import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from backend.services.genesis.schemas import (
    GenesisProfileSchema, GenesisGoalsSchema, GenesisConstraintsSchema,
    IndustryType, FunnelType, GrowthStage, BudgetTier, GoalMode, TimelinePriority
)
from backend.services.genesis.profile import GenesisProfileManager
from backend.services.genesis.goals import GenesisGoalsManager
from backend.services.genesis.constraints import GenesisConstraintsManager
from backend.services.genesis.genesis_engine import GenesisEngine
from backend.services.genesis.mapping import GenesisMapping

# ================= Schemas & Validation Tests =================

def test_profile_validation_success():
    manager = GenesisProfileManager()
    payload = {
        "industry": "ecommerce",
        "aov": 150.50,
        "gross_margin": 0.45,
        "funnel_type": "direct_checkout",
        "geography": "US",
        "growth_stage": "scaling",
        "budget_tier": "mid"
    }
    
    validated = manager.validate_profile(payload)
    assert validated.industry == IndustryType.ECOMMERCE
    assert validated.aov == 150.50

def test_profile_validation_failure():
    manager = GenesisProfileManager()
    payload = {
        "industry": "ecommerce",
        "aov": -10,  # Invalid: must be gt=0
        "gross_margin": 1.5, # Invalid: must be le=1.0
        "funnel_type": "direct_checkout",
        "geography": "US",
        "growth_stage": "scaling",
        "budget_tier": "mid"
    }
    
    with pytest.raises(ValueError):
        manager.validate_profile(payload)

def test_goals_validation_mode_dependencies():
    manager = GenesisGoalsManager()
    
    # Scale Mode requires target_roas/cpa AND high aggressiveness
    payload_invalid = {
        "goal_mode": "scale_first",
        "target_roas": None,  # Invalid: requires target
        "target_cpa": None,
        "scaling_aggressiveness": 0.3, # Invalid: requires >= 0.5
        "timeline_priority": "short_term"
    }
    
    with pytest.raises(ValueError) as e:
        manager.validate_goals(payload_invalid)
        
    payload_valid = {
        "goal_mode": "scale_first",
        "target_roas": 2.5,  
        "target_cpa": None,
        "scaling_aggressiveness": 0.8, 
        "timeline_priority": "short_term"
    }
    
    validated = manager.validate_goals(payload_valid)
    assert validated.goal_mode == GoalMode.SCALE_FIRST

def test_constraints_validation_enforcement():
    manager = GenesisConstraintsManager()
    payload = {
        "max_budget_change_percent": 150.0, # Invalid: le=100.0
        "max_daily_budget": 5000,
        "min_allowed_roas": 0.5,
        "max_risk_score": 0.8,
        "auto_execution_enabled": True,
        "creative_sandbox_required": True,
        "landing_page_auto_edit_allowed": False
    }
    
    with pytest.raises(ValueError):
        manager.validate_constraints(payload)

# ================= Engine & DB Logic Mock Tests =================

@pytest.mark.asyncio
async def test_genesis_initialization_versioning():
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None # No existing state
    
    engine = GenesisEngine(mock_db)
    # Patch Versioning Manager's creation strictly
    engine.versioning.create_snapshot = AsyncMock()
    
    profile = {"industry": "ecommerce", "aov": 150, "gross_margin": 0.5, "funnel_type": "direct_checkout", "geography": "US", "growth_stage": "scaling", "budget_tier": "smb"}
    goals = {"goal_mode": "profit_first", "target_roas": 2.5, "scaling_aggressiveness": 0.8, "timeline_priority": "short_term"}
    constraints = {"max_budget_change_percent": 15, "max_daily_budget": 1000, "max_risk_score": 0.7, "auto_execution_enabled": False, "creative_sandbox_required": True, "landing_page_auto_edit_allowed": False}
    
    # Mock return
    mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock(
        company_id="test_cmp", version=1, profile_data=profile, goals_data=goals, constraints_data=constraints,
        updated_at=datetime.utcnow()
    )
    
    await engine.initialize_genesis("test_cmp", profile, goals, constraints)
    
    mock_db.add.assert_called()
    mock_db.commit.assert_called()
    # Confirm versioning logged iteration 1
    engine.versioning.create_snapshot.assert_called_with(
        "test_cmp", 1, profile, goals, constraints, "system", "Initial Setup"
    )

@pytest.mark.asyncio
async def test_safe_update_increments_version_and_preserves_history():
    mock_db = AsyncMock()
    
    existing_record = MagicMock(
         company_id="test_cmp", version=1, 
         profile_data={"old": "data"}, goals_data={"old": "data"}, constraints_data={"old": "data"},
         updated_at=datetime.utcnow()
    )
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing_record
    
    engine = GenesisEngine(mock_db)
    engine.versioning.create_snapshot = AsyncMock()
    
    new_profile = {"industry": "ecommerce", "aov": 150.50, "gross_margin": 0.45, "funnel_type": "direct_checkout", "geography": "US", "growth_stage": "scaling", "budget_tier": "mid"}
    
    await engine._safe_update("test_cmp", "profile", new_profile, "user_xyz", "Changed Industry AOV")
    
    # Verify version bump on original record without destructing
    assert existing_record.version == 2
    assert existing_record.profile_data == new_profile
    assert existing_record.goals_data == {"old": "data"} # Persisted unmodified logic securely
    
    # Verify Versioning History accurately triggered
    engine.versioning.create_snapshot.assert_called_with(
        company_id="test_cmp",
        version=2,
        profile=new_profile,
        goals={"old": "data"},
        constraints={"old": "data"},
        changed_by="user_xyz",
        change_reason="Changed Industry AOV"
    )
