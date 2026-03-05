"""
Storytelling Analyzer
=====================
Extracts the fundamental narrative schema (Problem -> Solution, Hero's Journey, etc.)
from the structural payload of the Creative.
Categories: problem_solution, hero_journey, before_after, testimonial, demo_walkthrough.
"""

import logging
from typing import Dict, Any, Optional
from .models import CreativeStructure, StoryPattern

logger = logging.getLogger(__name__)

class StorytellingAnalyzer:
    """Uses LLM logic to classify narrative patterns."""

    async def detect_pattern(self, structure: CreativeStructure) -> StoryPattern:
        """
        Scrapes the body structure to determine the narrative flow.
        """
        full_text = f"{structure.hook} {structure.body_message}".lower()
        
        # MOCK IMPLEMENTATION (Normally hitting BERT/OpenAI Classification)
        cat = "demo_walkthrough"
        conf = 0.55
        
        if "problem" in full_text or "waste" in full_text or "struggle" in full_text:
             cat = "problem_solution"
             conf = 0.82
        elif "before" in full_text or "used to" in full_text or "after" in full_text:
             cat = "before_after"
             conf = 0.90
        elif "says" in full_text or "helped me" in full_text:
             cat = "testimonial"
             conf = 0.88
             
        # Mock logic
        return StoryPattern(
            pattern_type=cat,
            confidence=conf
        )
