"""
Scenario Builder
================
Takes a singular Strategy Action recommended by CaptainStrategy and generates
multiple parameterized variations (Scenarios) to test inside the simulation environment.
"""

from typing import Dict, Any, List
import uuid
import logging

from .models import Scenario

logger = logging.getLogger(__name__)

class ScenarioBuilder:
    """
    Spawns test variations for Capital allocation, Audience width, or Platform mixes.
    """

    def build_scenarios(self, strategy_id: str, action: Dict[str, Any]) -> List[Scenario]:
        """
        Produce multiple scenarios based off a base action payload.
        """
        logger.debug(f"[ScenarioBuilder] Creating matrices for {action.get('type')}")
        scenarios = []
        action_type = action.get("action_type")
        base_payload = action.get("parameters", action.get("payload", {}))

        if action_type == "SCALE_BUDGET":
            # Test different scaling thresholds looking for breakpoints
            tests = [10, 20, 30]
            for val in tests:
                scenarios.append(Scenario(
                    id=str(uuid.uuid4()),
                    strategy_reference=strategy_id,
                    action_type=action_type,
                    parameter_variations={"increase_pct": val, "target_entity": base_payload.get("target_entity", "auto")}
                ))
                
        elif action_type == "NEW_CREATIVE_ANGLE":
            # Test focused vs broad split
            archs = base_payload.get("archetypes_to_test", [])
            scenarios.append(Scenario(
                id=str(uuid.uuid4()),
                strategy_reference=strategy_id,
                action_type=action_type,
                parameter_variations={"archetype": archs[0] if archs else "none", "budget_allocation": "15%"} # Default test
            ))
            if len(archs) > 1:
                scenarios.append(Scenario(
                     id=str(uuid.uuid4()),
                     strategy_reference=strategy_id,
                     action_type=action_type,
                     parameter_variations={"archetypes": archs[:2], "budget_allocation": "25%"} # Aggressive broad test
                ))
                
        elif action_type == "PAUSE_CAMPAIGN":
            # Test hard pause vs gentle taper
            scenarios.append(Scenario(
                id=str(uuid.uuid4()), strategy_reference=strategy_id, action_type=action_type,
                parameter_variations={"method": "hard_pause", "target": base_payload.get("criteria")}
            ))
            scenarios.append(Scenario(
                id=str(uuid.uuid4()), strategy_reference=strategy_id, action_type=action_type,
                parameter_variations={"method": "taper_budget", "decrease_pct": 50, "target": base_payload.get("criteria")}
            ))
            
        else:
             # Basic 1-to-1 map if unfamiliar Action
             scenarios.append(Scenario(
                 id=str(uuid.uuid4()),
                 strategy_reference=strategy_id,
                 action_type=action_type,
                 parameter_variations=base_payload
             ))

        return scenarios
