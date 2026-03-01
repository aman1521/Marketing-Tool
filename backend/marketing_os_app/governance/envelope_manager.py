import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from backend.marketing_os_app.ecosystem_models import BudgetEnvelopeModel, StrategyEnvelopeModel

logger = logging.getLogger(__name__)

class EnvelopeManager:
    """
    Loads and validates the active Budget + Strategy Envelope for a company.
    AI execution passes through this before dispatch.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_budget_envelope(self, company_id: str) -> BudgetEnvelopeModel:
        q = select(BudgetEnvelopeModel).where(BudgetEnvelopeModel.company_id == company_id)
        res = await self.db.execute(q)
        env = res.scalar_one_or_none()
        if not env:
            raise HTTPException(status_code=404, detail=f"No budget envelope configured for {company_id}")
        return env

    async def get_strategy_envelope(self, company_id: str) -> StrategyEnvelopeModel:
        q = select(StrategyEnvelopeModel).where(StrategyEnvelopeModel.company_id == company_id)
        res = await self.db.execute(q)
        env = res.scalar_one_or_none()
        if not env:
            raise HTTPException(status_code=404, detail=f"No strategy envelope configured for {company_id}")
        return env

    async def check_action_within_envelope(self, company_id: str,
                                            action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core gate. Returns dict with 'within_envelope' bool and 'breach_type' if violated.
        AI must pass this before any execution.
        """
        budget_env = await self.get_budget_envelope(company_id)
        strategy_env = await self.get_strategy_envelope(company_id)

        action_type     = action.get("action_type", "")
        budget_delta    = action.get("budget_delta_usd", 0.0)
        change_pct      = action.get("budget_change_percent", 0.0)
        risk_score      = action.get("risk_score", 0.0)
        platform        = action.get("platform", "")

        # 1. Daily change limit
        if change_pct > budget_env.daily_change_limit_percent:
            return {"within_envelope": False, "breach_type": "BUDGET_BREACH",
                    "detail": f"Change {change_pct}% > daily limit {budget_env.daily_change_limit_percent}%"}

        # 2. Strategy type allowed
        if action_type and strategy_env.allowed_strategy_types:
            if action_type not in strategy_env.allowed_strategy_types:
                return {"within_envelope": False, "breach_type": "STRATEGY_BREACH",
                        "detail": f"Action type {action_type} not in allowed list"}

        # 3. Platform allowed
        if platform and strategy_env.allowed_platforms:
            if platform not in strategy_env.allowed_platforms:
                return {"within_envelope": False, "breach_type": "STRATEGY_BREACH",
                        "detail": f"Platform {platform} not permitted"}

        # 4. Risk score cap
        if risk_score > strategy_env.max_risk_score:
            return {"within_envelope": False, "breach_type": "STRATEGY_BREACH",
                    "detail": f"Risk score {risk_score} > envelope max {strategy_env.max_risk_score}"}

        # ✅ Within envelope
        return {"within_envelope": True, "breach_type": None, "detail": "Cleared"}
