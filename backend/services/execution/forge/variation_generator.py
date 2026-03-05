import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class VariationGenerator:
    """
    Given a diagnosis context, automatically maps hypotheses and structures variations
    applicable to CaptainExecute payload schemas.
    """

    def generate_variations(self, diagnosis_state: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets CaptainDiagnose outputs and produces a structured A/B/n test matrix.
        """
        
        # Base structured definition
        experiment = {
             "hypothesis": f"Undefined for {diagnosis_state}",
             "experiment_type": "UNKNOWN",
             "variations": {}
        }

        # Rules Engine generating variations deterministically based on Dark Matter outputs
        if diagnosis_state == "CREATIVE_FATIGUE":
             experiment["experiment_type"] = "CREATIVE_ANGLE_SHIFT"
             experiment["hypothesis"] = "Refreshing the visual hook while maintaining standard copy will invert audience decay rates."
             experiment["variations"] = {
                 "control": {"copy": "baseline", "creative_asset": "historical_best_performer"},
                 "variation_1": {"copy": "baseline", "creative_asset": "new_hook_angle_a"},
                 "variation_2": {"copy": "baseline", "creative_asset": "new_hook_angle_b"}
             }
             logger.info(f"Forge variation engine prescribed CREATIVE_ANGLE_SHIFT for {diagnosis_state}")

        elif diagnosis_state == "SCALING_OPPORTUNITY":
             experiment["experiment_type"] = "AUDIENCE_EXPANSION"
             experiment["hypothesis"] = "Expanding lookalike percentage limits mathematically preserves ROAS during accelerated budget ingest."
             experiment["variations"] = {
                 "control": {"audience_type": "1%_LAL", "bidding": "target_cpa"},
                 "variation_1": {"audience_type": "3%_LAL", "bidding": "target_cpa"},
                 "variation_2": {"audience_type": "broad_open", "bidding": "lowest_cost"}
             }
             logger.info(f"Forge variation engine prescribed AUDIENCE_EXPANSION for {diagnosis_state}")
             
        elif diagnosis_state == "CONVERSION_PROBLEM":
             experiment["experiment_type"] = "LANDING_PAGE_VARIATION"
             experiment["hypothesis"] = "Minimizing checkout stages from 3 to 1 will reduce bottom-funnel abandonment."
             experiment["variations"] = {
                 "control": {"destination_url": "baseline_funnel", "page_layout": "standard"},
                 "variation_1": {"destination_url": "exp_funnel_1_step", "page_layout": "optimized_checkout"}
             }
             logger.info(f"Forge variation engine prescribed LANDING_PAGE_VARIATION for {diagnosis_state}")
             
        else:
             experiment["experiment_type"] = "BUDGET_SPLIT_TEST"
             experiment["hypothesis"] = f"Generic optimization split for baseline {diagnosis_state}"
             experiment["variations"] = {
                 "control": {"budget_modifier": 1.0},
                 "variation_1": {"budget_modifier": 1.1}
             }
             logger.info(f"Forge variation engine fell back to generic BUDGET_SPLIT_TEST for {diagnosis_state}")
             
        return experiment
