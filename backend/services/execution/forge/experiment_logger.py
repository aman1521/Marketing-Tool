import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperimentLogger:
    """
    Strict mapping layer transferring Forge insights to the Atlas EventLog 
    for hybrid learning model training loops.
    """

    def __init__(self, atlas_event_api_url: Optional[str] = None):
        self.atlas_url = atlas_event_api_url

    async def log_experiment_learning(self, experiment_record: Dict[str, Any], outcome_label: str, confidence: float):
        """
        Structure final learnings explicitly for the ML Training loop.
        outcome_label is usually strings like "WINNER", "LOSER", "INCONCLUSIVE".
        """
        
        payload = {
            "engine_name": "ForgeExperimentation",
            "engine_version": "v1.0",
            "experiment_id": experiment_record.get("experiment_id"),
            "hypothesis": experiment_record.get("hypothesis"),
            "variations": experiment_record.get("variations_blob"),
            "status": experiment_record.get("status"),
            "statistical_summary": experiment_record.get("statistical_summary", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "learning_label": outcome_label,
            "confidence_score": confidence
        }
        
        # In production this calls the internal EventLog router (e.g. over HTTPX to AtlasMemory)
        logger.info(f"Forge logged definitive ML Learning: [{outcome_label}] for {payload['experiment_id']} (Confidence: {confidence})")
        
        return True
