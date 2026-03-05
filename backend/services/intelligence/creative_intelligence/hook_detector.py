"""
Hook Detector
=============
Identifies explicitly WHICH category out of (curiosity, pain_point, social_proof, 
controversial, question, story) the Hook string falls under.
"""

import logging
from typing import Dict, Any, Optional
from .models import CreativeStructure, HookType

logger = logging.getLogger(__name__)

class HookDetector:
    """Uses LLM classification to assign a vectorizable category to the first 3 seconds."""

    async def detect_type(self, structure: CreativeStructure) -> HookType:
        """
        Classifies the hook text and attaches a confidence score.
        """
        logger.debug(f"[HookDetector] Analyzing hook topology on: '{structure.hook}'")
        
        # MOCK IMPLEMENTATION (Normally hitting OpenAI Classification)
        hook_lower = structure.hook.lower()
        
        cat = "curiosity"
        conf = 0.65
        
        if "waste" in hook_lower or "problem" in hook_lower or "stop" in hook_lower:
             cat = "pain_point"
             conf = 0.90
        elif "?" in hook_lower:
             cat = "question"
             conf = 0.85
        elif "most" in hook_lower or "how to" in hook_lower:
             cat = "story"
             conf = 0.70
             
        # Mock logic
        return HookType(
            category=cat,
            confidence=conf
        )
