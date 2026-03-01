import logging
from typing import List
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RBAC:
    """
    Hard-stops external UI requests from modifying Genesis bounds unless
    they possess explicit SaaS Owner/Admin permissions.
    """
    
    ROLE_HIERARCHY = {
        "OWNER": 4,
        "ADMIN": 3,
        "ANALYST": 2,
        "VIEWER": 1
    }

    @staticmethod
    def enforce_role(user_role: str, required_role: str):
        user_level = RBAC.ROLE_HIERARCHY.get(user_role.upper(), 0)
        req_level = RBAC.ROLE_HIERARCHY.get(required_role.upper(), 99)

        if user_level < req_level:
            logger.error(f"RBAC Violation: User ({user_role}) attempted to access ({required_role}) endpoint.")
            raise HTTPException(status_code=403, detail="Insufficient execution permissions for this tenant.")
            
    @staticmethod
    def can_approve_calibration(user_role: str) -> bool:
        """Only Admins/Owners can mutate Governance mappings externally."""
        return RBAC.ROLE_HIERARCHY.get(user_role.upper(), 0) >= 3

    @staticmethod
    def can_toggle_shadow_mode(user_role: str) -> bool:
        return RBAC.ROLE_HIERARCHY.get(user_role.upper(), 0) >= 3
