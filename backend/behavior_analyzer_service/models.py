"""
Pydantic models for behavior analyzer service.
Defines request/response schemas for all endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Enums
class ContentTypeEnum(str, Enum):
    """Content type classification."""
    INFORMATIONAL = "Informational"
    VIRAL = "Viral"
    SLOW_BURN = "Slow Burn"
    ENTERTAINMENT = "Entertainment"
    HYBRID = "Hybrid"


class IntentSegmentEnum(str, Enum):
    """Customer intent segments."""
    COLD_CURIOSITY = "Cold Curiosity"
    PROBLEM_AWARE = "Problem Aware"
    SOLUTION_AWARE = "Solution Aware"
    READY_TO_BUY = "Ready to Buy"


class OptimizationPriorityEnum(str, Enum):
    """Optimization priority levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# ==================== ENGAGEMENT ANALYSIS ====================

class EngagementSignalsRequest(BaseModel):
    """Engagement metrics from social platforms."""
    
    platform: str = Field(..., description="Social platform name")
    watch_retention: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Percentage of viewers who watched to end"
    )
    save_rate: float = Field(..., ge=0, le=1, description="Save/bookmark rate")
    share_rate: float = Field(..., ge=0, le=1, description="Share rate")
    comment_rate: float = Field(..., ge=0, le=1, description="Comment rate")
    view_count: int = Field(..., ge=0, description="Total view count")
    
    class Config:
        schema_extra = {
            "example": {
                "platform": "tiktok",
                "watch_retention": 0.70,
                "save_rate": 0.12,
                "share_rate": 0.05,
                "comment_rate": 0.08,
                "view_count": 45000
            }
        }


class EngagementFeaturesResponse(BaseModel):
    """Engagement analysis results."""
    
    emotional_resonance_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Emotional engagement strength"
    )
    information_value_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Educational/informational value"
    )
    viral_potential_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Likelihood to be shared"
    )
    content_type: ContentTypeEnum = Field(..., description="Classified content type")
    recommendation: str = Field(..., description="Strategic recommendation")
    
    class Config:
        schema_extra = {
            "example": {
                "emotional_resonance_score": 0.10,
                "information_value_score": 0.65,
                "viral_potential_score": 0.13,
                "content_type": "Informational",
                "recommendation": "Emphasize expertise and educational value"
            }
        }


# ==================== CONVERSION ANALYSIS ====================

class ConversionSignalsRequest(BaseModel):
    """Conversion funnel metrics."""
    
    add_to_cart_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Add to cart conversion rate"
    )
    checkout_abandon_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Checkout abandonment rate"
    )
    avg_product_page_time: float = Field(
        ..., 
        ge=0, 
        description="Average time on product page (seconds)"
    )
    avg_session_duration: float = Field(
        ..., 
        ge=0, 
        description="Average total session duration (seconds)"
    )
    repeat_purchase_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Percentage of repeat customers"
    )
    monthly_sessions: int = Field(default=10000, ge=1, description="Monthly session count")
    avg_order_value: float = Field(default=75.0, ge=0, description="Average order value")
    
    class Config:
        schema_extra = {
            "example": {
                "add_to_cart_rate": 0.18,
                "checkout_abandon_rate": 0.42,
                "avg_product_page_time": 187.5,
                "avg_session_duration": 245,
                "repeat_purchase_rate": 0.35,
                "monthly_sessions": 10000,
                "avg_order_value": 75.0
            }
        }


class ConversionFeaturesResponse(BaseModel):
    """Conversion analysis results."""
    
    purchase_intent_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Likelihood to purchase"
    )
    conversion_friction_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Amount of friction in funnel (higher = more friction)"
    )
    primary_friction_point: str = Field(..., description="Main conversion barrier")
    secondary_friction_point: str = Field(..., description="Secondary barrier")
    optimization_priority: OptimizationPriorityEnum = Field(
        ..., 
        description="Priority level for fixes"
    )
    estimated_monthly_revenue_loss: float = Field(
        ..., 
        ge=0, 
        description="Estimated monthly revenue loss in USD"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "purchase_intent_score": 0.138,
                "conversion_friction_score": 0.584,
                "primary_friction_point": "Checkout process too complex",
                "secondary_friction_point": "Mobile UX issues",
                "optimization_priority": "High",
                "estimated_monthly_revenue_loss": 1200.00
            }
        }


# ==================== INTENT CLASSIFICATION ====================

class IntentSignalsRequest(BaseModel):
    """Customer behavior signals for intent classification."""
    
    scroll_depth: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="How far user scrolled (0-1)"
    )
    pages_visited: float = Field(
        ..., 
        ge=0, 
        description="Average pages visited per session"
    )
    time_on_site: float = Field(
        ..., 
        ge=0, 
        description="Time on site in seconds"
    )
    has_added_to_cart: bool = Field(default=False, description="Has user added items to cart?")
    is_previous_purchaser: bool = Field(default=False, description="Is repeat customer?")
    email_opens: int = Field(default=0, ge=0, description="Email open count")
    abandoned_carts: int = Field(default=0, ge=0, description="Abandoned cart count")
    
    class Config:
        schema_extra = {
            "example": {
                "scroll_depth": 0.85,
                "pages_visited": 3.2,
                "time_on_site": 245,
                "has_added_to_cart": True,
                "is_previous_purchaser": False,
                "email_opens": 0,
                "abandoned_carts": 0
            }
        }


class IntentFeaturesResponse(BaseModel):
    """Intent classification results."""
    
    intent_segment: IntentSegmentEnum = Field(..., description="Customer intent classification")
    intent_strength: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence in segment classification"
    )
    recommended_strategy: List[str] = Field(..., description="Recommended content strategies")
    content_focus: str = Field(..., description="Primary content focus area")
    roas_potential_min: float = Field(..., ge=0, description="Minimum ROAS potential")
    roas_potential_max: float = Field(..., ge=0, description="Maximum ROAS potential")
    
    class Config:
        schema_extra = {
            "example": {
                "intent_segment": "Solution Aware",
                "intent_strength": 0.78,
                "recommended_strategy": [
                    "Product benefits focus",
                    "Social proof & testimonials",
                    "Overcome specific objections",
                    "Limited time urgency"
                ],
                "content_focus": "Conversion optimization",
                "roas_potential_min": 2.0,
                "roas_potential_max": 3.5
            }
        }


# ==================== COMBINED ANALYSIS ====================

class ComprehensiveAnalysisRequest(BaseModel):
    """Full analysis request combining all signals."""
    
    engagement: EngagementSignalsRequest
    conversion: ConversionSignalsRequest
    intent: IntentSignalsRequest


class ComprehensiveAnalysisResponse(BaseModel):
    """Full analysis combining all outputs."""
    
    engagement: EngagementFeaturesResponse
    conversion: ConversionFeaturesResponse
    intent: IntentFeaturesResponse
    combined_insight: str = Field(..., description="Overall strategic insight")
    emotional_trigger: str = Field(..., description="Primary emotional trigger")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall analysis confidence")
    next_actions: List[str] = Field(..., description="Recommended next steps")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== HEALTH CHECK ====================

class HealthResponse(BaseModel):
    """Service health status."""
    
    status: str = Field(default="healthy", description="Service status")
    service: str = Field(default="Behavior Analyzer Service", description="Service name")
    version: str = Field(default="0.1.0", description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
