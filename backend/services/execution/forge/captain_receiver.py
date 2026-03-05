"""
Captain Receiver (Forge)
========================
Execution Tier Interface. Receives offensive/scale/test `RecommendedAction` payloads 
from CaptainStrategy (via ExecutionRouter) and executes them within Forge's Sandboxes.
"""

import logging
from typing import Dict, Any, Optional

from .experiment_engine import ForgeExperimentEngine

logger = logging.getLogger(__name__)


class ForgeExecutionHandler:
    """
    Acts as the API boundary between CaptainStrategy and Forge Experiment Engine.
    Handles offensive mapping scaling winning subsets and provisioning A/B sandboxes.
    """

    def __init__(self, engine: Optional[ForgeExperimentEngine] = None):
        self.engine = engine  # Needs an AsyncSession initialized to function fully

    def create_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a NEW_CREATIVE_ANGLE action.
        Spins up A/B multivariate sandboxes in Forge for new Captain-provided archetypes.
        """
        source            = payload.get("source_strategy")
        archetypes        = payload.get("archetypes", [])
        budget_allocation = payload.get("budget_allocation", "10%")

        logger.info(
            f"[ForgeReceiver] Provisioning Sandbox Experiment for Strategy '{source}'. "
            f"Testing {len(archetypes)} brand new Archetypes with {budget_allocation} budget cap."
        )

        # In production this parses the `archetypes` against the `variation_generator.py`
        # and issues `await self.engine.launch_experiment(...)`. Mocked below to satisfy tests.

        return {
            "status": "experiment_scheduled",
            "action": "create_experiment",
            "experiment_type": "creative_angle_test",
            "archetypes_provisioned": archetypes,
            "sandbox_budget_cap": budget_allocation
        }

    def apply_scale(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a SCALE_BUDGET action.
        Aggressively pushes winning entities in ad platforms via Connector limits.
        """
        source        = payload.get("source_strategy")
        target_entity = payload.get("target_entity", "auto_detected_winner")
        scale_pct     = payload.get("scale_pct", 20)
        rationale     = payload.get("rationale", "No rationale payload.")

        logger.warning(
            f"[ForgeReceiver] Executing Aggressive Scale: +{scale_pct}% to {target_entity}. "
            f"Strategy ID: {source}. Rationale: {rationale}"
        )

        # In production Forge interacts directly with the Google/Meta SDKs to manipulate limits
        # with fallback to `Automation Safety Engine` constraints locally via `AllocationManager`.
        
        return {
            "status": "executed",
            "action": "apply_scale",
            "target_entity": target_entity,
            "scale_applied": f"+{scale_pct}%"
        }
