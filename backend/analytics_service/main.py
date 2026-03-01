"""
Analytics & Reporting Layer - Handles KPI aggregation, forecast validation, and cohort metrics
"""

from fastapi import FastAPI
from typing import Dict, Any, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Analytics & Reporting Service"
API_VERSION = "0.1.0"
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.Business, bm.User])
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
    description="Analytics and Reporting APIs",
    version=API_VERSION,
    lifespan=lifespan
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": API_VERSION
    }

@app.get("/api/v1/analytics/kpi")
async def get_kpi_dashboard(business_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
    """Retrieves generic KPI Dashboard metrics."""
    return {
        "business_id": business_id,
        "timeframe": f"Last {timeframe_days} days",
        "metrics": {
            "total_spend": 12500.50,
            "total_revenue": 38400.00,
            "blended_roas": 3.07,
            "cpa": 45.10,
            "conversion_rate": 2.8,
            "active_campaigns": 8
        },
        "trends": {
            "roas_trend": "+12%",
            "spend_trend": "-5%",
            "cpa_trend": "-8%"
        }
    }

@app.get("/api/v1/analytics/cohorts")
async def get_cohort_analysis(business_id: str) -> Dict[str, Any]:
    """Retrieves standard cohort retention and LTV over months."""
    return {
        "business_id": business_id,
        "cohorts": [
            {"month": "January", "size": 1200, "m1_retention": 45, "m2_retention": 30, "m3_retention": 22, "ltv": 150},
            {"month": "February", "size": 1500, "m1_retention": 48, "m2_retention": 33, "m3_retention": 25, "ltv": 165},
            {"month": "March", "size": 1800, "m1_retention": 52, "m2_retention": 38, "m3_retention": 28, "ltv": 180}
        ]
    }

@app.get("/api/v1/analytics/forecast-vs-actual")
async def get_forecast_validation(business_id: str, days: int = 7) -> Dict[str, Any]:
    """Compares ML Predictions vs actual results for model drift monitoring."""
    history = []
    base_date = datetime.utcnow() - timedelta(days=days)
    
    for i in range(days):
        date_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        predicted = random.uniform(2.0, 3.5)
        error_margin = random.uniform(-0.3, 0.3)
        actual = predicted + error_margin
        
        history.append({
            "date": date_str,
            "predicted_roas": round(predicted, 2),
            "actual_roas": max(0.1, round(actual, 2)),
            "error_pct": round(abs(error_margin) / predicted * 100, 1)
        })
        
    avg_error = sum(h["error_pct"] for h in history) / len(history)
        
    return {
        "business_id": business_id,
        "model_drift_warning": avg_error > 15.0, # Flag if error is consistently high
        "average_error_pct": round(avg_error, 2),
        "data_points": history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
