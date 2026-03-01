from .base_model import MLModel
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BudgetOptimizationModel(MLModel):
    """
    Budget Optimization using a variant of Multi-Armed Bandit (Epsilon-Greedy approach).
    Reallocates budgets between campaigns dynamically to maximize total predicted ROAS.
    """

    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="budget_optimization", version=version)
        self.epsilon = 0.1 # 10% exploring, 90% exploiting
        self.campaign_history = {} # Tracks historical success of campaigns
        self.is_trained = True # Deterministic logic + slight randomness, doesn't require traditional ML fit

    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Updates the internal historical tracking for epsilon-greedy allocations.
        Required columns: 'campaign_id', 'spend', 'revenue'
        """
        if 'campaign_id' in data.columns and 'spend' in data.columns and 'revenue' in data.columns:
            for idx, row in data.iterrows():
                cid = row['campaign_id']
                spend = row['spend']
                revenue = row['revenue']
                
                if cid not in self.campaign_history:
                    self.campaign_history[cid] = {'trials': 0, 'successes': 0.0}
                    
                self.campaign_history[cid]['trials'] += spend
                self.campaign_history[cid]['successes'] += revenue
                
            self.save()
            return {"status": "success", "history_size": len(self.campaign_history)}
        return {"status": "error", "message": "Missing necessary columns"}

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates budget allocation recommendations.
        features should contain:
        - total_budget: float
        - campaigns: List of Dict { "id": str, "current_budget": float, "predicted_roas": float }
        """
        total_budget = float(features.get('total_budget', 1000.0))
        campaigns = features.get('campaigns', [])
        
        if not campaigns:
            return {"allocations": {}}
            
        # Exploit vs Explore calculation
        allocations = {}
        explore_budget = total_budget * self.epsilon
        exploit_budget = total_budget - explore_budget
        
        # EXPLORE (evenly distribute remaining epsilon pool among all candidates)
        base_explore_split = explore_budget / len(campaigns)
        for camp in campaigns:
            allocations[camp['id']] = base_explore_split
            
        # EXPLOIT (proportionally distribute the majority pool to the best predicted performers)
        # We only assign exploit budget to campaigns with expected ROAS > 1.0 (profitable)
        profitable_campaigns = [c for c in campaigns if c.get('predicted_roas', 0) > 1.0]
        
        if profitable_campaigns:
            total_predicted_roas = sum([c['predicted_roas'] for c in profitable_campaigns])
            
            for camp in profitable_campaigns:
                share = camp['predicted_roas'] / total_predicted_roas
                allocations[camp['id']] += (exploit_budget * share)
        else:
            # If nothing is profitable, distribute evenly
            base_split = exploit_budget / len(campaigns)
            for camp in campaigns:
                allocations[camp['id']] += base_split
                
        # Round final budgets
        allocations = {k: round(v, 2) for k, v in allocations.items()}
        
        return {
            "allocations": allocations,
            "strategy": f"Epsilon-greedy (epsilon={self.epsilon})"
        }
