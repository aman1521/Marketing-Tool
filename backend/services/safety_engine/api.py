import logging
import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from backend.services.safety_engine.models import Base
from backend.services.safety_engine.genesis_engine import GenesisEngine
from backend.services.safety_engine.schemas import (
    ProfileUpdateRequest, GoalMode, GenesisProfileSchema, GenesisGoalsSchema, GenesisConstraintsSchema,
    GoalsUpdateRequest, ConstraintsUpdateRequest, GenesisFullResponse, BudgetTier, FunnelType, IndustryType, GrowthStage, TimelinePriority
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("genesis")

API_VERSION = "1.0.0"
DATABASE_URL = os.getenv("GENESIS_DATABASE_URL", "postgresql+asyncpg://saas_user:saas_password@db:5432/marketing_saas")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Genesis DB schemas strictly enforced.")
    yield
    await engine.dispose()
    logger.info("Genesis DB Shutdown.")

app = FastAPI(
    title="Genesis System API",
    description="Business structure definition and governance logic layer.",
    version=API_VERSION,
    lifespan=lifespan
)

# --- Dependency ---
async def get_db():
    async with async_session() as session:
        yield session


@app.get("/health")
async def health_check():
    return {
        "status": "Genesis Governance Engine running.",
        "time": datetime.utcnow().isoformat(),
        "version": API_VERSION
    }

# ================= Read =================

@app.get("/api/v1/genesis/{company_id}")
async def fetch_genesis_configuration(company_id: str, db: AsyncSession = Depends(get_db)):
    """Exposes fully structured context matrix to Atlas, Captain, and endpoints deterministically."""
    g_engine = GenesisEngine(db)
    payload = await g_engine.get_active_genesis(company_id)
    if not payload:
        raise HTTPException(status_code=404, detail=f"Genesis block not found for {company_id}")
    return payload

@app.get("/api/v1/genesis/{company_id}/history")
async def fetch_genesis_history(company_id: str, db: AsyncSession = Depends(get_db)):
    """Pulls appending tracked metadata for ML auditing limits."""
    g_engine = GenesisEngine(db)
    return await g_engine.get_version_history(company_id)

# ================= Create/Mutate =================
@app.post("/api/v1/genesis/{company_id}/initialize")
async def initialize_genesis(company_id: str, db: AsyncSession = Depends(get_db)):
    """Mock test endpoint to map basic structural dependencies directly into DB"""
    g_engine = GenesisEngine(db)
    
    # Check
    existing = await g_engine.get_active_genesis(company_id)
    if existing:
         raise HTTPException(status_code=400, detail="Genesis already compiled for this ID.")
         
    # Mock Standard Inputs 
    p = GenesisProfileSchema(industry=IndustryType.ECOMMERCE, aov=120, gross_margin=0.5, funnel_type=FunnelType.DIRECT_CHECKOUT, geography="US", growth_stage=GrowthStage.SCALING, budget_tier=BudgetTier.SMB).model_dump()
    g = GenesisGoalsSchema(goal_mode=GoalMode.PROFIT_FIRST, target_roas=2.5, scaling_aggressiveness=0.8, timeline_priority=TimelinePriority.SHORT_TERM).model_dump()
    c = GenesisConstraintsSchema(max_budget_change_percent=15, max_daily_budget=1000, max_risk_score=0.7, auto_execution_enabled=False, creative_sandbox_required=True, landing_page_auto_edit_allowed=False).model_dump()
    
    return await g_engine.initialize_genesis(company_id, p, g, c)
    

@app.put("/api/v1/genesis/{company_id}/profile")
async def commit_profile_mutation(company_id: str, req: ProfileUpdateRequest, db: AsyncSession = Depends(get_db)):
    g_engine = GenesisEngine(db)
    try:
        return await g_engine.update_profile(company_id, req.profile.model_dump(), req.change_reason)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.put("/api/v1/genesis/{company_id}/goals")
async def commit_goal_mutation(company_id: str, req: GoalsUpdateRequest, db: AsyncSession = Depends(get_db)):
    g_engine = GenesisEngine(db)
    try:
        return await g_engine.update_goals(company_id, req.goals.model_dump(), req.change_reason)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.put("/api/v1/genesis/{company_id}/constraints")
async def commit_constraints_mutation(company_id: str, req: ConstraintsUpdateRequest, db: AsyncSession = Depends(get_db)):
    g_engine = GenesisEngine(db)
    try:
        return await g_engine.update_constraints(company_id, req.constraints.model_dump(), req.change_reason)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
