import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AllocationManager:
    """
    Determines mathematically how to distribute risk capital between 
    primary exploitation streams and new explorations.
    """

    def allocate_sandbox_budget(self, total_campaign_budget: float, genesis_aggression_tier: str) -> float:
        """
        Basic MVP Algorithm: Assign fixed percentage based on Genesis Risk mapping.
        Aggressive maps larger budgets to faster validation loops.
        """
        
        # Fixed Base allocations
        base_allocation_pct = 0.05
        
        if genesis_aggression_tier == "Aggressive":
            base_allocation_pct = 0.15
        elif genesis_aggression_tier == "Moderate":
            base_allocation_pct = 0.10
            
        allocated_budget = total_campaign_budget * base_allocation_pct
        
        logger.debug(f"Forge allocated {base_allocation_pct*100}% (${allocated_budget}) of campaign budget for exploration.")
        return round(allocated_budget, 2)
        
    def calculate_bandit_weights(self, variations: Dict[str, Any]) -> Dict[str, float]:
        """
        SCAFFOLD: Placeholder for Thompson Sampling / UCB algorithms when 
        variations begin scaling over multiple days dynamically.
        """
        num_variations = len(variations)
        if num_variations == 0:
            return {}
            
        # MVP: Even split 
        split = 1.0 / num_variations
        return {var_id: split for var_id in variations.keys()}
