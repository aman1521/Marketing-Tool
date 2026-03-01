"""
Business Service - Handles business logic and constraints
Validates business rules, applies constraints, manages business profiles
"""

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from contextlib import asynccontextmanager
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
from shared.models.beanie_models import Business as BusinessModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Business Service"
API_VERSION = "0.1.0"


class BusinessLogic(BaseModel):
    business_id: str
    margin_percentage: Optional[float]
    sales_cycle_days: Optional[int]
    subscription_model: bool


class BusinessConstraints(BaseModel):
    max_daily_budget: float
    min_roas_threshold: float
    allow_aggressive_scaling: bool
    max_budget_change_percentage: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")

    # Initialize MongoDB/Beanie
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [BusinessModel])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")

    yield

    # Shutdown
    try:
        close_mongo()
    except Exception:
        pass
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title=SERVICE_NAME,
    description="Business Logic and Constraint Validation",
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


@app.post("/api/v1/business/validate-constraints")
async def validate_constraints(business: BusinessLogic) -> Dict[str, Any]:
    """
    Validate business constraints based on business profile
    Applies business-specific rules
    """
    
    constraints = {
        "allow_aggressive_scaling": True,
        "enable_retention_mode": False,
        "enable_nurture_mode": False,
        "reason": "Constraints validated"
    }
    
    # Rule: If margin < 20% → Restrict Aggressive Scaling
    if business.margin_percentage and business.margin_percentage < 20:
        constraints["allow_aggressive_scaling"] = False
        constraints["reason"] = "Low margin detected - restricting aggressive scaling"
    
    # Rule: If sales_cycle > 30 days → Activate Nurture Mode
    if business.sales_cycle_days and business.sales_cycle_days > 30:
        constraints["enable_nurture_mode"] = True
        constraints["reason"] = "Long sales cycle detected - enabling nurture mode"
    
    # Rule: If subscription_model → Enable Retention Optimization
    if business.subscription_model:
        constraints["enable_retention_mode"] = True
        constraints["reason"] = "Subscription model detected - enabling retention optimization"
    
    logger.info(f"Constraints validation for business {business.business_id}: {constraints}")
    
    return {
        "business_id": business.business_id,
        "constraints": constraints,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/business/{business_id}")
async def get_business(business_id: str) -> Dict[str, Any]:
    """
    Get business profile and constraints
    """
    # TODO: Fetch from database
    return {
        "business_id": business_id,
        "message": "Business profile - database implementation pending"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
