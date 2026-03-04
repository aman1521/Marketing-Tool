"""
Autonomy Controller Stability Protocol
=======================================
Calm, disciplined autonomy management for the Marketing OS.

Design principles:
  - React slowly to noise, quickly to real risk
  - Never drop more than one band per evaluation cycle
  - Never increase more than one step while in stabilization mode
  - Protect capital above all else
  - All decisions are traceable and deterministic
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# AUTONOMY BANDS
# ─────────────────────────────────────────────────────────────

class Band(str, Enum):
    CONSERVATIVE = "conservative"   # 20–40 %
    BALANCED     = "balanced"       # 40–60 %   ← normal operating band
    AGGRESSIVE   = "aggressive"     # 60–75 %
    DOMINANT     = "dominant"       # 75–85 %
    MAX          = "max"            # 85–95 %


BAND_RANGES: Dict[Band, Tuple[float, float]] = {
    Band.CONSERVATIVE: (20.0, 40.0),
    Band.BALANCED:     (40.0, 60.0),
    Band.AGGRESSIVE:   (60.0, 75.0),
    Band.DOMINANT:     (75.0, 85.0),
    Band.MAX:          (85.0, 95.0),
}

BAND_ORDER = [Band.CONSERVATIVE, Band.BALANCED, Band.AGGRESSIVE, Band.DOMINANT, Band.MAX]

# Default midpoints per band (used when dropping into a band)
BAND_MIDPOINTS: Dict[Band, float] = {
    Band.CONSERVATIVE: 30.0,
    Band.BALANCED:     50.0,
    Band.AGGRESSIVE:   67.5,
    Band.DOMINANT:     80.0,
    Band.MAX:          90.0,
}

# ─────────────────────────────────────────────────────────────
# SIGNAL THRESHOLDS
# ─────────────────────────────────────────────────────────────

THRESHOLDS = {
    # Volatility
    "volatility_spike"          : 0.65,   # above → drop one band
    "volatility_budget_tighten" : 0.50,   # above → tighten budget_change_limit

    # Drift
    "drift_spike"               : 0.30,   # > 30 % drift frequency → reduce

    # Rollback
    "rollback_spike"            : 0.05,   # > 5 % → stabilization mode

    # ROI
    "roi_drop_significant"      : -0.15,  # 48 h delta below -15 % → check other signals
    "roi_drop_moderate"         : -0.10,  # 48 h delta below -10 % → check other signals

    # Escalation
    "escalation_overload"       : 0.25,   # > 25 % of cycles triggered escalation

    # Confidence decay
    "confidence_decay"          : 0.70,   # avg < 0.70 → reduce
    "confidence_stable"         : 0.82,   # avg >= 0.82 for N days → expand
    "confidence_stable_days"    : 7,      # consecutive days required

    # Stabilization exit
    "stabilization_exit_cycles" : 7,      # consecutive clean cycles to exit stab. mode

    # Expansion control
    "expansion_step_pct"        : 3.0,    # max expansion per cycle
    "reduction_step_pct"        : 5.0,    # max reduction per cycle (within band)
}


# ─────────────────────────────────────────────────────────────
# STATE  (per-company; in production, persisted to DB)
# ─────────────────────────────────────────────────────────────

@dataclass
class AutonomyState:
    company_id          : str
    current_pct         : float   = 50.0
    current_band        : Band    = Band.BALANCED
    stabilization_mode  : bool    = False
    stable_cycles       : int     = 0       # consecutive clean cycles
    confidence_stable_days: int   = 0
    history             : List[Dict] = field(default_factory=list)
    last_adjustment_reason: str   = "Initial state"
    budget_change_limit_pct: float = 30.0   # live budget cap fed back to envelope
    sandbox_allocation_pct:  float = 10.0   # experiment sandbox budget %

    def to_dashboard(self) -> Dict[str, Any]:
        return {
            "company_id"            : self.company_id,
            "current_pct"           : round(self.current_pct, 2),
            "current_band"          : self.current_band.value,
            "stabilization_mode"    : self.stabilization_mode,
            "stable_cycles"         : self.stable_cycles,
            "last_adjustment_reason": self.last_adjustment_reason,
            "stability_score"       : self._stability_score(),
            "budget_change_limit_pct": self.budget_change_limit_pct,
            "sandbox_allocation_pct" : self.sandbox_allocation_pct,
            "history"               : self.history[-20:],   # last 20 events
        }

    def _stability_score(self) -> float:
        """
        0–100 composite score. Penalised by: stabilization mode, band level, recent reductions.
        """
        base = 100.0
        if self.stabilization_mode:
            base -= 30
        band_penalty = {Band.CONSERVATIVE: 20, Band.BALANCED: 0, Band.AGGRESSIVE: 5,
                        Band.DOMINANT: 15, Band.MAX: 25}
        base -= band_penalty.get(self.current_band, 0)
        recent_reductions = sum(1 for h in self.history[-5:] if h.get("delta", 0) < 0)
        base -= recent_reductions * 8
        return round(max(0.0, min(100.0, base)), 1)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _band_for_pct(pct: float) -> Band:
    for band, (lo, hi) in BAND_RANGES.items():
        if lo <= pct <= hi:
            return band
    if pct < 20.0:
        return Band.CONSERVATIVE
    return Band.MAX


def _one_band_down(band: Band) -> Optional[Band]:
    idx = BAND_ORDER.index(band)
    return BAND_ORDER[idx - 1] if idx > 0 else None


def _one_band_up(band: Band) -> Optional[Band]:
    idx = BAND_ORDER.index(band)
    return BAND_ORDER[idx + 1] if idx < len(BAND_ORDER) - 1 else None


def _clamp_to_band(pct: float, band: Band) -> float:
    lo, hi = BAND_RANGES[band]
    return round(max(lo, min(hi, pct)), 2)


# ─────────────────────────────────────────────────────────────
# MAIN CONTROLLER
# ─────────────────────────────────────────────────────────────

class AutonomyController:
    """
    Production-grade Autonomy Stability Protocol.

    Metrics expected in evaluate():
        drift_frequency        — float 0–1   (from Sentinel)
        volatility_index       — float 0–1   (from Pulse)
        rollback_rate          — float 0–1
        roi_delta_48h          — float (-1 to +1)  % change over 48h
        escalation_frequency   — float 0–1
        confidence_avg         — float 0–1
        confidence_trend       — "stable" | "decaying" | "improving"
        portfolio_exposure_pct — float 0–100
    """

    def __init__(self, db=None):
        """db is optional; pass AsyncSession in production for persistence."""
        self.db = db
        self._states: Dict[str, AutonomyState] = {}

    # ── Public API ─────────────────────────────────────────

    def evaluate(self, current_pct: float, metrics: Dict[str, Any],
                 company_id: str = "default") -> Dict[str, Any]:
        """
        Evaluate signals and compute new autonomy level.
        Returns a full result dict. Does NOT persist to DB — call apply() for that.
        """
        state = self._get_or_create_state(company_id, current_pct)
        return self._run_protocol(state, metrics)

    async def apply_and_record(self, company_id: str, current_pct: float,
                                metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate + persist to DB."""
        state = self._get_or_create_state(company_id, current_pct)
        result = self._run_protocol(state, metrics)

        if self.db is not None and result["delta"] != 0:
            try:
                from backend.marketing_os_app.advanced_models import AutonomyControlRecord
                record = AutonomyControlRecord(
                    company_id=company_id,
                    previous_pct=result["previous_pct"],
                    new_pct=result["new_pct"],
                    trigger=result["last_adjustment_reason"],
                    context=metrics
                )
                self.db.add(record)
                await self.db.commit()
            except Exception as exc:
                logger.warning(f"Could not persist autonomy record: {exc}")

        return result

    def get_dashboard(self, company_id: str) -> Dict[str, Any]:
        """Return dashboard-safe state snapshot for a company."""
        if company_id not in self._states:
            return {"error": "No state found for company"}
        return self._states[company_id].to_dashboard()

    # ── Internal Protocol ───────────────────────────────────

    def _get_or_create_state(self, company_id: str, current_pct: float) -> AutonomyState:
        if company_id not in self._states:
            self._states[company_id] = AutonomyState(
                company_id=company_id,
                current_pct=current_pct,
                current_band=_band_for_pct(current_pct)
            )
        else:
            # Sync external pct if drifted
            self._states[company_id].current_pct = current_pct
            self._states[company_id].current_band = _band_for_pct(current_pct)
        return self._states[company_id]

    def _run_protocol(self, state: AutonomyState, metrics: Dict[str, Any]) -> Dict[str, Any]:
        prev_pct  = state.current_pct
        prev_band = state.current_band
        triggers: List[str] = []
        band_change: Optional[str] = None
        adjust_pct: float = 0.0

        drift        = metrics.get("drift_frequency",      0.0)
        volatility   = metrics.get("volatility_index",     0.0)
        rollback     = metrics.get("rollback_rate",        0.0)
        roi_delta    = metrics.get("roi_delta_48h",        0.0)
        esc_freq     = metrics.get("escalation_frequency", 0.0)
        confidence   = metrics.get("confidence_avg",       1.0)
        conf_trend   = metrics.get("confidence_trend",     "stable")

        # ── Priority 1: Rollback spike → Stabilization Mode ──────────
        if rollback > THRESHOLDS["rollback_spike"]:
            if not state.stabilization_mode:
                state.stabilization_mode = True
                state.stable_cycles      = 0
                triggers.append(f"ROLLBACK_SPIKE ({rollback:.1%}) → STABILIZATION_MODE entered")
            # Drop one band
            new_band = _one_band_down(state.current_band)
            if new_band and new_band != state.current_band:
                band_change = f"{state.current_band.value} → {new_band.value}"
                state.current_band = new_band
                state.current_pct  = BAND_MIDPOINTS[new_band]
                triggers.append(f"BAND_DROP: {band_change}")
            # Restrict envelope
            state.budget_change_limit_pct = max(10.0, state.budget_change_limit_pct - 5.0)
            state.sandbox_allocation_pct  = max(3.0,  state.sandbox_allocation_pct  - 2.0)

        # ── Priority 2: Volatility spike ─────────────────────────────
        elif volatility > THRESHOLDS["volatility_spike"]:
            triggers.append(f"VOLATILITY_SPIKE ({volatility:.2f})")
            new_band = _one_band_down(state.current_band)
            if new_band and new_band != state.current_band:
                band_change = f"{state.current_band.value} → {new_band.value}"
                state.current_band = new_band
                state.current_pct  = BAND_MIDPOINTS[new_band]
                triggers.append(f"BAND_DROP: {band_change}")
            # Also tighten envelope
            if volatility > THRESHOLDS["volatility_budget_tighten"]:
                state.budget_change_limit_pct = max(10.0, state.budget_change_limit_pct - 3.0)
                state.sandbox_allocation_pct  = max(3.0,  state.sandbox_allocation_pct  - 1.0)
                triggers.append("BUDGET_LIMIT_TIGHTENED")

        # ── Priority 3: Drift spike ───────────────────────────────────
        elif drift > THRESHOLDS["drift_spike"]:
            triggers.append(f"DRIFT_SPIKE ({drift:.1%})")
            # Reduce within band, not necessarily a full band drop
            adjust_pct = -THRESHOLDS["reduction_step_pct"]

        # ── Priority 4: Confidence decay ─────────────────────────────
        elif confidence < THRESHOLDS["confidence_decay"] or conf_trend == "decaying":
            triggers.append(f"CONFIDENCE_DECAY (avg={confidence:.2f}, trend={conf_trend})")
            new_band = _one_band_down(state.current_band)
            if new_band and new_band != state.current_band:
                band_change = f"{state.current_band.value} → {new_band.value}"
                state.current_band = new_band
                state.current_pct  = BAND_MIDPOINTS[new_band]
                triggers.append(f"BAND_DROP: {band_change}")
            state.sandbox_allocation_pct = min(20.0, state.sandbox_allocation_pct + 3.0)
            triggers.append("SANDBOX_EXPANDED for learning")

        # ── Priority 5: Escalation overload ──────────────────────────
        elif esc_freq > THRESHOLDS["escalation_overload"]:
            triggers.append(f"ESCALATION_OVERLOAD ({esc_freq:.1%})")
            # Widen envelope slightly rather than dropping band (avoids spam)
            state.budget_change_limit_pct = min(35.0, state.budget_change_limit_pct + 2.0)
            triggers.append("ENVELOPE_WIDENED slightly to reduce escalation spam")

        # ── Priority 6: ROI drop — nuanced response ───────────────────
        elif roi_delta < THRESHOLDS["roi_drop_significant"]:
            triggers.append(f"ROI_DROP_SIGNIFICANT (48h delta={roi_delta:.1%})")
            # Only reduce if corroborated by drift OR volatility
            if drift > THRESHOLDS["drift_spike"] * 0.6 or volatility > THRESHOLDS["volatility_budget_tighten"]:
                adjust_pct = -THRESHOLDS["reduction_step_pct"]
                triggers.append("CORROBORATED by drift/volatility → reduction applied")
            else:
                triggers.append("SIGNALS_NORMAL → maintaining autonomy, allowing self-correction")

        elif roi_delta < THRESHOLDS["roi_drop_moderate"]:
            triggers.append(f"ROI_DROP_MODERATE (48h delta={roi_delta:.1%}) → monitoring, no action")

        # ── Stabilization mode: check for exit ───────────────────────
        if state.stabilization_mode:
            cycle_clean = (
                rollback  <= THRESHOLDS["rollback_spike"] * 0.6
                and drift <= THRESHOLDS["drift_spike"] * 0.6
                and volatility <= THRESHOLDS["volatility_spike"] * 0.7
                and confidence >= THRESHOLDS["confidence_stable"]
            )
            if cycle_clean:
                state.stable_cycles += 1
                triggers.append(f"STABLE_CYCLE {state.stable_cycles}/{THRESHOLDS['stabilization_exit_cycles']}")
            else:
                state.stable_cycles = 0   # reset counter if any noise

            if state.stable_cycles >= THRESHOLDS["stabilization_exit_cycles"]:
                state.stabilization_mode = False
                state.stable_cycles      = 0
                triggers.append("STABILIZATION_MODE exited after 7 consecutive stable cycles")
                logger.info(f"[{state.company_id}] Stabilization mode exited cleanly")
        else:
            # Only consider expansion when fully stable and no triggers yet
            if not triggers:
                state.confidence_stable_days += 1
                if (state.confidence_stable_days >= THRESHOLDS["confidence_stable_days"]
                        and confidence >= THRESHOLDS["confidence_stable"]
                        and conf_trend in ("stable", "improving")):
                    # Gradual band expansion
                    target_pct = state.current_pct + THRESHOLDS["expansion_step_pct"]
                    band_lo, band_hi = BAND_RANGES[state.current_band]
                    if target_pct > band_hi:
                        # Attempt to move up one band
                        new_band = _one_band_up(state.current_band)
                        if new_band:
                            band_change = f"{state.current_band.value} → {new_band.value}"
                            state.current_band = new_band
                            state.current_pct  = BAND_RANGES[new_band][0] + THRESHOLDS["expansion_step_pct"]
                            triggers.append(f"CONFIDENCE_STABLE → BAND_PROMOTION: {band_change}")
                    else:
                        state.current_pct = target_pct
                        triggers.append(f"CONFIDENCE_STABLE → GRADUAL_EXPANSION +{THRESHOLDS['expansion_step_pct']}%")
                    state.confidence_stable_days = 0  # reset after acting
            else:
                state.confidence_stable_days = 0   # any signal resets counter

        # ── Apply within-band adjustment (from adjust_pct) ───────────
        if adjust_pct != 0:
            state.current_pct = _clamp_to_band(
                state.current_pct + adjust_pct, state.current_band
            )

        # ── Hard clamp to current band bounds ────────────────────────
        state.current_pct = _clamp_to_band(state.current_pct, state.current_band)

        # ── No triggers = system healthy ─────────────────────────────
        if not triggers:
            triggers = ["NO_ACTION: all signals nominal"]

        reason = " | ".join(triggers)
        state.last_adjustment_reason = reason

        delta = round(state.current_pct - prev_pct, 2)

        # Persist to history ring buffer
        state.history.append({
            "timestamp"  : datetime.utcnow().isoformat(),
            "previous_pct": prev_pct,
            "new_pct"    : round(state.current_pct, 2),
            "prev_band"  : prev_band.value,
            "new_band"   : state.current_band.value,
            "delta"      : delta,
            "triggers"   : triggers,
            "stabilization_mode": state.stabilization_mode,
        })
        if len(state.history) > 200:
            state.history = state.history[-200:]

        logger.info(
            f"AUTONOMY [{state.company_id}] {prev_pct:.1f}% → {state.current_pct:.1f}% "
            f"| band: {prev_band.value} → {state.current_band.value} | {reason}"
        )

        return {
            "previous_pct"          : prev_pct,
            "new_pct"               : round(state.current_pct, 2),
            "delta"                 : delta,
            "previous_band"         : prev_band.value,
            "current_band"          : state.current_band.value,
            "band_changed"          : band_change,
            "triggers"              : triggers,
            "last_adjustment_reason": reason,
            "stabilization_mode"    : state.stabilization_mode,
            "stable_cycles"         : state.stable_cycles,
            "stability_score"       : state._stability_score(),
            "budget_change_limit_pct": state.budget_change_limit_pct,
            "sandbox_allocation_pct" : state.sandbox_allocation_pct,
            "mode"                  : state.current_band.value,
        }
