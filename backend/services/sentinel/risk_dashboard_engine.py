import logging
from typing import Dict, Any, List

from backend.services.sentinel.health_monitor import HealthMonitor
from backend.services.sentinel.drift_detector import DriftDetector
from backend.services.sentinel.schemas import SentinelRiskSchema

logger = logging.getLogger(__name__)

class RiskDashboardEngine:
    """
    Exposes final unified metrics calculating total system reliability across Five Layers.
    """

    def __init__(self):
        self.health = HealthMonitor()
        self.drift = DriftDetector()

    def generate_dashboard_metrics(self, 
                                   uptime_metrics: Dict[str, float], 
                                   execution_history: List[Dict[str, Any]], 
                                   drift_variances: List[float]) -> SentinelRiskSchema:
        """
        Aggregates arrays mathematically into bounding standardizations (0 to 1).
        """
        # Health
        engine_health = self.health.calculate_engine_health(uptime_metrics, execution_history)
        failure_rate = engine_health.get("failure_rate", 0.0)
        
        # Stability index drops proportional to physical API/OS errors
        stability_idx = min(1.0, max(0.0, 1.0 - (failure_rate * 2.0)))
        
        # Drift Frequency (How often is the variance > 0.3?)
        drift_hits = sum(1 for v in drift_variances if abs(v) > 0.3)
        drift_freq = min(1.0, (drift_hits / max(1, len(drift_variances))))
        
        # Execution Precision refers to successful completions lacking Rollbacks
        rollback_freq = engine_health.get("rollback_frequency", 0.0)
        precision = min(1.0, max(0.0, 1.0 - rollback_freq))
        
        # Final combined risk scalar: The higher the number, the more dangerous the Autonomy currently is.
        combined_risk = (drift_freq * 0.6) + (failure_rate * 0.4)
        risk_score = round(min(1.0, combined_risk), 3)
        
        logger.info(f"Sentinel System Dashboard generated. Autonomous Risk Exposure: {risk_score}")
        
        return SentinelRiskSchema(
             autonomy_stability_index=round(stability_idx, 3),
             drift_frequency=round(drift_freq, 3),
             execution_precision_score=round(precision, 3),
             system_risk_exposure_score=risk_score,
             shadow_mode_active=False
        )
