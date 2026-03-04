"""
Execution Router
================
Acts as the bridge between CaptainStrategy (Decision Layer) and 
the Execution Tier (Hawkeye & Forge).

Routes generated `RecommendedAction` objects to their respective 
domain engines for actual implementation in ad networks.
"""

import logging
from typing import Dict, Any, List

from .models import ActionType, RecommendedAction

logger = logging.getLogger(__name__)


class ExecutionRouter:
    """
    Translates abstract strategic actions into domain-specific execution payloads
    for Hawkeye (Analytics/Defensive) and Forge (Offensive/Scale/Tests).
    """

    def __init__(self, forge_client=None, hawkeye_client=None):
        # In a real microservice arch these might be HTTP / gRPC clients.
        # For our monolithic structure, they might be instances of the domain managers.
        self.forge = forge_client
        self.hawkeye = hawkeye_client

    def route_strategy(self, strategy_id: str, actions: List[RecommendedAction]) -> Dict[str, Any]:
        """
        Process a list of actions and route them to the relevant execution engines.
        """
        logger.info(f"[ExecutionRouter] Routing {len(actions)} actions for Strategy [{strategy_id}]")
        
        results = {
            "forge_actions": 0,
            "hawkeye_actions": 0,
            "failed_routes": 0,
            "dispatched": []
        }

        for action in actions:
            try:
                if action.action_type in (
                    ActionType.SCALE_BUDGET, 
                    ActionType.NEW_CREATIVE_ANGLE, 
                    ActionType.AUDIENCE_EXPANSION,
                    ActionType.PLATFORM_SHIFT,
                    ActionType.OFFER_CHANGE
                ):
                    self._route_to_forge(action)
                    results["forge_actions"] += 1
                    
                elif action.action_type in (
                    ActionType.REDUCE_BUDGET,
                    ActionType.PAUSE_CAMPAIGN,
                    ActionType.BID_ADJUSTMENT
                ):
                    self._route_to_hawkeye(action)
                    results["hawkeye_actions"] += 1
                    
                else:
                    logger.warning(f"Unknown action type: {action.action_type}")
                    results["failed_routes"] += 1
                    continue
                
                results["dispatched"].append(action.id)
                
            except Exception as e:
                logger.error(f"[ExecutionRouter] Failed to route action {action.id}: {str(e)}")
                results["failed_routes"] += 1

        return results

    def _route_to_forge(self, action: RecommendedAction):
        """
        Route aggressive/testing/scaling moves to Forge (Experimentation Engine)
        """
        payload = action.payload or {}
        
        if self.forge is None:
            logger.debug(f"[Forge-Mock] Received {action.action_type} - Payload: {payload}")
            return

        if action.action_type == ActionType.NEW_CREATIVE_ANGLE:
            # Tell Forge to spin up A/B tests against new archetypes
            archetypes = payload.get("archetypes_to_test", [])
            self.forge.create_experiment({
                "source_strategy": action.strategy_id,
                "type": "creative_angle_test",
                "archetypes": archetypes,
                "budget_allocation": payload.get("budget_allocation", "10%")
            })

        elif action.action_type == ActionType.SCALE_BUDGET:
            # Tell Forge to increase budget on winners
            self.forge.apply_scale({
                "source_strategy": action.strategy_id,
                "target_entity": action.target_entity_id,
                "scale_pct": payload.get("increase_pct", 10),
                "rationale": action.rationale
            })

    def _route_to_hawkeye(self, action: RecommendedAction):
        """
        Route defensive/tracking moves to Hawkeye (Creative Analysis/Defensive Engine).
        Hawkeye handles fatigue monitoring, pausing, and shrinking exposure.
        """
        payload = action.payload or {}
        
        if self.hawkeye is None:
            logger.debug(f"[Hawkeye-Mock] Received {action.action_type} - Payload: {payload}")
            return

        if action.action_type == ActionType.PAUSE_CAMPAIGN:
            # Tell Hawkeye/Connection manager to hard-stop a campaign
            self.hawkeye.enforce_pause({
                "source_strategy": action.strategy_id,
                "criteria": payload.get("criteria"),
                "count": payload.get("count", 1),
                "rationale": action.rationale
            })

        elif action.action_type == ActionType.REDUCE_BUDGET:
            # Tell Hawkeye to penalise fatigued creative distributions
            self.hawkeye.apply_penalty({
                "source_strategy": action.strategy_id,
                "target": payload.get("target"),
                "decrease_pct": payload.get("decrease_pct", 10)
            })
