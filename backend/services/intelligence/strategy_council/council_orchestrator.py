"""
Council Orchestrator
====================
The Maestro of the multi-agent pipeline. Orchestrates the gathering of 
Insights, runs the Debate Engine, and triggers the Synthesis Engine.
"""

import logging
from typing import Dict, Any, List

from .models import CouncilSynthesis
from .growth_agent import GrowthAgent
from .creative_agent import CreativeAgent
from .market_agent import MarketAgent
from .competitor_agent import CompetitorAgent
from .risk_agent import RiskAgent
from .debate_engine import DebateEngine
from .synthesis_engine import SynthesisEngine

logger = logging.getLogger(__name__)

class StrategyCouncil:
    """
    Simulates a virtual marketing leadership team.
    Agents debate strategy against the fused context.
    """

    def __init__(self):
        self.growth      = GrowthAgent()
        self.creative    = CreativeAgent()
        self.market      = MarketAgent()
        self.competitor  = CompetitorAgent()
        self.risk        = RiskAgent()
        self.debate      = DebateEngine()
        self.synthesis   = SynthesisEngine()

    def run_council(self, strategic_context: Dict[str, Any]) -> CouncilSynthesis:
        """
        Executes the full Multi-Agent Council flow.
        """
        logger.info("[StrategyCouncil] Convening Strategy Council Debate.")

        # 1. Gather Agent Insights (Perception -> Proposal)
        insights = [
            self.growth.analyze(strategic_context),
            self.creative.analyze(strategic_context),
            self.market.analyze(strategic_context),
            self.competitor.analyze(strategic_context),
            self.risk.analyze(strategic_context)
        ]

        # 2. Run Debate Phase (Challenge / Support)
        debate_log = self.debate.run_debate(insights)

        # 3. Compile Final Strategy (Synthesis)
        final_synthesis = self.synthesis.synthesize(insights, debate_log)
        
        logger.info(f"[StrategyCouncil] Synthesized {len(final_synthesis.final_actions)} definitive actions.")

        return final_synthesis
