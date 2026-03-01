import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.pulse.seasonality_engine import SeasonalityEngine
from backend.services.pulse.volatility_engine import VolatilityEngine
from backend.services.pulse.demand_engine import DemandEngine
from backend.services.pulse.macro_drift_engine import MacroDriftEngine
from backend.services.pulse.schemas import PulseOutputSchema
from backend.services.pulse.pulse_registry import PulseRegistry

logger = logging.getLogger(__name__)

class PulseEngine:
    """
    Gravity Integrator Framework.
    Generates exact mathematical contextual modifiers representing macro market forces.
    These natively attach to CaptainDiagnose vectors modifying its output confidence scores deterministically.
    """

    def __init__(self, db_session: AsyncSession):
         self.db = db_session
         self.seasonality = SeasonalityEngine()
         self.volatility = VolatilityEngine()
         self.demand = DemandEngine()
         self.drift = MacroDriftEngine()
         self.registry = PulseRegistry(db_session)

    def _determine_market_phase(self, seasonality_idx: float, demand_idx: float, volatility_idx: float, drift_idx: float) -> str:
        """
        Derives String-defined environment phase controlling execution velocity thresholds implicitly.
        """
        if volatility_idx > 0.6 and drift_idx < -0.1:
            return "volatile_decline"
            
        if volatility_idx > 0.6 and demand_idx > 0.2:
            return "chaotic_surge"
            
        if seasonality_idx > 0.75 and demand_idx > 0:
            return "seasonal_peak_stable"
            
        if seasonality_idx < 0.25 and demand_idx < 0:
            return "seasonal_trough_dry"
            
        if drift_idx < -0.2 and demand_idx < -0.2:
            return "macro_collapse"
            
        return "stable_baseline"

    def _calculate_confidence_modifier(self, phase: str, volatility_idx: float) -> float:
        """
        The critical output of the Pulse Engine. 
        Adjusts the eventual CaptainDiagnose output. High market panic artificially drops
        Captain's logic conviction allowing Governance caps to stop Auto Execution logic naturally.
        Never drops below 0.1 (Will not zero-out models).
        """
        mod = 1.0 # 100% baseline (no modifier)
        
        # Severe volatility penalizes confidence mathematical models
        if volatility_idx > 0.6:
            mod -= (volatility_idx * 0.5) 
            
        # Specific phases limit aggression mechanically
        if "collapse" in phase:
            mod -= 0.3
        elif "volatile" in phase:
            mod -= 0.15
            
        # Peak stability can slightly reinforce ML execution models
        if phase == "stable_baseline":
            mod += 0.05
            
        return round(min(1.0, max(0.1, mod)), 3)

    async def execute_macro_scan(self, 
                                 company_id: str, 
                                 revenue_history: List[float], 
                                 cpm_history: List[float], 
                                 cpa_history: List[float], 
                                 baseline_conversions: float, 
                                 current_conversions: float, 
                                 platform_drift_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Sequentially structures the Gravity engines into a formal Context Modifier.
        Runs daily (e.g. at Midnight UTC) asynchronously producing the framework Captain
        relies upon continuously.
        """
        logger.info(f"Initiating Global Macro Scan for {company_id}")
        
        # Orchestrate Modules (Deterministic Mappings)
        sz = self.seasonality.calculate_seasonality(revenue_history, current_revenue_velocity=0) # Velocity placeholder
        vol = self.volatility.calculate_volatility(cpm_history, cpa_history)
        dem = self.demand.calculate_demand_shift(baseline_conversions, current_conversions)
        drf = self.drift.evaluate_platform_drift(platform_drift_factors)
        
        # Extract individual Indexes
        s_idx = sz.get("seasonality_index", 0.5)
        v_idx = vol.get("volatility_index", 0.0)
        d_idx = dem.get("demand_shift_score", 0.0)
        dr_idx = drf.get("macro_drift_score", 0.0)
        
        # Analyze Interaction
        market_phase = self._determine_market_phase(s_idx, d_idx, v_idx, dr_idx)
        modifier = self._calculate_confidence_modifier(market_phase, v_idx)
        
        # Pydantic Structural Guarantee Check
        payload = PulseOutputSchema(
             seasonality_index=s_idx,
             demand_shift_score=d_idx,
             volatility_index=v_idx,
             macro_drift_score=dr_idx,
             market_phase=market_phase,
             confidence_modifier=modifier
        ).model_dump()
        
        # Persist to Active State DB securely
        await self.registry.log_pulse_iteration(company_id, payload)
        
        logger.info(f"Pulse Orchestrator Complete. Multiplier Mod: {modifier}x | Market Phase: {market_phase}")
        return payload
