"""
Intelligence Orchestrator (The Main Loop)
=========================================
Pulls together the Context, Multi-Agent Council, CaptainStrategy, Simulation Twin, 
and Execution Router into the singular unified AI autonomous cycle.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.services.intelligence.captain_strategy.captain import CaptainStrategy
from backend.services.intelligence.captain_strategy.execution_router import ExecutionRouter
from backend.services.intelligence.strategy_council.council_orchestrator import StrategyCouncil
from backend.services.intelligence.strategy_simulation.simulator import StrategySimulationEngine
from backend.services.intelligence.marketing_knowledge.context_builder import KnowledgeContextBuilder
from backend.services.intelligence.marketing_knowledge.retrieval_engine import RetrievalEngine

logger = logging.getLogger(__name__)

class UnifiedIntelligenceOrchestrator:
    """
    The highest-level control loop. 
    Connects: Council Debate -> Synthesized Strategy -> Simulation testing -> Execution Boundaries.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.council         = StrategyCouncil()
        self.captain         = CaptainStrategy(db_session=self.db)
        self.simulator       = StrategySimulationEngine(db_session=self.db)
        self.router          = ExecutionRouter() # Usually receives Forge/Hawkeye interfaces
        self.knowledge_ctx   = KnowledgeContextBuilder()
        self.knowledge       = RetrievalEngine()

    async def execute_intelligence_loop(self, company_id: str, industry: str, current_campaigns: List[Dict]) -> Dict[str, Any]:
        """
        The absolute core of the autonomous marketing OS. Runs periodically (e.g., hourly).
        """
        logger.info(f"=== [Orchestrator] Beginning Unified Intelligence Cycle for {company_id} ===")

        # ---------------------------------------------------------
        # 1. Perception Layer (Context Synthesis)
        # ---------------------------------------------------------
        # Use CaptainStrategy's builder natively since it polls all engines
        raw_context = self.captain.builder.build_snapshot(company_id, industry, current_campaigns)
        fused_matrix = self.captain.fusion.fuse_context(raw_context)

        logger.info(f"[Orchestrator] Step 1 Complete: Snapshot generated {fused_matrix.get('momentum')} momentum.")

        # ---------------------------------------------------------
        # 2. Marketing Knowledge Engine (Retrieve LLM Playbooks)
        # ---------------------------------------------------------
        mke_context = self.knowledge_ctx.build_context(raw_context)
        playbooks = await self.knowledge.retrieve_relevant_skills(mke_context)
        
        # We append the exact playbook schemas back into the matrix so the Agent Council
        # can use them during the Debate Phase.
        fused_matrix["active_playbooks"] = [p.name for p in playbooks]
        
        logger.info(f"[Orchestrator] Step 2 Complete: Loaded {len(playbooks)} relevant Marketing Playbooks.")

        # ---------------------------------------------------------
        # 3. Multi-Agent Council (Debate)
        # ---------------------------------------------------------
        council_decision = self.council.run_council(fused_matrix)
        
        if not council_decision.final_actions:
             logger.warning("[Orchestrator] Council proposed no actions. Cycle Terminated.")
             return {"status": "terminated", "reason": "no_council_consensus"}

        logger.info(f"[Orchestrator] Step 3 Complete: Council synthesized {len(council_decision.final_actions)} actions. Confidence {council_decision.overall_confidence}")

        # ---------------------------------------------------------
        # 4. Decision Layer (CaptainStrategy Brain)
        # ---------------------------------------------------------
        # Instead of Captain natively inferring Opps/Threats, we override it to use the Council's output
        # to format its proper Database object structs
        
        # Format the strategy object mimicking normal Brain output
        strategy_payload = {
            "strategy_id": f"strat_{company_id}_test",
            "narrative": "Council Initiated Action.",
            "actions": [a.model_dump() for a in council_decision.final_actions]
        }
        
        logger.info("[Orchestrator] Step 4 Complete: Strategy formatted.")

        # ---------------------------------------------------------
        # 5. Simulation Engine (Digital Twin Validation)
        # ---------------------------------------------------------
        refined_actions = []
        for council_action in strategy_payload["actions"]:
            logger.info(f"[Orchestrator] Spooling Simulation Engine for: {council_action.get('action_type')}")
            
            # Predict
            sim_result = self.simulator.simulate_strategy(
                company_id=company_id,
                strategy_id=strategy_payload["strategy_id"],
                proposed_action=council_action,
                context=raw_context
            )
            
            if sim_result.risk_score > 0.60 or sim_result.confidence < 0.35:
                logger.warning(f"[Orchestrator] Simulator REJECTED action {council_action.get('action_type')} (Risk: {sim_result.risk_score})")
                continue # Skip executing this one
                
            # If safe, map the optimized parameters backwards
            optimized_action = council_action.copy()
            optimized_action["payload"] = sim_result.best_scenario.parameter_variations
            refined_actions.append(optimized_action)

        if not refined_actions:
             logger.error("[Orchestrator] Simulation Engine blocked all proposed actions due to risk physics.")
             return {"status": "blocked_by_safety"}

        logger.info(f"[Orchestrator] Step 5 Complete: Simulation validated {len(refined_actions)} optimized actions.")

        # ---------------------------------------------------------
        # 6. Execution Layer Routing
        # ---------------------------------------------------------
        # We dummy up the SQLAlchemy model object for the router
        from backend.services.intelligence.captain_strategy.models import RecommendedAction
        final_objs = []
        for ra in refined_actions:
             model = RecommendedAction(
                 strategy_id=strategy_payload["strategy_id"],
                 action_type=ra["action_type"],
                 payload=ra["payload"],
                 rationale=ra.get("rationale", "")
             )
             final_objs.append(model)
             
        routing_results = self.router.route_strategy(strategy_payload["strategy_id"], final_objs)
        logger.info(f"[Orchestrator] Step 6 Complete: Dispatched Execution Payloads: {routing_results}")
        
        return {
            "status": "success",
            "strategy": strategy_payload["strategy_id"],
            "council_confidence": council_decision.overall_confidence,
            "actions_simulated": len(strategy_payload["actions"]),
            "actions_executed": len(refined_actions),
            "execution_mapping": routing_results
        }
