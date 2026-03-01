import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FeatureManager:
    """
    SaaS Paywall logic mapper. Determines which modules the specific
    Tenant's current subscription has access to dynamically.
    """

    # Tiers mapped to capabilities mathematically
    TIER_FEATURES = {
        "shadow_only": {
             "max_autonomy_percent": 0.0,
             "forge_access": False,
         "hawkeye_access": False,
         "pulse_access": False,
         "calibration_access": False
        },
        "assisted_mode": {
         "max_autonomy_percent": 0.0,
         "forge_access": False,
         "hawkeye_access": True, # Gives them Solid Matter UI insights natively
         "pulse_access": False,
         "calibration_access": False
        },
        "partial_autonomy": {
         "max_autonomy_percent": 10.0, # 10% budget execution cap securely
         "forge_access": True,
         "hawkeye_access": True,
         "pulse_access": False,
         "calibration_access": False
        },
        "full_bounded_autonomy": {
         "max_autonomy_percent": 100.0,
         "forge_access": True,
         "hawkeye_access": True,
         "pulse_access": True,
         "calibration_access": True
        },
        "enterprise": {
         "max_autonomy_percent": 1000.0, # Infinite logical bound (Managed by Genesis only)
         "forge_access": True,
         "hawkeye_access": True,
         "pulse_access": True,
         "calibration_access": True,
         "custom_models": True
        }
    }

    def evaluate_access(self, company_id: str, plan_tier: str, feature_flag: str) -> bool:
        """Determines if API gateway bounces a tenant trying to hit a restricted OS component."""
        
        tier = plan_tier.lower()
        if tier not in self.TIER_FEATURES:
            logger.error(f"Tenant {company_id} mapped to invalid Subscription {tier}")
            return False
            
        return self.TIER_FEATURES[tier].get(feature_flag, False)

    def get_max_autonomy_cap(self, plan_tier: str) -> float:
        tier = plan_tier.lower()
        if tier not in self.TIER_FEATURES:
            return 0.0
        return self.TIER_FEATURES[tier].get("max_autonomy_percent", 0.0)
