"""
Execution Engine - Autonomous execution of campaign changes
Applies decisions to campaigns via platform APIs
Supports manual and auto modes
"""

from fastapi import FastAPI
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Execution Engine"
API_VERSION = "0.1.0"
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

from backend.execution_engine.executor import CampaignExecutor
from backend.execution_engine.experimentation import ExperimentationFramework
from shared.utils.audit_logger import AuditLogger

executor = CampaignExecutor()
experiment_engine = ExperimentationFramework()

# Simulates persistence
MOCK_RECOMMENDATION_DB = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.Campaign, bm.BudgetAllocation, bm.User])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")

    yield

    try:
        close_mongo()
    except Exception:
        pass
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title=SERVICE_NAME,
    description="Campaign Execution and Automation Engine",
    version=API_VERSION,
    lifespan=lifespan
)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/execution/manual-mode")
async def execute_manual_mode(business_id: str, recommendations: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manual mode: Show recommendations and await user approval
    """
    import uuid
    # Store recommendations temporarily awaiting execution via approval ID
    rec_id = str(uuid.uuid4())
    MOCK_RECOMMENDATION_DB[rec_id] = {
        "business_id": business_id,
        "recommendations": recommendations,
        "status": "pending_approval",
        "created_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Queued manual recommendations for biz {business_id}. Rec ID: {rec_id}")
    return {
        "execution_mode": "manual",
        "business_id": business_id,
        "recommendation_id": rec_id,
        "status": "awaiting_approval",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/execution/auto-mode")
async def execute_auto_mode(business_id: str, decisions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto mode: Automatically apply changes with safety checks
    """
    logger.info(f"AUTO-MODE Engaged for biz: {business_id}")
    
    # Send decisions downstream to platforms
    logs = executor.execute_adjustments(business_id, decisions)
    
    return {
        "execution_mode": "auto",
        "business_id": business_id,
        "changes_applied": logs,
        "status": "executed",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/execution/approve")
async def approve_recommendation(business_id: str, recommendation_id: str) -> Dict[str, Any]:
    """
    Approve a recommendation for execution
    """
    if recommendation_id not in MOCK_RECOMMENDATION_DB:
        return {"success": False, "error": "Recommendation ID not found."}
        
    obj = MOCK_RECOMMENDATION_DB[recommendation_id]
    
    # Execute 
    logs = executor.execute_adjustments(business_id, obj.get('recommendations', {}))
    obj['status'] = 'executed'
    
    # Phase 7.1: Audit Trail Logging
    await AuditLogger.log_action(
        action="APPROVE_EXECUTION",
        resource_type="campaign_recommendation",
        business_id=business_id,
        resource_id=recommendation_id,
        after_state={"status": "executed", "logs": logs}
    )
    
    return {
        "success": True,
        "recommendation_id": recommendation_id,
        "status": "executed",
        "changes_applied": logs,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/execution/reject")
async def reject_recommendation(business_id: str, recommendation_id: str) -> Dict[str, Any]:
    """
    Reject a recommendation
    """
    if recommendation_id in MOCK_RECOMMENDATION_DB:
        MOCK_RECOMMENDATION_DB[recommendation_id]['status'] = 'rejected'
        
        # Phase 7.1: Audit Trail Logging
        await AuditLogger.log_action(
            action="REJECT_EXECUTION",
            resource_type="campaign_recommendation",
            business_id=business_id,
            resource_id=recommendation_id,
            after_state={"status": "rejected"}
        )
        
    return {
        "success": True,
        "recommendation_id": recommendation_id,
        "status": "rejected",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/execution/kill-switch")
async def emergency_kill_switch(business_id: str) -> Dict[str, Any]:
    """
    Emergency kill switch - pause all campaigns
    """
    executor.pause_all_campaigns(business_id)
    
    # Phase 7.1: Audit Trail Compliance Log
    await AuditLogger.log_action(
        action="EMERGENCY_KILL_SWITCH",
        resource_type="global_campaigns",
        business_id=business_id,
        after_state={"action": "all_campaigns_paused", "status": "KILLED"}
    )
    
    return {
        "success": True,
        "business_id": business_id,
        "action": "all_campaigns_paused",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==========================================
# EXPERIMENTATION API BLOCK
# ==========================================

@app.post("/api/v1/experiments/create")
async def create_experiment(business_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    hypothesis = payload.get("hypothesis", "Test")
    variants = payload.get("variants", [])
    
    exp_id = experiment_engine.create_hypothesis(business_id, hypothesis, variants)
    
    return {
        "success": True,
        "experiment_id": exp_id,
        "hypothesis": hypothesis,
        "timestamp": datetime.utcnow().isoformat()
    }
    
@app.post("/api/v1/experiments/{experiment_id}/record")
async def record_metrics(experiment_id: str, variant_id: str, data: Dict[str, float]) -> Dict[str, Any]:
    status = experiment_engine.record_metrics(experiment_id, variant_id, data)
    return {
        "success": status,
        "recorded_points": len(data),
        "timestamp": datetime.utcnow().isoformat()
    }
    
@app.get("/api/v1/experiments/{experiment_id}/score")
async def score_experiment(experiment_id: str) -> Dict[str, Any]:
    return experiment_engine.calculate_experiment_score(experiment_id)
    
@app.post("/api/v1/experiments/{experiment_id}/archive")
async def archive_experiment(experiment_id: str) -> Dict[str, Any]:
    return experiment_engine.archive_learning(experiment_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
