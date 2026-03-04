"""
Captain Receiver (Hawkeye)
==========================
Execution Tier Interface. Receives defensive `RecommendedAction` payloads 
from CaptainStrategy (via ExecutionRouter) and executes them within Hawkeye's domain.
"""

import logging
from typing import Dict, Any, Optional

from .hawkeye_engine import HawkeyeEngine

logger = logging.getLogger(__name__)


class HawkeyeExecutionHandler:
    """
    Acts as the API boundary between CaptainStrategy and Hawkeye Engine.
    Handles defensive actions like Pausing campaigns or penalising fatigued creatives.
    """

    def __init__(self, engine: Optional[HawkeyeEngine] = None):
        self.engine = engine

    def enforce_pause(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a PAUSE_CAMPAIGN action.
        """
        source      = payload.get("source_strategy")
        criteria    = payload.get("criteria", "worst_performers")
        count       = payload.get("count", 1)
        rationale   = payload.get("rationale", "No rationale provided.")

        logger.warning(
            f"[HawkeyeReceiver] Enforcing strict PAUSE on {count} {criteria} campaign(s). "
            f"Strategy ID: {source}. Rationale: {rationale}"
        )

        # In production this queries the Hawkeye DB for active fatigue tracking
        # and issues a connector POST to Meta/Google to actually pause it.
        # Here we mock the result set.
        
        return {
            "status": "executed",
            "action": "pause_campaign",
            "campaigns_paused": count,
            "target_criteria": criteria,
            "system_rationale": rationale
        }

    def apply_penalty(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a REDUCE_BUDGET / Penalise fatigued creative logic.
        """
        source       = payload.get("source_strategy")
        target       = payload.get("target", "fatigued_creatives")
        decrease_pct = payload.get("decrease_pct", 15)

        logger.info(
            f"[HawkeyeReceiver] Applying {decrease_pct}% penalty to {target}. "
            f"Strategy ID: {source}."
        )

        # In production, Hawkeye marks specific creatives in its Registry as "Penalty Applied"
        # and triggers the connector layers to shrink ad-set daily budgets.

        return {
            "status": "executed",
            "action": "apply_penalty",
            "target_cluster": target,
            "penalty_applied": f"-{decrease_pct}%",
            "tracked": True
        }
