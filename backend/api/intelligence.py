"""
Intelligence API
================
FastAPI router surfacing the autonomous Intelligence cycle to the Frontend.
Allows human operators to trigger, monitor, and review AI generated strategies.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
# If SQLAlchemy was fully wired we'd inject session DBs here
# from sqlalchemy.orm import Session

from backend.schemas.intelligence_schema import StrategyRunRequest, StrategyRunResponse, BackgroundTaskResponse
from backend.services.intelligence.orchestrator.main_loop import UnifiedIntelligenceOrchestrator

# Import the Celery task physical handler
from worker.celery_worker import run_intelligence_cycle_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence"])

# Dependency mock - replace with actual get_db
def get_db():
    yield None

@router.post("/run-synchronous", response_model=StrategyRunResponse)
async def trigger_intelligence_loop(request: StrategyRunRequest, db: Any = Depends(get_db)):
    """
    Manually forces the Agent Council & Simulation twin to evaluate the current context
    and execute changes immediately (Blocking/Synchronous output).
    """
    logger.info(f"[API] Manual Intelligence run triggered for {request.company_id}")
    
    try:
        orchestrator = UnifiedIntelligenceOrchestrator(db_session=db)
        
        # main_loop.py is async, so we await it natively in the FastAPI event loop
        result = await orchestrator.execute_intelligence_loop(
            company_id=request.company_id,
            industry=request.industry,
            current_campaigns=request.current_campaigns
        )
        
        return StrategyRunResponse(
            status=result.get("status", "unknown"),
            strategy_id=result.get("strategy"),
            council_confidence=result.get("council_confidence", 0.0),
            actions_simulated=result.get("actions_simulated", 0),
            actions_executed=result.get("actions_executed", 0),
            reason=result.get("reason"),
            execution_mapping=result.get("execution_mapping", {})
        )
        
    except Exception as e:
        logger.error(f"[API] Intelligence cycle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-async", response_model=BackgroundTaskResponse)
async def trigger_intelligence_loop_bg(request: StrategyRunRequest):
    """
    Dispatches the Intelligence cycle to a distributed background worker (Celery).
    This is best practice for production UI so the browser doesn't hang.
    """
    logger.info(f"[API] Dispatching Celery background task for {request.company_id}")
    
    try:
         task = run_intelligence_cycle_task.delay(
             company_id=request.company_id,
             industry=request.industry,
             campaigns=request.current_campaigns
         )
         
         return BackgroundTaskResponse(
             task_id=task.id,
             status="enqueued",
             message="Intelligence Matrix is booting up in the background."
         )
    except Exception as e:
         logger.error(f"[API] Background dispatch failed: {e}")
         raise HTTPException(status_code=500, detail="Failed to connect to required Celery/Redis Broker")
