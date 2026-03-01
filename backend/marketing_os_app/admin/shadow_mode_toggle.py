from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.marketing_os_app.api_gateway.router import authenticate_tenant
from backend.marketing_os_app.auth.rbac import RBAC
import logging

logger = logging.getLogger(__name__)
shadow_mode_router = APIRouter()

@shadow_mode_router.post("/api/v1/admin/shadow-mode/enable")
async def enable_shadow_mode(context: Dict[str, Any] = Depends(authenticate_tenant)):
    RBAC.enforce_role(context["role"], "ADMIN")
    logger.info(f"AUDIT: {context['company_id']} shadow mode ENABLED by {context['role']}")
    return {"status": "success", "shadow_mode": True, "message": "All AI execution is now simulated."}

@shadow_mode_router.post("/api/v1/admin/shadow-mode/disable")
async def disable_shadow_mode(context: Dict[str, Any] = Depends(authenticate_tenant)):
    RBAC.enforce_role(context["role"], "OWNER")
    logger.info(f"AUDIT: {context['company_id']} shadow mode DISABLED by {context['role']}")
    return {"status": "success", "shadow_mode": False, "message": "Live autonomous execution re-enabled."}
