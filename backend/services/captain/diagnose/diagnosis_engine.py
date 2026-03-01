from typing import Dict, Any, List
from datetime import datetime
import asyncio

from backend.services.captain.diagnose.signal_aggregator import SignalAggregator
from backend.services.captain.diagnose.campaign_classifier import CampaignClassifier
from backend.services.captain.diagnose.account_aggregator import AccountAggregator
from backend.services.captain.diagnose.confidence_engine import ConfidenceEngine
from backend.services.captain.diagnose.llm_reasoner import LLMReasoner

class CaptainDiagnosisEngine:
    """
    Core Pipeline orchestrating the 5-layer Hybrid Multi-Level Architecture.
    Takes AtlasSignals directly, runs deterministic models, and outputs LLM-backed
    narratives wrapped in JSON payload.
    """
    
    def __init__(self):
        self.signal_layer = SignalAggregator()
        self.campaign_layer = CampaignClassifier()
        self.account_layer = AccountAggregator()
        self.confidence_layer = ConfidenceEngine()
        self.narrative_layer = LLMReasoner()
        self.engine_version = "v1.0"

    async def run_hybird_diagnosis(
        self, 
        campaigns_payload: List[Dict[str, Any]], 
        benchmark_baseline: Dict[str, Any], 
        genesis_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes strictly Top-Down matching Layer 1 -> Layer 5.
        campaigns_payload example: 
        [{"campaign_id": "c_1", "metrics": {"revenue": 100, "spend": 50}, "features": {"roas_1d": 2.0, "ctr": 0.03}}]
        """
        
        campaign_states = []
        metrics_dict = {}
        
        # ---------- LAYER 1 & 2 ----------
        for cap in campaigns_payload:
            c_id = cap["campaign_id"]
            features = cap.get("features", {})
            metrics_dict[c_id] = cap.get("metrics", {"revenue": 0, "spend": 0})
            
            # Layer 1: Math
            deviations = self.signal_layer.compute_campaign_deviations(features, benchmark_baseline, genesis_profile)
            
            # Layer 2: Rule Assignment
            state_obj = self.campaign_layer.classify_campaign(c_id, deviations)
            campaign_states.append(state_obj)
            
        # ---------- LAYER 3 ----------
        account_summary = self.account_layer.aggregate_account_state(campaign_states, metrics_dict)
        
        # ---------- LAYER 4 ----------
        confidence = self.confidence_layer.calculate_confidence(campaign_states, account_summary)
        
        # Construct Draft Output Schema for LLM Context
        diagnostic_context = {
            "account_state": account_summary.get("account_state"),
            "risk_level": account_summary.get("risk_level"),
            "confidence_score": confidence,
            "campaign_states": campaign_states
        }
        
        # ---------- LAYER 5 ----------
        # Force LLM exclusively into contextual response (NOT state assignment)
        narrative = await self.narrative_layer.generate_explanation(diagnostic_context)
        
        # Pack Final JSON
        return {
            "engine_name": "CaptainDiagnose",
            "engine_version": self.engine_version,
            "account_state": account_summary.get("account_state"),
            "campaign_breakdown": campaign_states,
            "confidence_score": confidence,
            "primary_focus": narrative.get("primary_focus"),
            "secondary_focus": narrative.get("secondary_focus"),
            "strategic_direction": narrative.get("strategic_direction"),
            "risk_level": account_summary.get("risk_level"),
            "explanation": narrative.get("explanation"),
            "supporting_signals": {
                "stability_index": account_summary.get("stability_index"),
                "spend_weights": account_summary.get("spend_weights")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
