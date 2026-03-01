"""
Shared feature calculation library.
Provides reusable feature engineering utilities for all services.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class ContentType(str, Enum):
    """Content type classification."""
    INFORMATIONAL = "Informational"
    VIRAL = "Viral"
    SLOW_BURN = "Slow Burn"
    ENTERTAINMENT = "Entertainment"
    HYBRID = "Hybrid"


class IntentSegment(str, Enum):
    """Customer intent segments."""
    COLD_CURIOSITY = "Cold Curiosity"
    PROBLEM_AWARE = "Problem Aware"
    SOLUTION_AWARE = "Solution Aware"
    READY_TO_BUY = "Ready to Buy"


@dataclass
class EngagementFeatures:
    """Engagement analysis output."""
    emotional_resonance_score: float
    information_value_score: float
    viral_potential_score: float
    content_type: ContentType
    recommendation: str


@dataclass
class ConversionFeatures:
    """Conversion analysis output."""
    purchase_intent_score: float
    conversion_friction_score: float
    primary_friction_point: str
    secondary_friction_point: str
    optimization_priority: str
    estimated_monthly_revenue_loss: float


@dataclass
class IntentFeatures:
    """Intent classification output."""
    intent_segment: IntentSegment
    intent_strength: float
    recommended_strategy: list
    content_focus: str


class FeatureCalculator:
    """Core feature calculation utilities."""

    @staticmethod
    def normalize_score(value: float, min_val: float = 0, max_val: float = 1) -> float:
        """Normalize a value to 0-1 range."""
        if min_val >= max_val:
            return 0.0
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))

    @staticmethod
    def weighted_average(values: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted average of values."""
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(values[key] * weights[key] for key in values if key in weights)
        return weighted_sum / total_weight

    @staticmethod
    def clamp(value: float, min_val: float = 0, max_val: float = 1) -> float:
        """Clamp value between min and max."""
        return max(min_val, min(max_val, value))


class EngagementCalculator:
    """Engagement feature calculations."""

    @staticmethod
    def emotional_resonance(save_rate: float, comment_rate: float) -> float:
        """
        Calculate emotional resonance from saves and comments.
        Higher = more emotional engagement.
        """
        return (save_rate + comment_rate) / 2

    @staticmethod
    def information_value(watch_retention: float, share_rate: float) -> float:
        """
        Calculate information value from watch time and shares.
        High watch time - low shares = informational.
        """
        return FeatureCalculator.clamp(watch_retention - share_rate)

    @staticmethod
    def viral_potential(share_rate: float, comment_rate: float) -> float:
        """
        Calculate viral potential from shares and comments.
        Multiplier indicates viral amplification.
        """
        base_potential = (share_rate + comment_rate) * 10
        return FeatureCalculator.clamp(base_potential)

    @staticmethod
    def classify_content_type(
        emotional_resonance: float,
        information_value: float,
        viral_potential: float
    ) -> ContentType:
        """
        Classify content based on engagement signals.
        """
        # High saves + comments, high watch, low shares = Informational
        if information_value > 0.6 and emotional_resonance > 0.1:
            return ContentType.INFORMATIONAL
        
        # High shares + comments = Viral
        if viral_potential > 0.15:
            return ContentType.VIRAL
        
        # High retention only = Slow Burn
        if information_value > 0.6 and viral_potential < 0.1:
            return ContentType.SLOW_BURN
        
        # All moderate = Entertainment
        if 0.3 <= information_value <= 0.7 and 0.05 <= viral_potential <= 0.15:
            return ContentType.ENTERTAINMENT
        
        return ContentType.HYBRID

    @staticmethod
    def engagement_recommendation(content_type: ContentType) -> str:
        """Generate recommendation based on content type."""
        recommendations = {
            ContentType.INFORMATIONAL: "Emphasize expertise and educational value",
            ContentType.VIRAL: "Focus on shareability and emotional hooks",
            ContentType.SLOW_BURN: "Build trust through consistency and quality",
            ContentType.ENTERTAINMENT: "Maintain entertainment value with subtle CTAs",
            ContentType.HYBRID: "Balance education with entertainment appeal",
        }
        return recommendations.get(content_type, "Analyze performance trends")


