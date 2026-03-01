import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Tracks microservice interactions across the Five Matter elements 
    measuring pipeline reliability statically.
    """

    def calculate_engine_health(self, uptime_metrics: Dict[str, float], execution_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Derives latencies and physical success limits safely.
        """
        total_executions = len(execution_logs)
        if total_executions == 0:
            return {"failure_rate": 0.0, "rollback_frequency": 0.0, "status": "healthy"}
            
        failures = sum(1 for log in execution_logs if log.get("status") == "failed")
        rollbacks = sum(1 for log in execution_logs if log.get("status") == "rollback_triggered")
        
        failure_rate = failures / total_executions
        rollback_frequency = rollbacks / total_executions
        
        status = "healthy"
        if failure_rate > 0.1 or rollback_frequency > 0.05:
            status = "degraded"
            logger.warning(f"HealthMonitor detects degraded throughput! Failures: {failure_rate*100}% | Rollbacks: {rollback_frequency*100}%")
            
        return {
            "failure_rate": round(failure_rate, 3),
            "rollback_frequency": round(rollback_frequency, 3),
            "sync_latency_ms": uptime_metrics.get("avg_latency_ms", 150),
            "status": status
        }
