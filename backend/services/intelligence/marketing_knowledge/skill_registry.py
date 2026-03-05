"""
Skill Registry
==============
A central directory mapping human-readable skill names to their structural capabilities.
Agents use this registry to know what plays exist before querying the Retrieval Engine.
"""

from typing import Dict, List
import logging

from .models import SkillRegistryItem

logger = logging.getLogger(__name__)

class SkillRegistry:
    """Pre-maps the universe of capabilities within the Marketing Knowledge Engine."""
    
    def __init__(self):
        self._skills: Dict[str, SkillRegistryItem] = {
            "cro_analysis": SkillRegistryItem(
                name="CRO Analysis",
                description="Framework for finding friction on landing pages and checkout flows.",
                skill_type="conversion",
                input_requirements=["url_or_page_content", "dropoff_metrics"],
                output_format="problem, recommendation, expected_conversion_lift"
            ),
            "copywriting_frameworks": SkillRegistryItem(
                name="Copywriting Frameworks",
                description="Psychological structures (PAS, AIDA) to rewrite saturated ad angles.",
                skill_type="creative",
                input_requirements=["current_saturated_copy", "audience_pain_point"],
                output_format="new_variants_using_framework"
            ),
            "seo_strategy": SkillRegistryItem(
                name="SEO Strategy",
                description="Organic keyword targeting and technical structural plays.",
                skill_type="organic_growth",
                input_requirements=["current_domain_authority", "top_performers"],
                output_format="prioritized_keyword_targets, new_cluster_topics"
            ),
            "growth_experiments": SkillRegistryItem(
                name="Growth Experiments",
                description="Structured Hypothesis generation for A/B split testing.",
                skill_type="experimentation",
                input_requirements=["current_metric_baseline", "proposed_change_idea"],
                output_format="formalized_hypothesis, metrics_to_track"
            ),
            "analytics_setup": SkillRegistryItem(
                name="Analytics Setup",
                description="Data layer tracking and pixel schemas for attribution fidelity.",
                skill_type="data_engineering",
                input_requirements=["funnel_stages", "current_platform_stack"],
                output_format="tracking_architecture_diagram, event_schemas"
            ),
            "engineering_marketing": SkillRegistryItem(
                name="Engineering as Marketing",
                description="Building free mini-tools to passively capture leads at scale.",
                skill_type="product_led_growth",
                input_requirements=["core_persona_pain_point", "development_bandwidth"],
                output_format="mini_tool_concept, gating_strategy"
            ),
            "marketing_ideas": SkillRegistryItem(
                name="Marketing Ideas",
                description="Breakthrough ideation frameworks for saturated channels.",
                skill_type="creative",
                input_requirements=["current_blocked_metric", "industry"],
                output_format="lateral_campaign_idea, anti_goal_fixes"
            )
        }

    def get_all_skills(self) -> List[SkillRegistryItem]:
        """Returns the complete list of available AI playbooks."""
        return list(self._skills.values())

    def get_skill(self, name: str) -> SkillRegistryItem:
        """Retrieves exact metadata for a playbook."""
        if name not in self._skills:
            logger.warning(f"Skill '{name}' not found in registry.")
            return None
        return self._skills[name]
