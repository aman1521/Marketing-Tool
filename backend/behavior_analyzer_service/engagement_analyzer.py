"""
Engagement Analyzer - Converts social engagement metrics into behavioral signals.
Analyzes platform-specific engagement patterns to classify content and determine emotional impact.
"""

from shared.utils.feature_library import (
    EngagementCalculator,
    EngagementFeatures,
    ContentType,
)
from backend.behavior_analyzer_service.models import (
    EngagementSignalsRequest,
    EngagementFeaturesResponse,
    ContentTypeEnum,
)


class EngagementAnalyzer:
    """
    Analyzes social media engagement metrics to understand content performance
    and audience emotional response.
    
    Signals Analyzed:
    - Watch retention: How much of content did viewers consume
    - Save rate: Content perceived as valuable for later reference
    - Share rate: Content compelling enough to amplify to others
    - Comment rate: Content engaging enough to trigger discussion
    
    Output:
    - Emotional resonance: How emotionally engaging the content is
    - Information value: How informational/educational the content is
    - Viral potential: How likely to be shared and amplified
    - Content type: Categorical classification
    """
    
    def __init__(self):
        """Initialize the engagement analyzer."""
        self.calculator = EngagementCalculator()
    
    def analyze(self, signals: EngagementSignalsRequest) -> EngagementFeaturesResponse:
        """
        Analyze engagement signals and return feature scores.
        
        Args:
            signals: EngagementSignalsRequest with platform metrics
            
        Returns:
            EngagementFeaturesResponse with calculated features and recommendation
        """
        # Calculate component scores
        emotional_resonance = self.calculator.emotional_resonance(
            save_rate=signals.save_rate,
            comment_rate=signals.comment_rate
        )
        
        information_value = self.calculator.information_value(
            watch_retention=signals.watch_retention,
            share_rate=signals.share_rate
        )
        
        viral_potential = self.calculator.viral_potential(
            share_rate=signals.share_rate,
            comment_rate=signals.comment_rate
        )
        
        # Classify content type
        content_type = self.calculator.classify_content_type(
            emotional_resonance=emotional_resonance,
            information_value=information_value,
            viral_potential=viral_potential
        )
        
        # Generate recommendation
        recommendation = self.calculator.engagement_recommendation(content_type)
        
        return EngagementFeaturesResponse(
            emotional_resonance_score=round(emotional_resonance, 4),
            information_value_score=round(information_value, 4),
            viral_potential_score=round(viral_potential, 4),
            content_type=ContentTypeEnum(content_type.value),
            recommendation=recommendation
        )
    
    def analyze_with_details(self, signals: EngagementSignalsRequest) -> dict:
        """
        Analyze engagement signals and return detailed breakdown.
        
        Includes:
        - Individual score calculations
        - Content classification reasoning
        - Platform-specific insights
        
        Args:
            signals: EngagementSignalsRequest with platform metrics
            
        Returns:
            Dictionary with detailed analysis breakdown
        """
        response = self.analyze(signals)
        
        # Calculate engagement rate
        engagement_rate = (
            signals.save_rate + signals.share_rate + signals.comment_rate
        ) / 3
        
        # Platform-specific insights
        platform_insights = self._get_platform_insights(
            signals.platform,
            response.emotional_resonance_score,
            response.information_value_score,
            response.viral_potential_score
        )
        
        return {
            "response": response.dict(),
            "engagement_rate": round(engagement_rate, 4),
            "view_count": signals.view_count,
            "platform": signals.platform,
            "platform_insights": platform_insights,
            "engagement_breakdown": {
                "watch_retention": signals.watch_retention,
                "save_rate": signals.save_rate,
                "share_rate": signals.share_rate,
                "comment_rate": signals.comment_rate
            }
        }
    
    @staticmethod
    def _get_platform_insights(
        platform: str,
        emotional_resonance: float,
        information_value: float,
        viral_potential: float
    ) -> str:
        """
        Get platform-specific insights for the content performance.
        
        Args:
            platform: Social platform name
            emotional_resonance: Emotional engagement score
            information_value: Information value score
            viral_potential: Viral potential score
            
        Returns:
            Platform-specific insight string
        """
        platform_lower = platform.lower()
        
        # TikTok insights
        if "tiktok" in platform_lower:
            if viral_potential > 0.15:
                return "High viral potential - TikTok's algorithm will amplify this"
            if emotional_resonance > 0.15:
                return "Strong emotional engagement - Consider series content"
            if information_value > 0.6:
                return "Educational content performing well - Lean into this pattern"
        
        # Instagram insights
        elif "instagram" in platform_lower:
            if emotional_resonance > 0.15:
                return "Strong save rate - Content perceived as valuable reference"
            if viral_potential < 0.1:
                return "Low share rate - Consider CTAs to increase distribution"
        
        # YouTube insights
        elif "youtube" in platform_lower:
            if information_value > 0.6:
                return "Strong watch retention - Long-form content resonates"
            if emotional_resonance < 0.1:
                return "Consider adding emotional hooks to improve engagement metrics"
        
        # LinkedIn insights
        elif "linkedin" in platform_lower:
            if information_value > 0.6:
                return "Professional content performing well - Share industry insights"
            if emotional_resonance > 0.1:
                return "Storytelling approach effective - Increase personal narratives"
        
        # Default insight
        return "Monitor performance trends to optimize content strategy"
