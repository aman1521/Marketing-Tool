import logging
from typing import Dict, Any

from backend.services.genesis.schemas import GenesisProfileSchema

logger = logging.getLogger(__name__)

class GenesisProfileManager:
    """
    Manages structured business identity rules.
    """
    def validate_profile(self, payload: Dict[str, Any]) -> GenesisProfileSchema:
        """
        Ensures strict type-checking and logical constraints.
        Raises ValueError if structural data is corrupted or unsupported.
        """
        try:
            profile = GenesisProfileSchema(**payload)
            logger.debug(f"Profile validated successfully for industry: {profile.industry}")
            return profile
        except Exception as e:
            logger.error(f"Profile validation failed: {str(e)}")
            raise ValueError(f"Invalid profile configuration: {str(e)}")
