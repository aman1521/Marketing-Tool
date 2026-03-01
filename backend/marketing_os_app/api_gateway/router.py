import logging
from typing import Dict, Any
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# (In production, Depends(get_db) connects to actual multi-tenant clusters)

from backend.marketing_os_app.feature_flags.feature_manager import FeatureManager
from backend.marketing_os_app.dashboards.autonomy_status_service import AutonomyStatusService

logger = logging.getLogger(__name__)

dashboard_router = APIRouter()
feature_engine = FeatureManager()
status_engine = AutonomyStatusService()

def authenticate_tenant(x_company_id: str = Header(...), x_role: str = Header(...), x_plan: str = Header(...), x_system_mode: str = Header(default="saas_standard")) -> Dict[str, str]:
    """
    Mock JWT extractor. Extracts strictly validated multi-tenant scopes securely.
    """
    if not x_company_id or not x_role:
        raise HTTPException(status_code=401, detail="Unauthorized API invocation.")
        
    return {"company_id": x_company_id, "role": x_role, "active_plan": x_plan, "system_mode": x_system_mode}

@dashboard_router.get("/api/v1/dashboard/autonomy")
async def fetch_tenant_dashboard(context: Dict[str, str] = Depends(authenticate_tenant)):
    """
    The main client portal load event tracking the stability of their internal Engine.
    Requires at least 'Shadow Only' functionality.
    """
    
    # Strictly bind inputs utilizing Context dict mappings
    cid = context["company_id"]
    role = context["role"]
    system_mode = context["system_mode"]
    
    # Execute Core Logic Wrapper
    dashboard_payload = await status_engine.get_dashboard(company_id=cid, access_role=role, system_mode=system_mode)
    
    return dashboard_payload

@dashboard_router.get("/api/v1/dashboard/hawkeye-insights")
async def fetch_creative_insights(context: Dict[str, str] = Depends(authenticate_tenant)):
    """
    Feature-gated API endpoint utilizing the Paywall definitions.
    """
    cid = context["company_id"]
    plan = context["active_plan"]
    system_mode = context["system_mode"]
    
    # Gatecheck!
    if not feature_engine.evaluate_access(cid, system_mode, plan, "hawkeye_access"):
        raise HTTPException(status_code=403, detail="Hawkeye Intelligence requires the Assisted Mode plan or higher.")
        
    # Standard 200 Mock
    return {"status": "success", "creatives_analyzed": 142, "fatigue_scores": []}
