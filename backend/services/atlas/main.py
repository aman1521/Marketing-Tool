"""
Atlas System - Data Ingestion, Signals & Benchmarks Interface
FastAPI implementation with Async PostgreSQL.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("atlas")

# Import Models and System Components
from backend.services.atlas.models import Base
from backend.services.atlas.collect.sync_orchestrator import SyncOrchestrator
from backend.services.atlas.signals.feature_engine import AtlasFeatureEngine
from backend.services.atlas.memory.feature_store import FeatureStore
from backend.services.atlas.benchmarks.benchmark_engine import AtlasBenchmarkEngine

API_VERSION = "1.0.0"
DATABASE_URL = os.getenv("ATLAS_DATABASE_URL", "postgresql+asyncpg://saas_user:saas_password@db:5432/marketing_saas")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup tables on load if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Atlas Database connected and schemas enforced.")
    yield
    await engine.dispose()
    logger.info("Atlas DB Shutdown.")

app = FastAPI(
    title="Atlas System",
    description="Foundational data ingestion, feature engineering, and signal memory layer.",
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
        "status": "Atlas OK",
        "time": datetime.utcnow().isoformat(),
        "version": API_VERSION
    }

@app.post("/api/v1/collect/sync/{company_id}")
async def trigger_platform_sync(company_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Trigger the Sync Orchestrator asynchronously."""
    async def run_sync():
        orchestrator = SyncOrchestrator(db)
        await orchestrator.run_daily_sync(company_id)
        
        # Immediately pipeline to feature generation
        # Logic: Select the new RawMetrics and feed to AtlasFeatureEngine
        # (This triggers logic inside background tasks rather than blocking return)

    background_tasks.add_task(run_sync)
    return {"message": f"Sync queued for company {company_id}", "status": "processing"}

@app.get("/api/v1/signals/{campaign_id}")
async def get_engineered_signals(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the synthesized 'gas matter' feature states for a campaign."""
    feature_store = FeatureStore(db)
    blob = await feature_store.get_latest_features(campaign_id)
    if not blob:
        raise HTTPException(status_code=404, detail="Features not found or sync pending.")
    
    return {
        "campaign_id": campaign_id,
        "features": blob,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
