import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import companies
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Tenant Marketing AI Autonomous Intelligence System"
)

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
from app.api import auth, companies, subscriptions, connectors, intelligence, competitor, automation

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Billing & Subs"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["Platform Connectors"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["Intelligence UI"])
app.include_router(competitor.router, prefix="/api/v1/competitor", tags=["Competitor Index"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["Safety & Overrides"])

@app.get("/health")
async def root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# Entrypoint for uvicorn inside docker
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
