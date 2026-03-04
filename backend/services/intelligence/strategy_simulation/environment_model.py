"""
Environment Model
=================
Synthesizes current platform metrics (Meta/Google), signals, and competitor saturation
into a cohesive `EnvironmentState` to ground predictions realistically.
"""

from typing import Dict, Any, List
import logging

from .models import EnvironmentState

logger = logging.getLogger(__name__)

class EnvironmentModel:
    """
    Loads and mathematically represents the real world conditions that
    strategies constrain against (like current CPC or Audience Saturation).
    """

    def load_environment(self, company_id: str, company_context: Dict[str, Any]) -> EnvironmentState:
        """
        Produce a quantifiable snapshot of the marketing ecosystem.
        """
        logger.debug(f"[EnvironmentModel] Loading real-world physics for {company_id}.")
        
        # Parse inputs from standard context arrays (Hawkeye, Pulse, Sentinel, etc)
        # We simulate extraction logic here:
        perf = company_context.get("current_performance", {})
        market = company_context.get("market_signals", {})
        comp = company_context.get("competitor_intelligence", {}).get("market_pressure", {})
        flags = company_context.get("critical_flags", {})
        
        # Calculate heuristics
        base_cpa = perf.get("avg_cpa", 25.0)
        cpm_trend = market.get("cpm_trend", 0.0)
        
        # Dummy environmental physics
        avg_cpm = 10.0 * (1 + cpm_trend)
        avg_ctr = 0.012  # Industry baseline
        conv_rate = 0.04
        
        # Adjust for fatigue and pressure
        saturation = 0.85 if flags.get("creative_fatigue") else 0.40
        pressure   = comp.get("saturation_score", 0.50)  if isinstance(comp, dict) else 0.50

        state = EnvironmentState(
            average_cpm=round(avg_cpm, 2),
            average_ctr=round(avg_ctr, 3),
            conversion_rate=round(conv_rate, 3),
            audience_saturation=round(saturation, 2),
            competitor_pressure=round(pressure, 2)
        )

        logger.debug(f"[EnvironmentModel] Physics Built: Saturation {saturation*100}% | Pressure {pressure*100}%")
        return state
