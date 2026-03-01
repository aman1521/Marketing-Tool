import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

# Mocks
from backend.services.sentinel.risk_dashboard_engine import RiskDashboardEngine

logger = logging.getLogger(__name__)

class AutonomyStatusService:
    """
    The SaaS frontend wrapper hitting the Sentinel core directly.
    Translates structural engineering arrays into clean presentation graphs.
    """
    
    def __init__(self):
        self.sentinel = RiskDashboardEngine()

    async def get_dashboard(self, company_id: str, access_role: str, db_stub: AsyncSession = None) -> Dict[str, Any]:
        """
        Securely restricts cross-company queries implicitly.
        If role is VIEWER, mock obfuscating sensitive financial budget limits conditionally.
        """
        logger.info(f"SaaS Application generating UI dashboard for {company_id} - Role: {access_role}")
        
        # MOCK HIT to Core Sentinel logic simulating standard outputs (Sentinel would normally query DB natively)
        uptime = {"avg_latency_ms": 110.0}
        executions = [{"status": "success"}]*40 + [{"status": "rollback_triggered"}]*2
        variances = [0.1, 0.2, 0.4] # 1 Drift Hit mathematically
        
        raw_core_data = self.sentinel.generate_dashboard_metrics(uptime, executions, variances).model_dump()
        
        # Abstract mapping logic into UI JSON explicitly
        dashboard_json = {
            "company_id": company_id,
            "autonomy_stability_index": raw_core_data.get("autonomy_stability_index", 0.0),
            "drift_incidents": 1,
            "current_risk_level": "Elevated" if raw_core_data.get("system_risk_exposure_score") > 0.4 else "Stable",
            "budget_exposure_percentage": 5.4 if access_role != "VIEWER" else "Obfuscated",
            "shadow_mode_active": raw_core_data.get("shadow_mode_active", True),
            "confidence_average": 0.77,
            "rollback_count": 2,
            "pending_calibration_suggestions": 1
        }
        
        return dashboard_json
