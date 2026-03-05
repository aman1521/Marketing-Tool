"""
Hook Generator
==============
Outputs specific copy strings targeting the first 3 seconds of attention span based upon the learned patterns.
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

class HookGenerator:
    """Takes a specific DNA classification and spits out 3-5 variants targeting the exact emotion map."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-4o-mini"

    async def generate_hooks(self, goal: CreativeGoal, target_dna: Optional[CreativeDNA] = None, pattern: Optional[PatternInsight] = None) -> List[str]:
         """
         If we know 'fear + software_demo' works best, generate specific strings hitting those signals.
         """
         logger.info(f"[HookGenerator] Generating {target_dna.hook_type if target_dna else 'standard'} hooks for {goal.product}")
         
         if not self.openai_api_key:
              return [
                  "Most marketers waste 80% of their ad budget",
                  "We simulated 10 campaigns before spending $1",
                  "What if your ads could predict performance?"
              ]
              
         # Build Prompt
         system = (
             "You are an expert Direct Response Copywriter. Generate exactly 3 variants "
             "for the first 3 seconds (the hook) of a video ad."
         )
         
         user = (
             f"Product: {goal.product}\n"
             f"Audience: {goal.audience}\n"
             f"Hook Emotion: {target_dna.emotion if target_dna else 'High Empathy'}\n"
             f"Hook Category: {target_dna.hook_type if target_dna else 'Problem'}\n\n"
             "Return exactly 3 numbered bullet points. Nothing else."
         )
         
         try:
              client = AsyncOpenAI(api_key=self.openai_api_key)
              res = await client.chat.completions.create(
                  model=self.model,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                  temperature=0.7
              )
              
              lines = res.choices[0].message.content.strip().split('\n')
              hooks = [h.strip() for h in lines if h.strip()]
              logger.debug(f"[HookGenerator] Generated {len(hooks)} variants.")
              return hooks
              
         except Exception as e:
              logger.error(f"[HookGenerator] LLM Generation Failed: {e}")
              return ["Are you struggling with ad fatigue? Watch this."]
