import logging
from typing import Dict, Any, List
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperimentationFramework:
    """
    Tracks A/B testing variants, stores hypotheses, and calculates performance scores.
    """
    
    def __init__(self):
        # In memory simulation of NoSQL variant tracking
        self.experiments = {}
        
    def create_hypothesis(self, business_id: str, hypothesis_text: str, variants: List[Dict[str, Any]]) -> str:
        """
        Setup a new experiment holding variant metadata.
        """
        exp_id = str(uuid.uuid4())
        self.experiments[exp_id] = {
            "business_id": business_id,
            "hypothesis": hypothesis_text,
            "status": "active",
            "start_time": datetime.utcnow().isoformat(),
            "variants": variants,
            "results": {}
        }
        logger.info(f"Created new experiment {exp_id} for hypothesis: {hypothesis_text}")
        return exp_id
        
    def record_metrics(self, experiment_id: str, variant_id: str, performance_data: Dict[str, float]) -> bool:
        """
        Log live performance (conversions, clicks) into the active tracking variant.
        """
        if experiment_id not in self.experiments:
            logger.error(f"Experiment {experiment_id} not found.")
            return False
            
        exp = self.experiments[experiment_id]
        if "results" not in exp:
            exp["results"] = {}
            
        if variant_id not in exp["results"]:
            exp["results"][variant_id] = []
            
        exp["results"][variant_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "data": performance_data
        })
        return True

    def calculate_experiment_score(self, experiment_id: str) -> Dict[str, Any]:
        """
        Compares variant performances against Baseline (A) vs Challengers (B+).
        """
        if experiment_id not in self.experiments:
             return {"error": "Experiment not found."}
             
        exp = self.experiments[experiment_id]
        
        # Example logic: Tallying conversion_rate averages
        variant_scores = {}
        for var_id, logs in exp.get("results", {}).items():
            if not logs:
                continue
                
            # Aggregate average CVR
            cvr_sum = sum([entry["data"].get("conversion_rate", 0) for entry in logs])
            avg_cvr = cvr_sum / len(logs)
            variant_scores[var_id] = round(avg_cvr, 4)
            
        # Identify winner
        winner = None
        if variant_scores:
            winner = max(variant_scores.items(), key=lambda x: x[1])
            
        return {
            "experiment_id": experiment_id,
            "hypothesis": exp["hypothesis"],
            "variant_scores": variant_scores,
            "winner": winner[0] if winner else None,
            "winning_metric": winner[1] if winner else None,
            "status": exp["status"]
        }

    def archive_learning(self, experiment_id: str) -> Dict[str, Any]:
        """
        Close out experiment and port its data into the generic learning archive mapped for ML models.
        """
        if experiment_id in self.experiments:
            self.experiments[experiment_id]["status"] = "archived"
            self.experiments[experiment_id]["end_time"] = datetime.utcnow().isoformat()
            logger.info(f"Archived experiment {experiment_id}. Appending to ML Variant History.")
            return self.experiments[experiment_id]
        return {"error": "Not found"}
