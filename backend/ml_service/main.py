"""
ML Service - Machine Learning Model Training and Inference
Handles 4 core models: Audience Clustering, Creative Performance, ROAS Prediction, Budget Optimization
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
import httpx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

from backend.ml_service.models.audience_clustering import AudienceClusteringModel
from backend.ml_service.models.roas_prediction import ROASPredictionModel
from backend.ml_service.models.budget_optimization import BudgetOptimizationModel
from backend.ml_service.models.creative_performance import CreativePerformanceModel
import asyncio
from backend.ml_service.feature_store_cron import start_cron_scheduler

audience_model = AudienceClusteringModel()
roas_model = ROASPredictionModel()
budget_model = BudgetOptimizationModel()
creative_model = CreativePerformanceModel()

BEHAVIOR_ANALYZER_URL = os.getenv("BEHAVIOR_ANALYZER_URL", "http://behavior_analyzer_service:8009")


class PredictionRequest(BaseModel):
    business_id: str
    model_type: str  # audience, creative, roas, budget_optimization
    features: Dict[str, Any]


class PredictionResponse(BaseModel):
    business_id: str
    model_type: str
    prediction: float
    confidence: float
    features_used: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    # Initialize MongoDB/Beanie
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.MLPrediction, bm.Business, bm.User])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")

    # Load pre-trained models from disk
    audience_model.load()
    roas_model.load()
    creative_model.load()
    
    # Start automated feature aggregation background cron task
    cron_task = asyncio.create_task(start_cron_scheduler(interval_seconds=3600))
    
    yield

    try:
        cron_task.cancel()
        close_mongo()
    except Exception:
        pass
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title=SERVICE_NAME,
    description="ML Model Training and Inference Engine",
    version=API_VERSION,
    lifespan=lifespan
)

ML_MODELS = ["audience_clustering", "creative_performance", "roas_prediction", "budget_optimization"]


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "models_available": ML_MODELS,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ml/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> Dict[str, Any]:
    """
    Generate prediction using specified model
    
    Models:
    - audience_clustering: Returns cluster ID + profitability score
    - creative_performance: Returns predicted CTR + CVR + creative score
    - roas_prediction: Returns predicted ROAS
    - budget_optimization: Returns recommended budget allocation
    """
    
    if request.model_type not in ML_MODELS:
        raise HTTPException(status_code=400, detail=f"Model {request.model_type} not found")
    
    # Check if intent signals are provided, and if so, fetch intent features
    if "intent_signals" in request.features:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{BEHAVIOR_ANALYZER_URL}/api/v1/classify/intent",
                    json=request.features["intent_signals"],
                    timeout=5.0
                )
                if resp.status_code == 200:
                    intent_data = resp.json()
                    request.features["intent_segment"] = intent_data.get("intent_segment")
                    request.features["intent_strength"] = intent_data.get("intent_strength")
                    request.features["roas_potential"] = intent_data.get("expected_roas_potential")
        except Exception as e:
            logger.warning(f"Failed to fetch intent features from Behavior Analyzer: {e}")

    logger.info(f"Prediction request for {request.model_type} from business {request.business_id}")
    
    prediction = None
    confidence = 0.0

    if request.model_type == "audience_clustering":
        res = audience_model.predict(request.features)
        prediction = res.get("cluster_id", 0)
        confidence = res.get("confidence", 0.0)
        request.features["roas_multiplier"] = res.get("roas_multiplier", 1.0)
        
    elif request.model_type == "roas_prediction":
        res = roas_model.predict(request.features)
        prediction = res.get("predicted_roas", 0.0)
        confidence = res.get("confidence", 0.0)
        
    elif request.model_type == "budget_optimization":
        res = budget_model.predict(request.features)
        prediction = 1.0 # Successful run
        confidence = 1.0
        request.features["allocations"] = res.get("allocations", {})
        
    elif request.model_type == "creative_performance":
        res = creative_model.predict(request.features)
        prediction = res.get("creative_score", 0.0)
        confidence = res.get("confidence", 0.0)
        request.features["predicted_ctr"] = res.get("predicted_ctr", 0.0)
        request.features["predicted_cvr"] = res.get("predicted_cvr", 0.0)

    return {
        "business_id": request.business_id,
        "model_type": request.model_type,
        "prediction": float(prediction),
        "confidence": float(confidence),
        "features_used": request.features
    }


@app.post("/api/v1/ml/batch-predict")
async def batch_predict(requests: List[PredictionRequest]) -> Dict[str, Any]:
    """
    Generate multiple predictions efficiently
    """
    # TODO: Implement batch prediction logic
    
    return {
        "success": True,
        "predictions": [],
        "total_requests": len(requests),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/ml/models")
async def list_models() -> Dict[str, Any]:
    """
    Get information about available models
    """
    # TODO: Return model metadata, versions, performance metrics
    
    return {
        "models": [
            {
                "name": "audience_clustering",
                "version": "1.0",
                "accuracy": None,
                "last_trained": None
            },
            {
                "name": "creative_performance",
                "version": "1.0",
                "accuracy": None,
                "last_trained": None
            },
            {
                "name": "roas_prediction",
                "version": "1.0",
                "rmse": None,
                "last_trained": None
            },
            {
                "name": "budget_optimization",
                "version": "1.0",
                "algorithm": "multi-armed bandit",
                "last_trained": None
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ml/retrain/{model_type}")
async def retrain_model(model_type: str) -> Dict[str, Any]:
    """
    Trigger retraining of specified model
    Uses latest data from database
    """
    if model_type not in ML_MODELS:
        raise HTTPException(status_code=400, detail=f"Model {model_type} not found")
    
    # TODO: Queue retraining job
    # TODO: Use feature store data
    
    logger.info(f"Retraining initiated for {model_type}")
    
    return {
        "success": True,
        "model": model_type,
        "status": "queued",
        "message": f"Retraining job queued for {model_type}",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/ml/feature-store/{business_id}")
async def get_feature_store(business_id: str) -> Dict[str, Any]:
    """
    Get computed features for business
    Features include rolling averages, creative scores, seasonality, etc.
    """
    # TODO: Query feature store from database
    
    return {
        "business_id": business_id,
        "features": {
            "rolling_averages": [],
            "creative_scores": [],
            "audience_profitability_scores": [],
            "seasonality_signals": [],
            "conversion_lag_metrics": []
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
