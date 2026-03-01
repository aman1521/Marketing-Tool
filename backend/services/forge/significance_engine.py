import logging
from typing import Dict, Any, Tuple
import math

logger = logging.getLogger(__name__)

class SignificanceEngine:
    """
    Mathematical Inference Engine proving success or failure of Forge variations.
    Rejects naive CTR differences and runs formal frequentist methods for deterministic
    outcomes mapped via conversion and click ratios.
    """

    def _z_test_proportions(self, success_a: int, trials_a: int, success_b: int, trials_b: int) -> Tuple[float, float]:
        """
        Two-sample Z-test for proportions mathematically assessing differences in Conversion rate natively.
        Returns: (Z-score, approximate P-value one-tailed)
        """
        if trials_a == 0 or trials_b == 0:
            return (0.0, 1.0)
            
        p_a = success_a / trials_a
        p_b = success_b / trials_b
        
        # Pooled proportion
        p_pool = (success_a + success_b) / (trials_a + trials_b)
        
        # Standard Error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/trials_a + 1/trials_b))
        
        if se == 0:
             return (0.0, 1.0)
             
        z_stat = (p_b - p_a) / se
        
        # Approximate P-value using standard normal bounds (ignoring precise CDF scipy requiremnts here for portability)
        # Using basic deterministic mapping approximations for structural MVP
        if z_stat > 1.645:
             p_val = 0.05
        elif z_stat > 1.96:
             p_val = 0.025
        elif z_stat > 2.576:
             p_val = 0.005
        else:
             p_val = 0.5 # Fail to reject
             
        return (z_stat, p_val)

    def evaluate_experiment(self, control_stats: Dict[str, int], variation_stats: Dict[str, int], confidence_threshold: float = 0.95) -> Dict[str, Any]:
        """
        Execute formal statistical significance matrix on live variations vs baseline control.
        """
        
        c_trials = control_stats.get("clicks", 0)     # Denominator
        c_success = control_stats.get("conversions", 0) # Numerator
        
        v_trials = variation_stats.get("clicks", 0)
        v_success = variation_stats.get("conversions", 0)
        
        # Minimum data thresholds rule logic strictly
        if c_trials < 100 or v_trials < 100:
             logger.warning("Significance Engine rejected: Insufficient trial data gathered (<100 clicks).")
             return {"significant": False, "lift_percentage": 0.0, "p_value": 1.0, "reason": "insufficient_data"}
        
        z_stat, p_value = self._z_test_proportions(c_success, c_trials, v_success, v_trials)
        
        c_cr = (c_success / c_trials) 
        v_cr = (v_success / v_trials)
        
        lift = ((v_cr - c_cr) / c_cr) * 100 if c_cr > 0 else 0.0
        
        alpha = 1.0 - confidence_threshold
        is_significant = (p_value <= alpha) and (lift > 0)
        
        logger.info(f"Forge Significance Executed. Lift: {round(lift, 2)}% | P-Val: {p_value} | Significant: {is_significant}")
        
        return {
            "significant": is_significant,
            "lift_percentage": round(lift, 2),
            "p_value": p_value,
            "confidence_level": 1.0 - p_value,
            "z_score": round(z_stat, 3)
        }
