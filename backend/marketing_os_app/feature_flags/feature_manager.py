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

    def evaluate_access(self, company_id: str, system_mode: str, plan_tier: str, feature_flag: str) -> bool:
        """Determines if API gateway bounces a tenant trying to hit a restricted OS component."""
        if system_mode.lower() == "agency_alpha":
            return True # Alpha gets full access natively
            
        tier = plan_tier.lower()
        if tier not in self.TIER_FEATURES:
            logger.error(f"Tenant {company_id} mapped to invalid Subscription {tier}")
            return False
            
        return self.TIER_FEATURES[tier].get(feature_flag, False)

    def get_max_autonomy_cap(self, system_mode: str, plan_tier: str) -> float:
        if system_mode.lower() == "agency_alpha":
            return 10000.0 # Unlimited logical bounds
            
        tier = plan_tier.lower()
        if tier not in self.TIER_FEATURES:
            return 0.0
        return self.TIER_FEATURES[tier].get("max_autonomy_percent", 0.0)

    def get_exposure_level(self, system_mode: str) -> str:
        """Determines how much raw structure is returned via APIs."""
        if system_mode.lower() == "agency_alpha":
            return "RAW_SIGNALS"
        elif system_mode.lower() == "enterprise_api":
            return "STRUCTURED_FIREHOSE"
        return "CLEAN_DASHBOARD"

    def can_approve_calibration(self, system_mode: str, user_role: str) -> bool:
        """Determines if the tenant UI allows them to push parameter changes to Genesis."""
        if system_mode.lower() == "agency_alpha":
            return True  # Internal operators always have authority
        elif system_mode.lower() == "enterprise_api":
            return user_role in ["OWNER", "ADMIN"]
        # SAAS standard lacks calibration mutation rights initially
        return False
