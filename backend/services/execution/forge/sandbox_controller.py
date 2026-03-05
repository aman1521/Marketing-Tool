import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SandboxController:
    """
    Enforces strict isolation and financial bounds for autonomous campaigns.
    Ensures that bad experiments cannot bleed budget into primary channels.
    """

    def check_sandbox_safe(self, proposed_budget: float, core_budget: float, genesis_constraints: Dict[str, Any]) -> bool:
        """
        Validates if the requested allocation aligns with strict Genesis caps.
        """
        if not genesis_constraints.get("creative_sandbox_required", True):
             # Highly unusual, but allowed if Genesis Governance disabled sandboxing globally
             logger.warning("Sandbox requirements bypassed globally by Genesis Governance.")
             return True
             
        # Check against pure execution rules
        max_daily_budget = genesis_constraints.get("max_daily_budget", 0)
        
        if (core_budget + proposed_budget) > max_daily_budget:
            logger.warning(f"Sandbox rejected: Total proposed ({core_budget + proposed_budget}) > Max Allowed ({max_daily_budget})")
            return False
            
        return True

    def calculate_isolation_parameters(self, campaign_id: str, variation_id: str) -> Dict[str, Any]:
        """
        Generates strict target exclusions bridging the core campaign away 
        from the sandbox test to prevent audience overlap/bidding against oneself.
        """
        return {
             "parent_campaign_exclusion": campaign_id,
             "naming_convention": f"[FORGE-SANDBOX] {campaign_id} - {variation_id}",
             "bidding_isolation_mode": "cost_cap_strict"
        }
