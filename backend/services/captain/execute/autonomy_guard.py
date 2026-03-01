from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AutonomyGuard:
    """
    Hard Governance Rule Gate for CaptainExecute.
    Blocks any automated action that intersects with defined Genesis Constraints 
    or Atlas Signal anomaly flags.
    """

    def check_autonomy_safe(
        self, 
        action: Dict[str, Any], 
        genesis_constraints: Dict[str, Any], 
        diagnostic_context: Dict[str, Any],
        signal_features: Dict[str, Any]
    ) -> bool:
        """
        Runs exhaustive matrix evaluation to ensure auto-execution is mathematically safe.
        """
        
        c_id = action.get("campaign_id", "unknown")
        
        # 1. Global Auto Execute Check
        if not genesis_constraints.get("auto_execution_enabled", False):
            logger.warning(f"[{c_id}] Autonomy blocked: Genesis auto_execution_enabled is False.")
            return False
            
        # 2. Confidence & Risk Score Caps
        current_risk_level = self._map_risk_to_float(diagnostic_context.get("risk_level", "HIGH"))
        max_risk_score = genesis_constraints.get("max_risk_score", 0.0)
        
        if current_risk_level > max_risk_score:
            logger.warning(f"[{c_id}] Autonomy blocked: Current risk ({current_risk_level}) > Max allowed ({max_risk_score}).")
            return False
            
        confidence = diagnostic_context.get("confidence_score", 0.0)
        if confidence < 0.65: # Hard assumption that autonomy requires strong conviction
            logger.warning(f"[{c_id}] Autonomy blocked: Confidence score ({confidence}) too low.")
            return False

        # 3. Anomaly Flags
        anomaly_score = signal_features.get("anomaly_score", 0.0)
        if anomaly_score > 0.5:
             logger.warning(f"[{c_id}] Autonomy blocked: High anomaly score detected ({anomaly_score}).")
             return False

        # 4. Action Specific Blocks (E.g. Budget math validation)
        action_type = action.get("action_type")
        params = action.get("parameters", {})
        
        if action_type == "BUDGET_INCREASE":
            old_b = params.get("old_budget", 0)
            new_b = params.get("new_budget", 0)
            
            if old_b > 0:
                change_pct = ((new_b - old_b) / old_b) * 100
                max_pct = genesis_constraints.get("max_budget_change_percent", 0.0)
                if change_pct > max_pct:
                    logger.warning(f"[{c_id}] Autonomy blocked: Budget change ({change_pct}%) exceeds Genesis constraint ({max_pct}%).")
                    return False
                    
            if new_b > genesis_constraints.get("max_daily_budget", 0.0):
                logger.warning(f"[{c_id}] Autonomy blocked: New budget ({new_b}) exceeds Max Daily ({genesis_constraints.get('max_daily_budget')}).")
                return False

        if action_type == "PAUSE_CREATIVE" and not genesis_constraints.get("creative_sandbox_required", True):
            # Optional constraints map
            pass

        logger.info(f"[{c_id}] Auto-Execution fully cleared by Autonomy Guard.")
        return True

    def _map_risk_to_float(self, risk_level: str) -> float:
        mapping = {"LOW": 0.2, "MODERATE": 0.5, "HIGH": 0.8, "CRITICAL": 1.0}
        return mapping.get(risk_level, 1.0)