class ConversionCalculator:
    """Conversion feature calculations."""

    @staticmethod
    def purchase_intent(add_to_cart_rate: float, avg_page_time: float, avg_session_duration: float) -> float:
        """
        Calculate purchase intent score.
        Combines cart activity with engagement depth.
        """
        if avg_session_duration == 0:
            return 0.0
        
        engagement_ratio = FeatureCalculator.normalize_score(
            avg_page_time / avg_session_duration,
            min_val=0,
            max_val=1
        )
        return add_to_cart_rate * engagement_ratio

    @staticmethod
    def conversion_friction(checkout_abandon_rate: float, add_to_cart_rate: float) -> float:
        """
        Calculate conversion friction score.
        Higher score = more friction.
        """
        if add_to_cart_rate == 0:
            return 0.0
        
        conversion_rate = 1 - checkout_abandon_rate
        expected_conversion = min(add_to_cart_rate * 0.5, 0.25)  # Expect ~50% conversion
        
        friction = 1 - (conversion_rate / max(expected_conversion, 0.01))
        return FeatureCalculator.clamp(friction)

    @staticmethod
    def identify_friction_points(
        checkout_abandon_rate: float,
        avg_product_page_time: float,
        avg_session_duration: float
    ) -> tuple:
        """
        Identify primary and secondary friction points.
        """
        primary = "Checkout process too complex"
        secondary = "Mobile UX issues"
        
        if checkout_abandon_rate > 0.5:
            primary = "Checkout process too complex"
            secondary = "Payment options limited"
        elif avg_product_page_time < 100:
            primary = "Product pages lack information"
            secondary = "Insufficient product images/videos"
        elif avg_session_duration < 180:
            primary = "Navigation confusing"
            secondary = "Product discovery difficult"
        
        return primary, secondary

    @staticmethod
    def optimization_priority(friction_score: float) -> str:
        """Determine optimization priority based on friction."""
        if friction_score > 0.7:
            return "Critical"
        elif friction_score > 0.5:
            return "High"
        elif friction_score > 0.3:
            return "Medium"
        return "Low"

    @staticmethod
    def estimated_revenue_loss(
        checkout_abandon_rate: float,
        add_to_cart_rate: float,
        monthly_sessions: int = 10000,
        avg_order_value: float = 75.0
    ) -> float:
        """
        Estimate monthly revenue loss from checkout abandonment.
        """
        potential_conversion = add_to_cart_rate * monthly_sessions
        actual_conversion = potential_conversion * (1 - checkout_abandon_rate)
        lost_conversion = potential_conversion - actual_conversion
        return lost_conversion * avg_order_value


class IntentCalculator:
    """Intent classification calculations."""

    @staticmethod
    def calculate_intent_strength(
        scroll_depth: float,
        pages_visited: float,
        time_on_site: float,
        has_added_to_cart: bool = False
    ) -> float:
        """
        Calculate overall intent strength score.
        """
        # Normalize different metrics
        scroll_component = scroll_depth
        pages_component = FeatureCalculator.normalize_score(pages_visited, 0, 5)
        time_component = FeatureCalculator.normalize_score(time_on_site, 0, 600)
        
        cart_bonus = 0.2 if has_added_to_cart else 0
        
        base_strength = (scroll_component + pages_component + time_component) / 3
        return FeatureCalculator.clamp(base_strength + cart_bonus)

    @staticmethod
    def classify_intent(
        intent_strength: float,
        pages_visited: float,
        has_added_to_cart: bool,
        is_previous_purchaser: bool,
        email_opens: int = 0,
        abandoned_carts: int = 0
    ) -> IntentSegment:
        """
        Classify customer into one of 4 intent segments.
        """
        # Ready to Buy: High intent + cart activity + previous purchase
        if is_previous_purchaser and (has_added_to_cart or abandoned_carts > 0):
            if intent_strength > 0.5:
                return IntentSegment.READY_TO_BUY
        
        # Solution Aware: Cart adds + good engagement
        if has_added_to_cart or abandoned_carts > 0:
            if intent_strength > 0.4:
                return IntentSegment.SOLUTION_AWARE
        
        # Problem Aware: Research behavior (multiple pages, good time spent)
        if pages_visited > 2.5 and intent_strength > 0.5:
            return IntentSegment.PROBLEM_AWARE
        
        # Cold Curiosity: Default for low engagement
        return IntentSegment.COLD_CURIOSITY

    @staticmethod
    def get_recommended_strategy(intent_segment: IntentSegment) -> list:
        """Get recommended content strategy for segment."""
        strategies = {
            IntentSegment.COLD_CURIOSITY: [
                "Brand awareness content",
                "Top-of-funnel education",
                "Emotional hooks",
                "Low-commitment engagement"
            ],
            IntentSegment.PROBLEM_AWARE: [
                "Problem validation",
                "Comparison content",
                "Educational resources",
                "Industry insights"
            ],
            IntentSegment.SOLUTION_AWARE: [
                "Product benefits focus",
                "Social proof & testimonials",
                "Overcome objections",
                "Limited time urgency"
            ],
            IntentSegment.READY_TO_BUY: [
                "Special offers & incentives",
                "Urgency & scarcity",
                "Money-back guarantee",
                "Quick checkout experience"
            ],
        }
        return strategies.get(intent_segment, [])

    @staticmethod
    def get_content_focus(intent_segment: IntentSegment) -> str:
        """Get primary content focus for segment."""
        focus_map = {
            IntentSegment.COLD_CURIOSITY: "Awareness & education",
            IntentSegment.PROBLEM_AWARE: "Problem understanding & comparison",
            IntentSegment.SOLUTION_AWARE: "Conversion optimization",
            IntentSegment.READY_TO_BUY: "Transaction & loyalty",
        }
        return focus_map.get(intent_segment, "General engagement")

    @staticmethod
    def get_roas_potential_range(intent_segment: IntentSegment) -> tuple:
        """Get expected ROAS range for segment."""
        ranges = {
            IntentSegment.COLD_CURIOSITY: (0.5, 1.0),
            IntentSegment.PROBLEM_AWARE: (1.0, 1.5),
            IntentSegment.SOLUTION_AWARE: (2.0, 3.5),
            IntentSegment.READY_TO_BUY: (3.5, 5.0),
        }
        return ranges.get(intent_segment, (0.0, 1.0))
