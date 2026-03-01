from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, JSON, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# ──────────────────────────────────────────────
# ENUMS
# ──────────────────────────────────────────────

class TeamRole(str, enum.Enum):
    OWNER = "owner"
    CMO = "cmo"
    MEDIA_BUYER = "media_buyer"
    CREATIVE_STRATEGIST = "creative_strategist"
    ANALYST = "analyst"
    FINANCE = "finance"
    VIEWER = "viewer"

class EscalationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ActivityType(str, enum.Enum):
    AI_EXECUTION = "ai_execution"
    ROLLBACK = "rollback"
    DRIFT_ALERT = "drift_alert"
    EXPERIMENT_LAUNCH = "experiment_launch"
    ESCALATION = "escalation"
    APPROVAL = "approval"
    CALIBRATION_PROPOSAL = "calibration_proposal"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    COMMENT = "comment"

class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

# ──────────────────────────────────────────────
# TEAM ECOSYSTEM
# ──────────────────────────────────────────────

class TeamMemberModel(Base):
    """Multi-user per company. Strict tenant-scoped."""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(TeamRole), nullable=False, default=TeamRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ──────────────────────────────────────────────
# ENVELOPE MODELS
# ──────────────────────────────────────────────

class BudgetEnvelopeModel(Base):
    """Hard guardrails bounding AI financial execution."""
    __tablename__ = "budget_envelopes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, unique=True, nullable=False)

    monthly_budget_cap = Column(Float, nullable=False)
    daily_change_limit_percent = Column(Float, nullable=False, default=10.0)
    max_portfolio_exposure = Column(Float, nullable=False)
    sandbox_percent_limit = Column(Float, nullable=False, default=5.0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)

class StrategyEnvelopeModel(Base):
    """Governance of what types of actions are permitted."""
    __tablename__ = "strategy_envelopes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, unique=True, nullable=False)

    allowed_strategy_types = Column(JSON, nullable=False, default=list)  # ["SCALE", "PAUSE", "BUDGET_SHIFT"]
    allowed_platforms = Column(JSON, nullable=False, default=list)        # ["meta", "google"]
    creative_change_limit = Column(Integer, nullable=False, default=5)    # max creatives per day
    max_risk_score = Column(Float, nullable=False, default=0.7)
    auto_execution_enabled = Column(Boolean, default=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ──────────────────────────────────────────────
# ESCALATION
# ──────────────────────────────────────────────

class EscalationLogModel(Base):
    """Full audit of every governance breach and outcome."""
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    escalation_id = Column(String, unique=True, nullable=False)

    breach_type = Column(String, nullable=False)   # BUDGET_BREACH, STRATEGY_BREACH, PORTFOLIO_BREACH
    action_payload = Column(JSON, nullable=False)
    envelope_snapshot = Column(JSON, nullable=False)
    exposure_snapshot = Column(JSON, nullable=False)
    risk_snapshot = Column(JSON, nullable=False)

    routed_to_roles = Column(JSON, nullable=False)   # ["finance", "owner"]
    status = Column(Enum(EscalationStatus), default=EscalationStatus.PENDING)
    resolved_by = Column(String, nullable=True)
    resolution_note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

# ──────────────────────────────────────────────
# ACTIVITY FEED
# ──────────────────────────────────────────────

class ActivityFeedModel(Base):
    """Structured event bus powering the real-time intelligence stream."""
    __tablename__ = "activity_feed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)

    activity_type = Column(Enum(ActivityType), nullable=False)
    actor = Column(String, nullable=False)         # "ai_engine" or user_id
    summary = Column(String, nullable=False)       # Human-readable 1-liner
    payload = Column(JSON, nullable=True)          # Full structured data

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# ──────────────────────────────────────────────
# DECISION THREADS
# ──────────────────────────────────────────────

class DecisionThreadModel(Base):
    """Full traceability record per AI action."""
    __tablename__ = "decision_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    thread_id = Column(String, unique=True, nullable=False)

    action_type = Column(String, nullable=False)
    envelope_snapshot = Column(JSON, nullable=False)
    risk_context = Column(JSON, nullable=False)
    simulation_summary = Column(JSON, nullable=False)
    execution_result = Column(JSON, nullable=True)

    comments = Column(JSON, default=list)
    approval_history = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

# ──────────────────────────────────────────────
# TASKS
# ──────────────────────────────────────────────

class TaskModel(Base):
    """Auto-created tasks from AI signal detection."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    task_id = Column(String, unique=True, nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    signal_type = Column(String, nullable=False)  # CREATIVE_FATIGUE, CONVERSION_ISSUE, FUNNEL_GAP
    assigned_role = Column(Enum(TeamRole), nullable=False)
    assigned_to_user_id = Column(String, nullable=True)

    supporting_signals = Column(JSON, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    completion_note = Column(Text, nullable=True)

# ──────────────────────────────────────────────
# PORTFOLIO RISK
# ──────────────────────────────────────────────

class PortfolioRiskModel(Base):
    """Snapshot of portfolio-level exposure per company per compute cycle."""
    __tablename__ = "portfolio_risk_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)

    total_capital_at_risk = Column(Float, nullable=False)
    cross_campaign_exposure = Column(Float, nullable=False)
    volatility_adjusted_risk_index = Column(Float, nullable=False)
    autonomy_exposure_pct = Column(Float, nullable=False)
    worst_case_downside = Column(Float, nullable=False)

    computed_at = Column(DateTime, default=datetime.utcnow, index=True)

# ──────────────────────────────────────────────
# USAGE
# ──────────────────────────────────────────────

class UsageSnapshotModel(Base):
    """Per-tenant metered usage for billing and impact analysis."""
    __tablename__ = "usage_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)

    executions_count = Column(Integer, default=0)
    budget_modified_usd = Column(Float, default=0.0)
    experiments_launched = Column(Integer, default=0)
    creative_analyses = Column(Integer, default=0)
    calibration_runs = Column(Integer, default=0)
    escalations_triggered = Column(Integer, default=0)
    approvals_pending = Column(Integer, default=0)

    autonomy_percentage = Column(Float, default=0.0)  # % of actions taken autonomously
    avg_approval_latency_minutes = Column(Float, default=0.0)

    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
