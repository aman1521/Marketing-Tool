"""
Main Application Entry Point (AI Marketing OS)
==============================================
Boots the FastAPI application, initializes the Data Layer, and binds the
intelligence routers for external consumption.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Config
from backend.config import settings
from backend.database import Base, engine

# API Routers
from backend.api.intelligence import router as intelligence_router
# from backend.api.auth import router as auth_router
# from backend.api.companies import router as company_router

# Core Database Generation - Replace with Alembic migrations for Production
logger = logging.getLogger("marketing_os")
logger.setLevel(logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Allow dashboard react layer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB Generation
@app.on_event("startup")
def on_startup():
    logger.info("Initializing Marketing OS Database Schemas...")
    # Bind all declarative models to physical SQL schemas
    # This automatically instantiates Users, Companies, Connectors, AI_Logs in SQLite/Postgres.
    from backend.models import user_models, company_models, connector_models, campaign_models, intelligence_models, subscription_models
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas generated successfully.")

# Route Injections
app.include_router(intelligence_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_modules": [
            "Market Signals",
            "Competitor Intelligence", 
            "Operator Memory",
            "Marketing Knowledge Engine",
            "Creative Intelligence Engine",
            "Strategy Council",
            "Digital Twin Simulation",
            "Execution Engines (Hawkeye/Forge)"
        ]
    }
