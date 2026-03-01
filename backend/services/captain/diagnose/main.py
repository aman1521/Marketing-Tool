"""
Decision Engine - Deterministic rule-based decision making
Applies business logic rules to make campaign decisions
"""

from fastapi import FastAPI
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Captain Diagnose"
API_VERSION = "0.1.0"
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

from backend.services.captain.risk.rules import DeterministicRulesEngine

rules_engine = DeterministicRulesEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.Business, bm.Campaign, bm.User])
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
    description="Deterministic Rule-Based Decision Engine",
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


@app.post("/api/v1/decisions/evaluate")
async def evaluate_decision(business_id: str, decision_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate decision using deterministic rules:
    1. Platform Fit Score
    2. Budget Scaling Logic
    3. Creative Replacement Logic
    """
    
    # Platform Fit Score
    metrics = decision_input.get("platform_metrics", {})
    fit_score = rules_engine.calculate_platform_fit_score(metrics)
    
    # Budget Scaling
    target_roas = decision_input.get("target_roas", 2.0)
    actual_roas = decision_input.get("actual_roas", 1.0)
    spend_velocity = decision_input.get("spend_velocity", 1.0)
    
    action, scale_factor = rules_engine.evaluate_budget_scaling(
        roas=actual_roas, 
        target_roas=target_roas, 
        spend_velocity=spend_velocity
    )
    
    # Apply Risk
    current_budget = decision_input.get("current_budget", 1000)
    max_increase = decision_input.get("max_daily_budget_increase", 500)
    
    suggested_budget = current_budget * scale_factor
    diff = suggested_budget - current_budget
    
    if diff > 0:
        diff_validated = rules_engine.apply_risk_validation(diff, max_increase)
        final_budget = current_budget + diff_validated
    else:
        final_budget = suggested_budget
        
    final_scale_factor = final_budget / current_budget if current_budget > 0 else 1.0
    
    # Creative Replacing
    creative_score = decision_input.get("creative_score", 50)
    frequency = decision_input.get("frequency", 2.0)
    days_active = decision_input.get("days_active", 5)
    
    should_replace, replace_reason = rules_engine.evaluate_creative_replacement(
        creative_score=creative_score, 
        frequency=frequency, 
        days_active=days_active
    )
    
    logger.info(f"Decision evaluated for {business_id}. Action: {action}")
    
    return {
        "business_id": business_id,
        "platform_fit_score": fit_score,
        "recommended_action": action,
        "suggested_budget": round(final_budget, 2),
        "budget_scaling_factor": round(final_scale_factor, 2),
        "should_replace_creative": should_replace,
        "creative_replace_reason": replace_reason,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/decisions/rules")
async def get_decision_rules() -> Dict[str, Any]:
    """
    Get active decision rules
    """
    # TODO: Return current rule configuration
    
    return {
        "rules": {
            "platform_fit_scoring": {},
            "budget_scaling": {},
            "creative_replacement": {}
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
