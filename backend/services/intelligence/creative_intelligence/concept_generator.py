"""
Concept Generator
=================
Synthesizes broad angles into the singular physical concept for execution.
Example: 'A UGC-style ad showing a marketer discovering that AI can simulate campaigns.'
"""

import os
import logging
from typing import Dict, Any, List, Optional
try:
    from openai import AsyncOpenAI
except ImportError:
    pass

from .models import CreativeGoal, CreativeDNA, PatternInsight

logger = logging.getLogger(__name__)

class ConceptGenerator:
    """Takes a CreativeDNA seed and constructs a textual narrative description."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-4o-mini"

    async def generate_concept(self, goal: CreativeGoal, target_dna: Optional[CreativeDNA] = None, pattern: Optional[PatternInsight] = None) -> str:
         """
         Constructs the core creative intent bridging the genetic markers.
         """
         logger.info(f"[ConceptGenerator] Brainstorming concepts for {goal.product} on {goal.platform}")
         
         if not self.openai_api_key:
              return f"Concept: An organic {target_dna.visual_format if target_dna else 'video'} highlighting {goal.audience} {target_dna.emotion if target_dna else 'pain points'} with a {target_dna.hook_type if target_dna else 'strong'} hook."
              
         # Build Prompt
         system = (
             "You are a Senior Creative Director designing high-converting performance ads. "
             "Your goal is to synthesize the provided genetic constraints into a one-sentence "
             "physical concept for video production."
         )
         
         user = (
             f"Product: {goal.product}\n"
             f"Audience: {goal.audience}\n"
             f"Target Format: {target_dna.visual_format if target_dna else 'Anything high-performing'}\n"
             f"Hook Emotion: {target_dna.emotion if target_dna else 'High Empathy'}\n"
             f"Narrative: {target_dna.story_pattern if target_dna else 'Problem/Solution'}\n\n"
             "Describe the video concept in exactly one vivid sentence."
         )
         
         try:
              client = AsyncOpenAI(api_key=self.openai_api_key)
              res = await client.chat.completions.create(
                  model=self.model,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                  temperature=0.7
              )
              concept = res.choices[0].message.content.strip()
              logger.debug(f"[ConceptGenerator] Generated: {concept}")
              return concept
         except Exception as e:
              logger.error(f"[ConceptGenerator] LLM Concept Generation Failed: {e}")
              return f"Concept: An organic {target_dna.visual_format if target_dna else 'video'} for {goal.audience}."
