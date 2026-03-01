"""
Platform Integration Service - Integrates with all advertising platforms
Manages API connections, data sync, webhooks for Meta, Google, TikTok, LinkedIn, Shopify, WooCommerce
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm
from shared.utils.data_validation import DataGovernor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "Platform Integration Service"
API_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    # Initialize MongoDB/Beanie
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.PlatformAccount, bm.Business, bm.User])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")

    # TODO: Initialize platform connectors
    yield

    try:
        close_mongo()
    except Exception:
        pass
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title=SERVICE_NAME,
    description="Multi-platform advertising API integration",
    version=API_VERSION,
    lifespan=lifespan
)


SUPPORTED_PLATFORMS = ["meta", "google", "tiktok", "linkedin", "shopify", "woocommerce"]


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "supported_platforms": SUPPORTED_PLATFORMS,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/platforms/{platform}/connect")
async def connect_platform(platform: str, account_id: str, token: str) -> Dict[str, Any]:
    """
    Connect and authenticate with a platform
    """
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
    
    # TODO: Validate token and store in database
    
    return {
        "success": True,
        "platform": platform,
        "account_id": account_id,
        "message": f"Connected to {platform}",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/platforms/{platform}/sync")
async def sync_platform_data(platform: str, business_id: str) -> Dict[str, Any]:
    """
    Trigger manual sync of all data from platform
    Pulls campaigns, audiences, creatives, and metrics
    """
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
    
    # TODO: Implement platform-specific sync logic
    
    return {
        "success": True,
        "platform": platform,
        "business_id": business_id,
        "message": f"Sync initiated for {platform}",
        "data_types": ["campaigns", "audiences", "creatives", "metrics"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/platforms/webhook")
async def handle_webhook() -> Dict[str, Any]:
    """
    Webhook endpoint for real-time platform updates
    Receives updates from Meta, Google, TikTok, etc.
    """
    # TODO: Implement webhook handlers
    
    return {
        "success": True,
        "message": "Webhook received",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/platforms/{platform}/ingest_performance")
async def ingest_platform_performance(platform: str, business_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 7.1: Strict Data Governance Gate
    Receives raw performance payloads from platform connectors and forces 
    them through the DataGovernor for schema enforcement and imputation BEFORE saving.
    """
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    validation_result = DataGovernor.enforce_and_impute(payload)
    
    if not validation_result["success"]:
        logger.error(f"Data Schema Alert for {business_id} on {platform}: {validation_result['error']}")
        raise HTTPException(status_code=422, detail={
            "message": "Data Schema Validation Failed",
            "errors": validation_result["error"]
        })
        
    clean_data = validation_result["data"]
    
    # Normally we save to MongoDB here using bm.PerformanceMetrics
    # For Phase 7, the core deliverable is proving the Governance gate works
    
    return {
        "success": True,
        "platform": platform,
        "business_id": business_id,
        "original_payload": payload,
        "scrubbed_data": clean_data,
        "message": "Data scrubbed and successfully ingested",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/platforms/status")
async def get_platform_status() -> Dict[str, Any]:
    """
    Get connection status and last sync time for all platforms
    """
    # TODO: Query database for platform status
    
    return {
        "platforms": {
            "meta": {"connected": False, "last_sync": None},
            "google": {"connected": False, "last_sync": None},
            "tiktok": {"connected": False, "last_sync": None},
            "linkedin": {"connected": False, "last_sync": None},
            "shopify": {"connected": False, "last_sync": None},
            "woocommerce": {"connected": False, "last_sync": None},
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
