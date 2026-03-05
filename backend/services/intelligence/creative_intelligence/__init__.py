"""
Creative Intelligence Engine
============================
Transforms raw visual/textual creative assets into structured DNA patterns.
Applies mathematical performance discovery to reverse engineer high CPA ad metrics
into dynamically generated high-throughput scripts and video concepts.
"""
from .models import (
    Creative, CreativeStructure, HookType, EmotionSignal, StoryPattern,
    CreativeDNA, PatternInsight, CreativeGoal, CreativeIdea, CreativeInsightLog
)
from .creative_collector import CreativeCollector
from .creative_parser import CreativeParser
from .hook_detector import HookDetector
from .emotion_classifier import EmotionClassifier
from .storytelling_analyzer import StorytellingAnalyzer
from .creative_dna_encoder import CreativeDNAEncoder
from .pattern_analyzer import PatternAnalyzer
from .creative_embeddings import CreativeEmbeddings

from .concept_generator import ConceptGenerator
from .hook_generator import HookGenerator
from .script_generator import ScriptGenerator
from .creative_generator import CreativeGeneratorCoordinator

__all__ = [
    "Creative",
    "CreativeStructure",
    "HookType",
    "EmotionSignal",
    "StoryPattern",
    "CreativeDNA",
    "PatternInsight",
    "CreativeGoal",
    "CreativeIdea",
    "CreativeInsightLog",
    "CreativeCollector",
    "CreativeParser",
    "HookDetector",
    "EmotionClassifier",
    "StorytellingAnalyzer",
    "CreativeDNAEncoder",
    "PatternAnalyzer",
    "CreativeEmbeddings",
    "ConceptGenerator",
    "HookGenerator",
    "ScriptGenerator",
    "CreativeGeneratorCoordinator"
]
