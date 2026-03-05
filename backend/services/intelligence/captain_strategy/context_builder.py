"""
Context Builder
===============
Collects signals from the 4 Perception Layer Engines:
1. Operator Memory
2. Competitor Intelligence
3. Creative Genome 
4. Market Signals

Constructs the raw, unstructured Reality Snapshot for the company.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.services.intelligence.operator_memory.influence_controller import InfluenceController
from backend.services.competitor_intelligence.market_pressure_detector import MarketPressureDetector
from backend.services.competitor_intelligence.strategy_gap_analyzer import StrategyGapAnalyzer
from backend.services.intelligence.creative_genome.creative_strategy_engine import CreativeStrategyEngine

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Builds the strategic reality snapshot for a given company environment.
    """

    def __init__(self,
                 memory_engine: Optional[InfluenceController] = None,
                 pressure_detector: Optional[MarketPressureDetector] = None,
                 gap_analyzer: Optional[StrategyGapAnalyzer] = None,
                 creative_strategy: Optional[CreativeStrategyEngine] = None):
        
        self.memory     = memory_engine or InfluenceController()
        self.pressure   = pressure_detector or MarketPressureDetector()
        self.gaps       = gap_analyzer or StrategyGapAnalyzer()
        self.creative   = creative_strategy or CreativeStrategyEngine()
        
        # Placeholder for external market signals (Pulse/Sentinel)
        self.market_signals = self._mock_market_signals

    def build_snapshot(self, company_id: str, industry: str, current_campaigns: List[Dict]) -> Dict[str, Any]:
        """
        Synthesize perception layer inputs into a combined snapshot context.
        """
        logger.info(f"[ContextBuilder] Assembling perception context for company: {company_id}")

        # 1. Gather Operator Context (Memory)
        # Using a dummy context dict representing a general scaling request for the company.
        # This asks the memory engine: "If we want to scale_budget right now in this industry, what do we know?"
        dummy_decision_context = {
            "strategy_type": "scale_budget",
            "industry_bucket": industry,
            "company_id": company_id
        }
        operator_memory_signal = self.memory.get_influence(company_id=company_id, decision_context=dummy_decision_context)

        # 2. Gather Competitor Intelligence
        competitor_pressure = self.pressure.detect_pressure(company_id=company_id, target_cluster="all")
        strategy_gaps = self.gaps.analyze_gaps(company_id=company_id)

        # 3. Gather Creative Genome Status
        creative_signals = []
        for campaign in current_campaigns:
            for genome in campaign.get("active_genomes", []):
                sig = self.creative.generate_signal(current_genome=genome, industry=industry)
                if sig:
                    creative_signals.append({
                        "campaign_id": campaign.get("id"),
                        "signal": sig
                    })

        # 4. Gather Macro Market Signals
        macro_signals = self.market_signals(industry)

        snapshot = {
            "company_id": company_id,
            "industry":   industry,
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            
            "operator_memory": operator_memory_signal,
            "competitor_intelligence": {
                "market_pressure": competitor_pressure,
                "strategy_gaps":   strategy_gaps
            },
            "creative_genome": {
                "active_campaign_signals": creative_signals
            },
            "market_signals": macro_signals,
            "current_performance": {
                "active_campaign_count": len(current_campaigns),
                "total_spend": sum(c.get("spend", 0) for c in current_campaigns),
                "avg_cpa": self._safe_avg([c.get("cpa", 0) for c in current_campaigns])
            }
        }
        
        return snapshot

    def _mock_market_signals(self, industry: str) -> Dict[str, Any]:
        """Mock output for Pulse engine (volatility, trends)."""
        return {
            "volatility_index": 0.45,  # Moderate market shaking
            "cpm_trend":        (-0.05 if industry == "ecommerce" else 0.12), # Drops vs hikes
            "seasonality":      "neutral",
            "platform_momentum": "tiktok" if industry == "ecommerce" else "linkedin"
        }

    @staticmethod
    def _safe_avg(nums: List[float]) -> float:
        valid = [n for n in nums if n > 0]
        return sum(valid)/len(valid) if valid else 0.0
