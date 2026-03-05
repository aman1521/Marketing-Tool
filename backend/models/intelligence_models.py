"""
AI Intelligence Logging Layer
=============================
Stores historic AI Strategies, Simulations, and generated Content (Ad Scripts)
so humans and users can review the Debate/Reasoning in the Dashboard.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from backend.database import Base

class AIModuleEnum(str, enum.Enum):
    STRATEGY_COUNCIL = "multi_agent_council"
    CAPTAIN_STRATEGY = "captain_brain"
    SIMULATOR = "strategy_simulator"
    CREATIVE_GEN = "creative_generator"
    COMPETITOR_INTEL = "competitor_analysis"

class AIStrategySession(Base):
    """
    The umbrella event connecting all AI decisions to a specific
    cron schedule or manual trigger in the frontend.
    """
    __tablename__ = "ai_strategy_sessions"

    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    triggered_by_user = Column(String, nullable=True) # If null, triggered by Celery Beat
    
    status = Column(String, default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Store the output summary payload that goes to the FrontEnd UI
    orchestrator_summary_json = Column(JSON, default=dict)
    
    # Relations
    actions = relationship("AIActionLog", back_populates="session", cascade="all, delete-orphan")

class AIActionLog(Base):
    """
    The granular breakdown of which module did what during the session.
    Example: Simulator blocked +25% Meta Spend.
    """
    __tablename__ = "ai_action_logs"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("ai_strategy_sessions.id"))
    module = Column(Enum(AIModuleEnum))
    
    action_type = Column(String) # e.g. BLOCK, SCALE, PIVOT, GENERATE_CREATIVE
    reasoning_summary = Column(String) 
    
    # E.g. {"confidence": 0.88, "risk": 0.2, "variables_changed": ["target_audience"]}
    parameters_json = Column(JSON, default=dict)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("AIStrategySession", back_populates="actions")

class AIGeneratedCreative(Base):
    """
    Physical output from the Creative Intelligence Engine (e.g., Video Scripts, Ad Hooks)
    waiting for human approval or automated dispatch.
    """
    __tablename__ = "ai_generated_creatives"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    
    target_platform = Column(String) # TikTok, Reddit, etc
    visual_concept = Column(String)
    hook_variant = Column(String)
    full_script_markdown = Column(String)
    
    # Track the success of the AI
    originating_insight_json = Column(JSON, default=dict) # The mathematical DNA pattern that built this

    status = Column(String, default="pending_review") # pending_review, approved, deployed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
