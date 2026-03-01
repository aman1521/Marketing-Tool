import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends

from backend.marketing_os_app.api_gateway.router import authenticate_tenant
from backend.marketing_os_app.dashboards.translation_layer import TranslationLayer
from backend.marketing_os_app.auth.rbac import RBAC

logger = logging.getLogger(__name__)

simple_view_router = APIRouter()
pro_view_router = APIRouter()
exec_view_router = APIRouter()

translator = TranslationLayer()

# ──────────────────────────────────────────────
# SIMPLE VIEW — Layman / Business Owner basics
# ──────────────────────────────────────────────

@simple_view_router.get("/api/v1/dashboard/simple")
async def simple_dashboard(context: Dict[str, Any] = Depends(authenticate_tenant)):
    """Available to all roles. Plain English only."""
    mock_signals = {
        "executions_count": 8, "rollback_count": 0,
        "system_risk_exposure_score": 0.22,
        "drift_incidents": 0, "pending_tasks_summary": "Nothing urgent.",
        "estimated_lift_usd": "$340"
    }
    return translator.translate(mock_signals, mode="simple")

# ──────────────────────────────────────────────
# PRO VIEW — Media Buyer / Analyst / CMO
# ──────────────────────────────────────────────

@pro_view_router.get("/api/v1/dashboard/pro")
async def pro_dashboard(context: Dict[str, Any] = Depends(authenticate_tenant)):
    """Restricted to ANALYST and above."""
    RBAC.enforce_role(context["role"], "ANALYST")
    mock_signals = {
        "executions_count": 8, "rollback_count": 1,
        "drift_incidents": 1, "fatigued_creatives": 3,
        "active_experiments": 5, "top_hook_strength": "Strong",
        "autonomy_stability_index": 0.91, "system_risk_exposure_score": 0.28,
        "confidence_average": 0.76, "pending_escalations": 0,
        "pending_calibration_suggestions": 1
    }
    return translator.translate(mock_signals, mode="pro")

# ──────────────────────────────────────────────
# EXECUTIVE VIEW — Owner / Finance / CMO
# ──────────────────────────────────────────────

@exec_view_router.get("/api/v1/dashboard/executive")
async def executive_dashboard(context: Dict[str, Any] = Depends(authenticate_tenant)):
    """Restricted to CMO and above. Exposes capital at risk."""
    RBAC.enforce_role(context["role"], "CMO")
    mock_signals = {
        "total_capital_at_risk": 4200.0,
        "worst_case_downside": 6300.0,
        "roi_delta_pct": "+14.2%",
        "autonomy_exposure_pct": 8.5,
        "executions_count": 42,
        "pending_escalations": 1,
        "system_risk_exposure_score": 0.31
    }
    return translator.translate(mock_signals, mode="executive")
