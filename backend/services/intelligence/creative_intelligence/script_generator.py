"""
Script Generator
================
Compiles the components (Hook, Story, Details) into a full physical 
artifact ready for video production.
"""

import os
import logging
from typing import Dict, Any, List, Optional
try:
    from openai import AsyncOpenAI
except ImportError:
    pass

from .models import CreativeGoal, CreativeIdea, CreativeDNA

logger = logging.getLogger(__name__)

class ScriptGenerator:
    """Takes all previous Generative Blocks and writes the final cohesive transcript."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-4o"  # Needs higher reasoning for narrative flow

    async def build_script(self, idea: CreativeIdea, goal: CreativeGoal, target_dna: Optional[CreativeDNA] = None) -> str:
         """
         Constructs the precise dialogue + visual directives.
         """
         logger.info(f"[ScriptGenerator] Building explicit script for '{idea.concept}'")
         
         if not self.openai_api_key:
              fallback = (
                  "Hook:\n"
                  f'"{idea.hook}"\n\n'
                  "Story:\n"
                  f"{idea.story_structure}\n\n"
                  "CTA:\n"
                  f"{idea.CTA}"
              )
              return fallback
              
         # Build Prompt
         system = (
             "You are a top 1% performance marketing scriptwriter. Your job is to take the "
             "following concept components and weave them into a 30-45 second video ad script. "
             "Format the output strictly as:\n"
             "Hook:\n[Text]\n\nStory:\n[Text]\n\nCTA:\n[Text]"
         )
         
         user = (
             f"Product: {goal.product}\n"
             f"Audience: {goal.audience}\n\n"
             "COMPONENTS TO INCLUDE:\n"
             f"- Concept: {idea.concept}\n"
             f"- Hook Variant: {idea.hook}\n"
             f"- Story Flow: {idea.story_structure}\n"
             f"- CTA Required: {idea.CTA}\n"
         )
         
         try:
              client = AsyncOpenAI(api_key=self.openai_api_key)
              res = await client.chat.completions.create(
                  model=self.model,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                  temperature=0.8
              )
              
              script = res.choices[0].message.content.strip()
              logger.debug(f"[ScriptGenerator] Ad Script successfully composed.")
              return script
              
         except Exception as e:
              logger.error(f"[ScriptGenerator] Final script generation failed: {e}")
              return f"Hook: {idea.hook}\n\nStory: {idea.concept}\n\nCTA: {idea.CTA}"
