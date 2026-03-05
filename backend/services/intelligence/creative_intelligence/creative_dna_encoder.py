"""
Creative DNA Encoder
====================
Fuses the outputs of the Parser, Hook Detector, Emotion Classifier, and 
Story Analyzer into a singular, indexable 'CreativeDNA' object.
"""

import logging
from typing import Dict, Any, Optional

from .models import Creative, CreativeStructure, HookType, EmotionSignal, StoryPattern, CreativeDNA
from .creative_parser import CreativeParser
from .hook_detector import HookDetector
from .emotion_classifier import EmotionClassifier
from .storytelling_analyzer import StorytellingAnalyzer

logger = logging.getLogger(__name__)

class CreativeDNAEncoder:
    """The central assembly pipeline that extracts a creative's genetic makeup."""

    def __init__(self):
        self.parser = CreativeParser()
        self.hook_detector = HookDetector()
        self.emotion_classifier = EmotionClassifier()
        self.story_analyzer = StorytellingAnalyzer()

    async def encode(self, creative: Creative) -> CreativeDNA:
        """
        Runs the full extraction pipeline over a raw creative and returns its DNA.
        """
        logger.info(f"[CreativeDNAEncoder] Sequencing genetic map for {creative.id}...")
        
        # 1. Break ad into parts
        structure: CreativeStructure = await self.parser.parse_structure(creative)
        
        # 2. Extract specific psychological markers
        hook_category: HookType = await self.hook_detector.detect_type(structure)
        emotion: EmotionSignal = await self.emotion_classifier.extract_emotion(structure)
        story: StoryPattern = await self.story_analyzer.detect_pattern(structure)
        
        # 3. Assemble the Genome
        dna = CreativeDNA(
            creative_id=creative.id,
            hook_type=hook_category.category,
            emotion=emotion.emotion,
            story_pattern=story.pattern_type,
            visual_format=creative.visual_type or "unknown_format",
            CTA_style=structure.CTA, # Usually normalized in a real system (direct, soft, query)
            offer_type=structure.offer or "standard_offer"
        )
        
        logger.debug(f"[CreativeDNAEncoder] Genome sequenced: {dna.hook_type} -> {dna.story_pattern} -> {dna.emotion}")
        
        return dna
