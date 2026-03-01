from enum import Enum
from typing import List, Dict, Any

class Role(str, Enum):
    BUSINESS_OWNER = "business_owner"
    AGENCY_ADMIN = "agency_admin"
    INTERNAL_OPERATOR = "internal_operator"

class Permission(str, Enum):
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    
    # Intelligence / Strategy
    VIEW_STRATEGY = "view_strategy"
    GENERATE_STRATEGY = "generate_strategy"
    
    # Execution
    APPROVE_EXECUTION = "approve_execution"
    REJECT_EXECUTION = "reject_execution"
    TOGGLE_KILL_SWITCH = "toggle_kill_switch"
    
    # Settings & Users
    MANAGE_USERS = "manage_users"
    MANAGE_BILLING = "manage_billing"

# Role to Permissions Mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.BUSINESS_OWNER: [
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_STRATEGY,
        Permission.APPROVE_EXECUTION,
        Permission.REJECT_EXECUTION,
        Permission.TOGGLE_KILL_SWITCH,
        Permission.MANAGE_USERS,
        Permission.MANAGE_BILLING
    ],
    Role.AGENCY_ADMIN: [
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_STRATEGY,
        Permission.GENERATE_STRATEGY,
        Permission.APPROVE_EXECUTION,
        Permission.REJECT_EXECUTION,
        Permission.TOGGLE_KILL_SWITCH
    ],
    Role.INTERNAL_OPERATOR: [
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_STRATEGY
    ]
}

def get_permissions_for_role(role_name: str) -> List[str]:
    """Return a list of permission strings for a given role"""
    try:
        role_enum = Role(role_name.lower())
        return [p.value for p in ROLE_PERMISSIONS.get(role_enum, [])]
    except ValueError:
        return []

def has_permission(role_name: str, required_permission: str) -> bool:
    """Check if a role has a specific permission"""
    permissions = get_permissions_for_role(role_name)
    return required_permission in permissions
