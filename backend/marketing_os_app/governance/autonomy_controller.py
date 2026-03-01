import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.marketing_os_app.advanced_models import AutonomyControlRecord

logger = logging.getLogger(__name__)

# Adaptive rules configuration
RULES = {
    "drift_spike_threshold":      0.3,    # >30% drift frequency triggers reduction
    "rollback_rate_threshold":    0.08,   # >8% rollback triggers conservative mode
    "volatility_high_threshold":  0.6,
    "confidence_stable_days":     14,
    "confidence_stable_threshold": 0.85,

    "reduction_step_pct":   5.0,   # Reduce by 5% per trigger
    "increase_step_pct":    2.0,   # Gradual 2% expansion per stable cycle
    "conservative_cap_pct": 5.0,   # Max autonomy in conservative mode
    "absolute_min_pct":     0.0,
    "absolute_max_pct":     100.0
}


class AutonomyController:
    """
    Adaptive Autonomy Throttling:
    AI autonomy % adjusts automatically based on system performance signals.
    Higher drift/rollbacks → squeeze autonomy.
    Stable confidence → expand autonomy gradually.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def evaluate(self, current_pct: float, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        metrics keys:
            drift_frequency        — float 0–1
            volatility_index       — float 0–1
            rollback_rate          — float 0–1
            portfolio_exposure_pct — float
            confidence_avg         — float 0–1
            stable_days            — int
            escalation_frequency   — float 0–1
        """
        new_pct = current_pct
        triggers = []

        # Rule 1: Drift spike
        if metrics.get("drift_frequency", 0) > RULES["drift_spike_threshold"]:
            new_pct -= RULES["reduction_step_pct"]
            triggers.append("DRIFT_SPIKE")

        # Rule 2: High volatility → tighten
        if metrics.get("volatility_index", 0) > RULES["volatility_high_threshold"]:
            new_pct -= RULES["reduction_step_pct"]
            triggers.append("HIGH_VOLATILITY")

        # Rule 3: Rollback rate exceeded → conservative mode
        if metrics.get("rollback_rate", 0) > RULES["rollback_rate_threshold"]:
            new_pct = min(new_pct, RULES["conservative_cap_pct"])
            triggers.append("ROLLBACK_RATE_EXCEEDED → CONSERVATIVE_MODE")

        # Rule 4: Stable confidence → gradual expansion
        stable_days = metrics.get("stable_days", 0)
        conf = metrics.get("confidence_avg", 0)
        if (stable_days >= RULES["confidence_stable_days"] and
                conf >= RULES["confidence_stable_threshold"] and
                not triggers):
            new_pct += RULES["increase_step_pct"]
            triggers.append("CONFIDENCE_STABLE → EXPANSION")

        # Rule 5: Escalation frequency pressure
        if metrics.get("escalation_frequency", 0) > 0.2:
            new_pct -= RULES["reduction_step_pct"] / 2
            triggers.append("ESCALATION_PRESSURE")

        # Bounds enforcement
        new_pct = round(max(RULES["absolute_min_pct"], min(RULES["absolute_max_pct"], new_pct)), 2)

        return {
            "previous_pct": current_pct,
            "new_pct": new_pct,
            "delta": round(new_pct - current_pct, 2),
            "triggers": triggers,
            "mode": "conservative" if new_pct <= RULES["conservative_cap_pct"] else "standard"
        }

    async def apply_and_record(self, company_id: str, current_pct: float,
                                metrics: Dict[str, Any]) -> Dict[str, Any]:
        result = self.evaluate(current_pct, metrics)

        if result["delta"] != 0:
            record = AutonomyControlRecord(
                company_id=company_id,
                previous_pct=result["previous_pct"],
                new_pct=result["new_pct"],
                trigger=", ".join(result["triggers"]),
                context=metrics
            )
            self.db.add(record)
            await self.db.commit()
            logger.info(f"AUTONOMY [{company_id}] {current_pct}% → {result['new_pct']}% ({result['triggers']})")

        return result
