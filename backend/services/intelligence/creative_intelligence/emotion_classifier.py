"""
Emotion Classifier
==================
Detects the underlying psychological trigger the Ad uses to compel clicks.
Categories: fear, aspiration, curiosity, urgency, trust, excitement.
"""

import logging
from typing import Dict, Any, Optional
from .models import CreativeStructure, EmotionSignal

logger = logging.getLogger(__name__)

class EmotionClassifier:
    """Uses LLM/Zero-shot NLP to identify the core human emotion driving the CTA."""

    async def extract_emotion(self, structure: CreativeStructure) -> EmotionSignal:
        """
        Scrapes the body and hook to map to the 6 core marketing emotional drivers.
        """
        full_text = f"{structure.hook} {structure.body_message} {structure.CTA}".lower()
        
        # MOCK IMPLEMENTATION (Normally hitting BERT/OpenAI Classification)
        cat = "curiosity"
        conf = 0.50
        
        if "lose" in full_text or "waste" in full_text or "stop" in full_text:
             cat = "fear"
             conf = 0.88
        elif "exclusive" in full_text or "predict" in full_text or "secret" in full_text:
             cat = "excitement"
             conf = 0.70
        elif "today" in full_text or "limited" in full_text or "expire" in full_text:
             cat = "urgency"
             conf = 0.95
             
        # Mock logic
        return EmotionSignal(
            emotion=cat,
            confidence=conf
        )
