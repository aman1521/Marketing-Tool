import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.marketing_os_app.ecosystem_models import PortfolioRiskModel

logger = logging.getLogger(__name__)

class PortfolioRiskTracker:
    """
    Computes and stores portfolio-level risk per company.
    Exposed only to Executive View and Owner role.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def compute_risk(self, active_campaigns: list, total_budget: float,
                      autonomy_pct: float, volatility_index: float) -> Dict[str, Any]:
        """
        Deterministic portfolio risk calculation.
        active_campaigns: list of dicts with {budget_allocated, roas, risk_score}
        """
        total_at_risk = 0.0
        exposure_stack = 0.0

        for c in active_campaigns:
            b = c.get("budget_allocated", 0.0)
            risk = c.get("risk_score", 0.3)
            total_at_risk += b * risk
            exposure_stack += b

        cross_exposure = exposure_stack / max(1.0, total_budget)
        vol_adjusted_risk = (total_at_risk / max(1.0, total_budget)) * (1.0 + volatility_index)
        worst_case = total_at_risk * 1.5  # 1.5x stress multiplier

        return {
            "total_capital_at_risk": round(total_at_risk, 2),
            "cross_campaign_exposure": round(cross_exposure, 4),
            "volatility_adjusted_risk_index": round(vol_adjusted_risk, 4),
            "autonomy_exposure_pct": round(autonomy_pct, 2),
            "worst_case_downside": round(worst_case, 2)
        }

    async def save_snapshot(self, company_id: str, risk_data: Dict[str, Any]):
        snap = PortfolioRiskModel(
            company_id=company_id,
            **risk_data
        )
        self.db.add(snap)
        await self.db.commit()
        logger.info(f"Portfolio risk snapshot saved for {company_id}")

    async def get_latest(self, company_id: str) -> Dict[str, Any]:
        q = (
            select(PortfolioRiskModel)
            .where(PortfolioRiskModel.company_id == company_id)
            .order_by(PortfolioRiskModel.computed_at.desc())
            .limit(1)
        )
        res = await self.db.execute(q)
        row = res.scalar_one_or_none()
        if not row:
            return {}
        return {
            "total_capital_at_risk": row.total_capital_at_risk,
            "cross_campaign_exposure": row.cross_campaign_exposure,
            "volatility_adjusted_risk_index": row.volatility_adjusted_risk_index,
            "autonomy_exposure_pct": row.autonomy_exposure_pct,
            "worst_case_downside": row.worst_case_downside,
            "computed_at": row.computed_at.isoformat()
        }
