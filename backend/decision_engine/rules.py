import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class DeterministicRulesEngine:
    """
    Evaluates hard-coded, deterministic business logic for campaigns.
    """
    
    def __init__(self):
        # Weights for Platform Fit Score
        self.fit_weights = {
            "roas": 0.40,
            "engagement": 0.20,
            "volume": 0.20,
            "growth": 0.20
        }
        
    def calculate_platform_fit_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculates a score (0-100) on how well a platform fits current business metrics.
        metrics needs:
        - normalized_roas_score (0-100)
        - normalized_engagement_score (0-100)
        - normalized_volume_score (0-100)
        - normalized_growth_score (0-100)
        """
        roas = metrics.get('normalized_roas_score', 0)
        engagement = metrics.get('normalized_engagement_score', 0)
        volume = metrics.get('normalized_volume_score', 0)
        growth = metrics.get('normalized_growth_score', 0)
        
        score = (
            (roas * self.fit_weights["roas"]) +
            (engagement * self.fit_weights["engagement"]) +
            (volume * self.fit_weights["volume"]) +
            (growth * self.fit_weights["growth"])
        )
        return round(score, 2)
        
    def evaluate_budget_scaling(self, roas: float, target_roas: float, spend_velocity: float) -> Tuple[str, float]:
        """
        Determines what to do with the budget.
        Returns (action_type, scaling_factor)
        """
        # If ROAS is significantly higher than target (e.g., > 1.2x target)
        if roas >= target_roas * 1.2:
            if spend_velocity < 0.9: # Not spending fast enough
                return "scale_up_aggressively", 1.25 # +25%
            return "scale_up", 1.15 # +15%
            
        # If ROAS is meeting target safely
        elif roas >= target_roas:
            return "maintain_or_scale", 1.05 # +5%
            
        # If ROAS is slightly under
        elif roas >= target_roas * 0.8:
            return "hold", 1.0
            
        # If ROAS is failing
        else:
            return "scale_down", 0.8 # -20%

    def evaluate_creative_replacement(self, creative_score: float, frequency: float, days_active: int) -> Tuple[bool, str]:
        """
        Decides if a creative needs to be replaced immediately.
        """
        # Ad fatigue check
        if frequency > 4.0 and days_active > 14:
            return True, "Fatigue threshold reached (High Frequency + Maturity)"
            
        # Underperforming logic
        if creative_score < 40 and days_active >= 7:
            return True, "Underperforming creative score after learning phase"
            
        return False, "Creative parameters within bounds"
        
    def apply_risk_validation(self, budget_change: float, max_daily_budget: float) -> float:
        """
        Ensure budget scaling doesn't violate hard business constraints.
        Returns the accepted budget change amount.
        """
        if budget_change > max_daily_budget:
            logger.warning(f"Risk Validator caught budget increase {budget_change} exceeding max {max_daily_budget}. Capping.")
            return max_daily_budget
        return budget_change
