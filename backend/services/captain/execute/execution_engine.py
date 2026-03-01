from typing import Dict, Any, List
import logging
import asyncio

from backend.services.captain.execute.payload_validator import PayloadValidator
from backend.services.captain.execute.autonomy_guard import AutonomyGuard
from backend.services.captain.execute.platform_router import PlatformRouter
from backend.services.captain.execute.rollback_manager import RollbackManager
from backend.services.captain.execute.execution_logger import ExecutionLogger
from backend.services.captain.execute.execution_monitor import ExecutionMonitor

logger = logging.getLogger(__name__)

class CaptainExecuteEngine:
    """
    Phase 2 Capstone Module: Transforms Strategy JSON into real-world autonomous writes.
    Fails tightly against Genesis governance rules without human intervention.
    """

    def __init__(self):
        self.validator = PayloadValidator()
        self.guard = AutonomyGuard()
        self.router = PlatformRouter()
        self.rollback = RollbackManager(self.router)
        self.action_logger = ExecutionLogger()
        self.monitor = ExecutionMonitor(self.rollback, self.action_logger)

    async def execute_strategy(
        self, 
        proposed_actions: List[Dict[str, Any]], 
        genesis_constraints: Dict[str, Any], 
        diagnostic_context: Dict[str, Any], 
        signal_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reads CaptainStrategy payload. Performs Autonomy gating. Dispatches sequentially.
        """
        
        execution_results = []
        
        for action in proposed_actions:
            c_id = action.get("campaign_id", "Unknown")
            
            # Layer 1: Validate Schema
            if not self.validator.validate(action):
                await self.action_logger.log_action(action, diagnostic_context, "REJECTED_SCHEMA")
                execution_results.append({"campaign_id": c_id, "status": "failed", "reason": "schema_invalid"})
                continue
                
            # Layer 2: Autonomy Constraints Match
            is_safe = self.guard.check_autonomy_safe(action, genesis_constraints, diagnostic_context, signal_features)
            
            if not is_safe:
                # Kick back to human verification / UI manual approval loop
                await self.action_logger.log_action(action, diagnostic_context, "REQUIRES_MANUAL_APPROVAL")
                execution_results.append({"campaign_id": c_id, "status": "blocked", "reason": "violates_autonomy_governance"})
                continue
                
            # Layer 3: Execute Action
            response = await self.router.dispatch_action(action)
            
            # Track state payload
            exec_record = {
               "action": action,
               "context": diagnostic_context,
               "response": response
            }
            
            # Layer 4: Log Output strictly into Event Memory
            await self.action_logger.log_action(action, diagnostic_context, "EXECUTED")
            
            # Layer 5: Queue the 24-hr Drift Safety Monitor
            asyncio.create_task(self.monitor.trigger_monitoring_loop(exec_record))
            
            execution_results.append({"campaign_id": c_id, "status": "success", "platform_ack": response.get("platform_ack_id")})

        return {
            "engine": "CaptainExecute",
            "version": "v1.0",
            "executions": execution_results
        }
