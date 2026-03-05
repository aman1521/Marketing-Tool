"""
Creative Intelligence Engine Models
===================================
Data structures representing raw Ad creatives, extracted structural markers, 
Creative DNA encodings, and textual generative outputs.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Creative(BaseModel):
    """Raw collected ad data."""
    id: str
    platform: str
    ad_text: str
    headline: Optional[str] = None
    visual_type: Optional[str] = None
    video_url: Optional[str] = None
    landing_page_url: Optional[str] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

class CreativeStructure(BaseModel):
    """Parsed fundamental blocks of a creative."""
    hook: str
    body_message: str
    CTA: str
    offer: Optional[str] = None

class HookType(BaseModel):
    """Classification of the first 3 seconds / top line."""
    category: str  # curiosity, pain_point, social_proof, controversial, question, story
    confidence: float = Field(ge=0.0, le=1.0)

class EmotionSignal(BaseModel):
    """Psychological trigger classification."""
    emotion: str  # fear, aspiration, curiosity, urgency, trust, excitement
    confidence: float = Field(ge=0.0, le=1.0)

class StoryPattern(BaseModel):
    """The overarching narrative flow."""
    pattern_type: str  # problem_solution, hero_journey, before_after, testimonial, demo_walkthrough
    confidence: float = Field(ge=0.0, le=1.0)

class CreativeDNA(BaseModel):
    """The definitive genetic encoding of an ad's strategy."""
    creative_id: str
    hook_type: str
    emotion: str
    story_pattern: str
    visual_format: str
    CTA_style: str
    offer_type: str

class PatternInsight(BaseModel):
    """A mathematically proven combination of Creative DNA variables."""
    visual_format: str
    hook: str
    story: str
    performance_lift: str
    insight_reasoning: str

class CreativeGoal(BaseModel):
    """Inputs to the generative engine."""
    product: str
    audience: str
    platform: str
    additional_context: Optional[str] = None

class CreativeIdea(BaseModel):
    """A generalized concept block."""
    concept: str
    hook: str
    story_structure: str
    CTA: str

class CreativeInsightLog(BaseModel):
    """Persistence model tracking performance of explicit Creative DNAs."""
    creative_dna: Dict[str, str]
    performance_metrics: Dict[str, Any]
    industry: str
