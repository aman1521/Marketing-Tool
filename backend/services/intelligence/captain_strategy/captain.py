"""
CaptainStrategy (The Brain)
===========================
Orchestrator for the Decision Layer. Synthesizes inputs from the 4 Perception Engines, 
builds a fused understanding, detects threats/opportunities, and outputs actionable Execution Strategies.

Inputs: Memory, Competitor, Genome, Market
Outputs: `GeneratedStrategy` and List of `RecommendedAction`
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .models import GeneratedStrategy, RecommendedAction, StrategyStatus, ActionType
from .context_builder import ContextBuilder
from .signal_fusion import SignalFusionEngine
from .opportunity_detector import OpportunityDetector
from .threat_detector import ThreatDetector
from .strategy_generator import StrategyGenerator
from .outcome_predictor import OutcomePredictor

logger = logging.getLogger(__name__)

class CaptainStrategy:
    """
    The orchestrator module that acts as the Chief Marketing Strategist.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db           = db_session
        self.builder      = ContextBuilder()
        self.fusion       = SignalFusionEngine()
        self.opportunities= OpportunityDetector()
        self.threats      = ThreatDetector()
        self.generator    = StrategyGenerator()
        self.predictor    = OutcomePredictor()

    def generate_strategy(self, company_id: str, industry: str, current_campaigns: List[Dict]) -> Dict[str, Any]:
        """
        Executes the 8-Step Brain Flow.
        Returns the dictionary representing the ultimate strategy.
        """
        logger.info(f"[CaptainStrategy] Initiating 8-Step Brain Flow for {company_id}.")

        # 1. Perception: Gather Raw Signals
        raw_context = self.builder.build_snapshot(company_id, industry, current_campaigns)

        # 2. Understanding: Feature Engineering & Context Fusion
        fused_matrix = self.fusion.fuse_context(raw_context)

        # 3. Detection: Opportunities (Asymmetric Upside)
        detected_opportunities = self.opportunities.scan(fused_matrix)

        # 4. Detection: Threats (Systemic or Market Risk)
        detected_threats = self.threats.scan(fused_matrix)

        # 5. Decision: Strategy Generation
        strategy_payload = self.generator.generate(detected_opportunities, detected_threats)
        
        narrative     = strategy_payload["narrative"]
        action_drafts = strategy_payload["actions"]

        # 6. Decision: Strategic Simulation & Baseline Prediction
        # Apply the outcome predictor to each action to estimate CPA and Lift
        refined_actions = []
        global_roas_delta = 0.0
        global_cpa_delta  = 0.0
        avg_confidence    = 0.0
        
        for draft in action_drafts:
            # Predict the specific action outcome
            predictions = self.predictor.predict(draft, {"operator_memory": raw_context.get("operator_memory", {})})
            
            action_obj = RecommendedAction(
                action_type=draft["action_type"],
                payload=draft.get("payload", {}),
                rationale=draft.get("rationale", ""),
                expected_cpa_delta=predictions["expected_cpa_delta"],
                expected_ctr_delta=predictions["expected_ctr_delta"],
                expected_roas_delta=predictions["expected_roas_delta"],
                status="pending"
            )
            refined_actions.append(action_obj)
            
            # Aggregate globals
            global_roas_delta += predictions["expected_roas_delta"]
            global_cpa_delta  += predictions["expected_cpa_delta"]
            avg_confidence    += predictions["confidence"]

        if refined_actions:
            avg_confidence /= len(refined_actions)
            global_roas_delta /= len(refined_actions)
            global_cpa_delta /= len(refined_actions)

        # 7. Construct Final Strategy Package
        strategy_obj = GeneratedStrategy(
            company_id=company_id,
            fused_context=fused_matrix,
            opportunities=detected_opportunities,
            threats=detected_threats,
            narrative=narrative,
            confidence_score=round(avg_confidence, 4),
            risk_score=round(0.15, 4), # Dummy risk baseline
            predicted_lift=round(global_roas_delta, 4),
            predicted_cpa_change=round(global_cpa_delta, 4),
            status=StrategyStatus.PENDING_APPROVAL
        )

        # Option: Commit to DB if session provided
        if self.db:
            try:
                self.db.add(strategy_obj)
                self.db.flush() # get strategy ID
                for ra in refined_actions:
                    ra.strategy_id = strategy_obj.id
                    self.db.add(ra)
                self.db.commit()
            except Exception as e:
                logger.error(f"[CaptainStrategy] DB Insert failed: {e}")
                self.db.rollback()

        # 8. Return structured dict to flow down to Hawkeye/Forge
        return {
            "strategy_id": strategy_obj.id,
            "company_id":  company_id,
            "narrative":   narrative,
            "opportunities": detected_opportunities,
            "threats":     detected_threats,
            "actions":     [
                {
                    "type": a.action_type, 
                    "payload": a.payload, 
                    "rationale": a.rationale,
                    "expected_cpa_delta": a.expected_cpa_delta
                } 
                for a in refined_actions
            ],
            "confidence":  strategy_obj.confidence_score,
            "predicted_cpa_change": strategy_obj.predicted_cpa_change
        }
