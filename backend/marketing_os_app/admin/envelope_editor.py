import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from backend.marketing_os_app.api_gateway.router import authenticate_tenant
from backend.marketing_os_app.auth.rbac import RBAC
from backend.marketing_os_app.collaboration.role_matrix import can_role_perform

logger = logging.getLogger(__name__)

envelope_editor_router = APIRouter()

@envelope_editor_router.put("/api/v1/admin/envelope/budget")
async def update_budget_envelope(
    monthly_budget_cap: float,
    daily_change_limit_percent: float,
    max_portfolio_exposure: float,
    context: Dict[str, Any] = Depends(authenticate_tenant)
):
    """Finance and Owner only can update budget bounds."""
    role = context["role"]
    cid = context["company_id"]
    
    if not can_role_perform(role, "can_modify_envelope"):
        raise HTTPException(status_code=403, detail="Role not permitted to modify envelope.")

    RBAC.enforce_role(role, "FINANCE")
    logger.info(f"AUDIT TRAIL: {cid} - {role} updated budget envelope.")
    
    # In production: persists to BudgetEnvelopeModel via DB
    return {
        "status": "success",
        "updated": {
            "monthly_budget_cap": monthly_budget_cap,
            "daily_change_limit_percent": daily_change_limit_percent,
            "max_portfolio_exposure": max_portfolio_exposure
        }
    }

@envelope_editor_router.put("/api/v1/admin/envelope/strategy")
async def update_strategy_envelope(
    allowed_strategy_types: list,
    max_risk_score: float,
    context: Dict[str, Any] = Depends(authenticate_tenant)
):
    """Owner and CMO only."""
    role = context["role"]
    cid = context["company_id"]
    
    if not can_role_perform(role, "can_modify_envelope"):
        raise HTTPException(status_code=403, detail="Role not permitted to modify envelope.")

    logger.info(f"AUDIT TRAIL: {cid} - {role} updated strategy envelope.")
    return {
        "status": "success",
        "updated": {
            "allowed_strategy_types": allowed_strategy_types,
            "max_risk_score": max_risk_score
        }
    }
