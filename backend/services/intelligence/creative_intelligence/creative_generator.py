"""
Creative Generator Orchestrator
===============================
Connects the generation modules: Concept -> Hook -> Script 
using the DNA derived from the Pattern Analyzer.
"""

import logging
from typing import Dict, Any, List, Optional

from .models import CreativeGoal, CreativeDNA, PatternInsight, CreativeIdea
from .concept_generator import ConceptGenerator
from .hook_generator import HookGenerator
from .script_generator import ScriptGenerator

logger = logging.getLogger(__name__)

class CreativeGeneratorCoordinator:
    """Orchestrates the physical output of new ad concepts from learned intelligence."""

    def __init__(self):
        self.concept = ConceptGenerator()
        self.hooks = HookGenerator()
        self.script = ScriptGenerator()

    async def generate_winning_creative(self, goal: CreativeGoal, insight: PatternInsight) -> Dict[str, Any]:
        """
        Takes the mathematical 'Insight' (UGC + Pain Point + Problem/Solution = +24% CTR)
        and physically hallucinates the exact video script to execute it.
        """
        logger.info(f"[CreativeGeneratorCoordinator] Assembling new creative based on Pattern Insight: {insight.performance_lift}")
        
        # 1. Map the insight back to the structural constraints
        target_dna = CreativeDNA(
             creative_id="gen_0001",
             hook_type=insight.hook,
             emotion="High Empathy",  # Generalizing from pain point
             story_pattern=insight.story,
             visual_format=insight.visual_format,
             CTA_style="Direct Offer",
             offer_type="Scale Trial"
        )
        
        # 2. Build the Concept Block
        core_concept = await self.concept.generate_concept(goal, target_dna=target_dna, pattern=insight)
        
        # 3. Spin 3 Hooks targeting that emotion
        generated_hooks = await self.hooks.generate_hooks(goal, target_dna=target_dna, pattern=insight)
        top_hook = generated_hooks[0] if generated_hooks else "Is your current logic failing?"
        
        # 4. Weave the final structural block
        idea = CreativeIdea(
            concept=core_concept,
            hook=top_hook,
            story_structure=f"Follows {target_dna.story_pattern} emphasizing the product's value proposition against {target_dna.emotion} objections.",
            CTA="Sign up today to test campaigns autonomously."
        )
        
        # 5. Output the literal transcript
        final_script = await self.script.build_script(idea, goal, target_dna=target_dna)
        
        return {
             "source_insight": insight.model_dump(),
             "concept_block": idea.model_dump(),
             "alternative_hooks": generated_hooks,
             "final_script": final_script
        }
