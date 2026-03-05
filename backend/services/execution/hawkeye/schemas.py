from pydantic import BaseModel, Field
from typing import Optional

class HawkeyeOutputSchema(BaseModel):
    """
    Standardized payload formatting the abstract vision and semantic states 
    into numerical triggers meant for AtlasMemory and Forge.
    """
    creative_id: str
    hook_strength: float = Field(ge=0.0, le=1.0)
    emotional_tone: str
    offer_clarity_score: float = Field(ge=0.0, le=1.0)
    cta_intensity_score: float = Field(ge=0.0, le=1.0)
    visual_complexity_score: float = Field(ge=0.0, le=1.0)
    fatigue_score: float = Field(ge=0.0, le=1.0)
    creative_cluster: str
    timestamp: str

class VisionMetricsSchema(BaseModel):
    composition_score: float
    text_density: float
    faces_detected: int
    motion_pacing_score: float
    visual_clutter: float
    hook_detected_in_3s: bool

class CopyMetricsSchema(BaseModel):
    readability_score: float
    urgency_detected: bool
    sentiment_polarity: float
    benefit_framing_score: float
    problem_framing_score: float
    primary_emotion: str
    offer_extracted: str

class FunnelMetricsSchema(BaseModel):
    landing_page_url: str
    above_fold_clarity: float
    cta_density: int
    trust_signals_count: int
    friction_indicators: int
    funnel_gap_score: float
