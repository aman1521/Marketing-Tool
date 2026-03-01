import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from backend.marketing_os_app.advanced_models import EscalationState

logger = logging.getLogger(__name__)

# Role priority for conflict resolution (higher = more authority)
ROLE_PRIORITY = {
    "owner":   100,
    "finance": 70,
    "cmo":     60,
    "media_buyer": 30,
    "analyst": 20,
    "viewer":  0
}

# SLA deadline before EXPIRED state (hours)
ESCALATION_SLA_HOURS = 4


class EscalationStateMachine:
    """
    Deterministic resolution engine for escalation conflicts.
    Handles conflicting approvals, envelope mutations mid-escalation,
    risk spikes, timeouts, and emergency overrides.
    """

    def __init__(self):
        self._state_log: List[Dict[str, Any]] = []   # In production: persisted to DB

    # ──────────────────────────────────────────────
    # CORE STATE TRANSITIONS
    # ──────────────────────────────────────────────

    def evaluate(self, escalation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Primary evaluation entry point. Applies deterministic rules
        and returns the resolved state + decision path.
        """
        esc_id       = escalation["escalation_id"]
        created_at   = escalation["created_at"]           # datetime
        approvals    = escalation.get("approvals", [])    # list of {role, decision, timestamp}
        current_risk = escalation.get("current_risk_score", 0.0)
        envelope_modified = escalation.get("envelope_modified_mid_escalation", False)
        emergency_override = escalation.get("emergency_override", False)

        # 1. Emergency override — highest priority
        if emergency_override:
            return self._transition(esc_id, EscalationState.OVERRIDDEN,
                                    "Emergency override by Owner.")

        # 2. Timeout check
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        if age_hours > ESCALATION_SLA_HOURS and not approvals:
            return self._transition(esc_id, EscalationState.EXPIRED,
                                    f"No response within {ESCALATION_SLA_HOURS}h SLA.")

        # 3. Envelope modified mid-escalation → re-evaluate from scratch
        if envelope_modified:
            return self._transition(esc_id, EscalationState.PENDING,
                                    "Envelope changed during review. Escalation reset to PENDING.")

        # 4. Risk escalated mid-review
        if current_risk > 0.85:
            return self._transition(esc_id, EscalationState.PENDING,
                                    f"Risk score {current_risk} > 0.85. Escalated to Owner before proceeding.")

        # 5. No approvals yet
        if not approvals:
            return self._transition(esc_id, EscalationState.PENDING, "Awaiting review.")

        # 6. Conflict resolution — multiple approvers with conflicting decisions
        approved_roles = [a for a in approvals if a["decision"] == "approved"]
        rejected_roles = [a for a in approvals if a["decision"] == "rejected"]

        if approved_roles and rejected_roles:
            # Highest-priority role wins the conflict deterministically
            top_approval  = max(approved_roles, key=lambda a: ROLE_PRIORITY.get(a["role"], 0))
            top_rejection = max(rejected_roles, key=lambda a: ROLE_PRIORITY.get(a["role"], 0))

            ap = ROLE_PRIORITY.get(top_approval["role"], 0)
            rp = ROLE_PRIORITY.get(top_rejection["role"], 0)

            if ap > rp:
                return self._transition(esc_id, EscalationState.APPROVED,
                                        f"Conflict resolved: {top_approval['role']} (P={ap}) overrides {top_rejection['role']} (P={rp}).")
            elif rp > ap:
                return self._transition(esc_id, EscalationState.REJECTED,
                                        f"Conflict resolved: {top_rejection['role']} (P={rp}) overrides {top_approval['role']} (P={ap}).")
            else:
                # Equal priority — conservative default: reject
                return self._transition(esc_id, EscalationState.REJECTED,
                                        "Equal-priority conflict. Conservative default: REJECTED.")

        # 7. Unanimous approval
        if approved_roles and not rejected_roles:
            return self._transition(esc_id, EscalationState.APPROVED, "All reviewers approved.")

        # 8. Unanimous rejection
        return self._transition(esc_id, EscalationState.REJECTED, "All reviewers rejected.")

    # ──────────────────────────────────────────────
    # STATE LOGGER
    # ──────────────────────────────────────────────

    def _transition(self, esc_id: str, state: EscalationState, reason: str) -> Dict[str, Any]:
        entry = {
            "escalation_id": esc_id,
            "resolved_state": state.value,
            "reason": reason,
            "resolved_at": datetime.utcnow().isoformat()
        }
        self._state_log.append(entry)
        logger.info(f"ESC_STATE [{esc_id}] → {state.value}: {reason}")
        return entry

    def get_log(self) -> List[Dict[str, Any]]:
        return self._state_log
