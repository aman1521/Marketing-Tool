from typing import Dict, Any

# ──────────────────────────────────────────────
# ROLE PERMISSION MATRIX
# ──────────────────────────────────────────────

ROLE_MATRIX: Dict[str, Dict[str, Any]] = {
    "owner": {
        "can_execute": True,
        "can_modify_envelope": True,
        "can_approve_escalations": True,
        "visibility_scope": "full",
        "can_override": True,
        "can_toggle_shadow": True,
        "receive_escalations": ["BUDGET_BREACH", "PORTFOLIO_BREACH", "HIGH_VOLATILITY"]
    },
    "cmo": {
        "can_execute": False,
        "can_modify_envelope": False,           # Cannot unilaterally change limits
        "can_approve_escalations": True,
        "visibility_scope": "strategy",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": ["STRATEGY_BREACH"]
    },
    "media_buyer": {
        "can_execute": True,                    # Can action within envelope only
        "can_modify_envelope": False,
        "can_approve_escalations": False,
        "visibility_scope": "campaigns",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": []
    },
    "creative_strategist": {
        "can_execute": False,
        "can_modify_envelope": False,
        "can_approve_escalations": False,
        "visibility_scope": "creative",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": []
    },
    "analyst": {
        "can_execute": False,
        "can_modify_envelope": False,
        "can_approve_escalations": False,
        "visibility_scope": "analytics",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": []
    },
    "finance": {
        "can_execute": False,
        "can_modify_envelope": True,            # Can adjust budget bounds
        "can_approve_escalations": True,
        "visibility_scope": "budget",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": ["BUDGET_BREACH"]
    },
    "viewer": {
        "can_execute": False,
        "can_modify_envelope": False,
        "can_approve_escalations": False,
        "visibility_scope": "summary",
        "can_override": False,
        "can_toggle_shadow": False,
        "receive_escalations": []
    }
}

def get_role_permissions(role: str) -> Dict[str, Any]:
    return ROLE_MATRIX.get(role.lower(), ROLE_MATRIX["viewer"])

def can_role_perform(role: str, action: str) -> bool:
    perms = get_role_permissions(role)
    return perms.get(action, False)

def get_escalation_targets(breach_type: str) -> list:
    """Returns the list of roles that must be notified for this breach type."""
    targets = []
    for role, perms in ROLE_MATRIX.items():
        if breach_type in perms.get("receive_escalations", []):
            targets.append(role)
    return targets
