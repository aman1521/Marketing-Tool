"""
Context Builder (Marketing Knowledge)
=====================================
Structures physical reality (from DB/Connectors) into a `MarketingContext` 
format that the Retrieval Engine can read to pull the right Skills.
"""

from typing import Dict, Any, Optional
import logging

from .models import MarketingContext

logger = logging.getLogger(__name__)

class KnowledgeContextBuilder:
    """Builds a queryable snapshot of the current marketing crisis / growth area."""

    def build_context(self, raw_signals: Dict[str, Any]) -> MarketingContext:
        """
        Takes raw multi-engine inputs (like the Matrix object coming out of CaptainStrategy)
        and pulls out the specific data needed to query the vector Playbooks.
        """
        logger.debug("[KnowledgeContextBuilder] Assembling Context for vector retrieval.")
        
        # We need to map real conditions to English semantic strings for exact similarity
        perf = raw_signals.get("current_performance", {})
        flags = raw_signals.get("critical_flags", {})
        dir_signals = raw_signals.get("directional_signals", {})
        comp_intel = raw_signals.get("competitor_intelligence", {})
        
        # Try to infer the exact problem
        problem_str = "Growth stagnated."
        
        if flags.get("creative_fatigue"):
            problem_str = "Ad creatives and copy are severely fatigued causing high CPAs."
        elif flags.get("high_market_pressure") or comp_intel.get("market_pressure"):
            problem_str = "Competitors are scaling heavily into our targeting clusters driving costs up."
        elif dir_signals.get("operator_action") == "AVOID":
            problem_str = "Historical data shows a high likelihood of campaign failure here."
        
        # Build the final context packet
        ctx = MarketingContext(
            product_type=raw_signals.get("industry_category", "Saas/Software"),
            audience=raw_signals.get("primary_audience", "B2B"),
            campaign_goal="Scale efficiency while protecting core CPA margin.",
            platform=raw_signals.get("market_signals", {}).get("platform_momentum", "Meta/Google"),
            current_problem=problem_str,
            performance_metrics=perf
        )
        
        return ctx
