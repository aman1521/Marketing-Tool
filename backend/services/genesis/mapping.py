from typing import Dict, Any
import logging

from backend.services.genesis.schemas import GenesisProfileSchema

logger = logging.getLogger(__name__)

class GenesisMapping:
    """
    Evaluates business context strictly for mapping arrays into the intelligence
    clusters located in Atlas.
    """

    def generate_mapping(self, profile: GenesisProfileSchema) -> Dict[str, Any]:
        """
        Derives benchmark clusters mathematically based on configured margins, AOV, and budgets.
        """
        
        # 1. Benchmark Cluster Assignment
        # (Combines exact industry logic and AOV segments for Atlas retrieval)
        tier = "High" if profile.aov > 150 else ("Med" if profile.aov > 50 else "Low")
        benchmark_cluster = f"{profile.industry}_{tier}_AOV"

        # 2. Risk Cluster Classification
        # (Lower margins mathematically generate tighter risk tolerances)
        if profile.gross_margin < 0.3:
            risk_cluster = "Conservative"
        elif profile.gross_margin > 0.6:
            risk_cluster = "Tolerant"
        else:
            risk_cluster = "Standard"

        # 3. Aggression Tier Assignment
        # Map budget firepower to systematic aggressive testing limits
        aggression_tier = "Moderate"
        if profile.budget_tier in ["mid", "ent"] and profile.growth_stage == "scaling":
            aggression_tier = "Aggressive"
            
        # 4. Maturity Level
        maturity_level = profile.growth_stage

        logger.info(f"Generated Genesis Intelligence Mapping. Cluster: {benchmark_cluster}, Risk: {risk_cluster}")

        return {
            "benchmark_cluster": benchmark_cluster,
            "risk_cluster": risk_cluster,
            "aggression_tier": aggression_tier,
            "maturity_level": maturity_level
        }
