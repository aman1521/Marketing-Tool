"""
Intelligence Orchestrator - Merges ML outputs and applies business constraints
Produces structured decision objects for Decision Engine
"""

from fastapi import FastAPI
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Intelligence Orchestrator"
API_VERSION = "0.1.0"
import os
import sys
import httpx
from pydantic import BaseModel
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

from backend.intelligence_orchestrator.llm_strategy import LLMStrategyGenerator

DECISION_ENGINE_URL = os.getenv("DECISION_ENGINE_URL", "http://decision_engine:8007")

llm_generator = LLMStrategyGenerator(provider="openai")

class OrchestrationRequest(BaseModel):
    business_context: Dict[str, Any]
    ml_predictions: List[Dict[str, Any]]
    behavior_intent: Dict[str, Any]



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.MLPrediction, bm.StrategyOutput, bm.User])
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
    description="Intelligence Orchestrator",
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


@app.post("/api/v1/orchestrate/merge-intelligence")
async def merge_intelligence(business_id: str, request: OrchestrationRequest) -> Dict[str, Any]:
    """
    Merge all ML outputs into structured decision object
    Apply business constraints and risk validation via Decision Engine
    Pass context to LLM strategy layer
    """
    
    # Extract prediction elements to pass to Decision Engine
    decision_input = {
        "target_roas": request.business_context.get("target_roas", 2.0),
        "current_budget": request.business_context.get("monthly_budget", 1000) / 30, # Approx daily
        "max_daily_budget_increase": request.business_context.get("max_daily_budget_increase", 50),
        "platform_metrics": {
            "normalized_roas_score": 80,
            "normalized_engagement_score": 70,
            "normalized_volume_score": 60,
            "normalized_growth_score": 65
        },
        "actual_roas": 0.0,
        "spend_velocity": 1.0,
        "creative_score": 50,
        "frequency": 2.0,
        "days_active": 10
    }
    
    # Try to map actual ML outputs to decision input
    for pred in request.ml_predictions:
        if pred.get("model_type") == "roas_prediction":
            decision_input["actual_roas"] = pred.get("prediction", 0.0)
        elif pred.get("model_type") == "creative_performance":
            decision_input["creative_score"] = pred.get("prediction", 50)
            
    # 1. Ask Decision Engine for deterministic logic
    decision_outcome = {}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DECISION_ENGINE_URL}/api/v1/decisions/evaluate",
                params={"business_id": business_id},
                json=decision_input,
                timeout=5.0
            )
            if resp.status_code == 200:
                decision_outcome = resp.json()
    except Exception as e:
        logger.warning(f"Failed to reach Decision Engine: {e}")
        decision_outcome = {"error": "Decision Engine Unavailable", "recommended_action": "hold"}
        
    # 2. Inject context into LLM Strategy Layer
    strategy_response = await llm_generator.generate_strategy(
        business_context=request.business_context,
        ml_preds=request.ml_predictions,
        behavior_intent=request.behavior_intent
    )
    
    # 3. Merge outputs
    merged_intelligence = {
        "business_id": business_id,
        "timestamp": datetime.utcnow().isoformat(),
        "deterministic_decision": decision_outcome,
        "llm_strategy": strategy_response.get("strategy", "No strategy generated."),
        "risk_flags": []
    }
    
    # Flag risks natively
    if decision_outcome.get("recommended_action") == "scale_down":
        merged_intelligence["risk_flags"].append("ROAS_FAILING_SCALE_DOWN")
        
    return merged_intelligence


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
