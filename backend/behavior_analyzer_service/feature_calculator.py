"""
Feature Calculator - Aggregates all analyses into comprehensive insights.
Combines engagement, conversion, and intent analysis for strategic decision-making.
"""

from backend.behavior_analyzer_service.models import (
    ComprehensiveAnalysisRequest,
    ComprehensiveAnalysisResponse,
    EngagementSignalsRequest,
    ConversionSignalsRequest,
    IntentSignalsRequest,
)
from backend.behavior_analyzer_service.engagement_analyzer import EngagementAnalyzer
from backend.behavior_analyzer_service.conversion_analyzer import ConversionAnalyzer
from backend.behavior_analyzer_service.intent_classifier import IntentClassifier


class FeatureCalculator:
    """
    Aggregates engagement, conversion, and intent analyses into a comprehensive
    intelligence report for strategic marketing decisions.
    
    Creates a unified view of:
    - What content resonates emotionally
    - Where conversion funnels leak
    - What purchase intent signals indicate
    - How to optimize marketing strategy
    """
    
    def __init__(self):
        """Initialize all analyzers."""
        self.engagement_analyzer = EngagementAnalyzer()
        self.conversion_analyzer = ConversionAnalyzer()
        self.intent_classifier = IntentClassifier()
    
    def analyze_comprehensive(
        self,
        engagement: EngagementSignalsRequest,
        conversion: ConversionSignalsRequest,
        intent: IntentSignalsRequest
    ) -> ComprehensiveAnalysisResponse:
        """
        Perform comprehensive analysis combining all three dimensions.
        
        Args:
            engagement: Engagement metrics from social platforms
            conversion: Conversion funnel metrics
            intent: Customer behavior signals
            
        Returns:
            ComprehensiveAnalysisResponse with unified insights
        """
        # Analyze each dimension
        engagement_result = self.engagement_analyzer.analyze(engagement)
        conversion_result = self.conversion_analyzer.analyze(conversion)
        intent_result = self.intent_classifier.classify(intent)
        
        # Generate combined insights
        combined_insight = self._generate_combined_insight(
            engagement=engagement_result,
            conversion=conversion_result,
            intent=intent_result
        )
        
        # Identify emotional trigger
        emotional_trigger = self._identify_emotional_trigger(
            content_type=engagement_result.content_type,
            emotional_resonance=engagement_result.emotional_resonance_score
        )
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(
            engagement=engagement_result,
            conversion=conversion_result,
            intent=intent_result
        )
        
        # Generate next actions
        next_actions = self._generate_next_actions(
            engagement=engagement_result,
            conversion=conversion_result,
            intent=intent_result
        )
        
        return ComprehensiveAnalysisResponse(
            engagement=engagement_result,
            conversion=conversion_result,
            intent=intent_result,
            combined_insight=combined_insight,
            emotional_trigger=emotional_trigger,
            confidence_score=confidence_score,
            next_actions=next_actions
        )
    
    def analyze_comprehensive_with_details(
        self,
        engagement: EngagementSignalsRequest,
        conversion: ConversionSignalsRequest,
        intent: IntentSignalsRequest
    ) -> dict:
        """
        Perform comprehensive analysis with detailed breakdowns.
        
        Args:
            engagement: Engagement metrics
            conversion: Conversion metrics
            intent: Intent signals
            
        Returns:
            Dictionary with full analysis details
        """
        # Get responses
        response = self.analyze_comprehensive(engagement, conversion, intent)
        
        # Get detailed analysis from each analyzer
        engagement_details = self.engagement_analyzer.analyze_with_details(engagement)
        conversion_details = self.conversion_analyzer.analyze_with_details(conversion)
        intent_details = self.intent_classifier.classify_with_details(intent)
        
        # Strategic recommendations
        strategic_recommendations = self._generate_strategic_recommendations(
            engagement=response.engagement,
            conversion=response.conversion,
            intent=response.intent
        )
        
        # Segment positioning
        segment_positioning = self._generate_segment_positioning(
            intent_segment=response.intent.intent_segment.value,
            emotional_trigger=response.emotional_trigger,
            revenue_loss=response.conversion.estimated_monthly_revenue_loss
        )
        
        # Implementation roadmap
        implementation_roadmap = self._generate_implementation_roadmap(
            conversion_priority=response.conversion.optimization_priority.value,
            intent_strength=response.intent.intent_strength,
            confidence=response.confidence_score
        )
        
        return {
            "comprehensive_response": response.dict(),
            "engagement_details": engagement_details,
            "conversion_details": conversion_details,
            "intent_details": intent_details,
            "strategic_recommendations": strategic_recommendations,
            "segment_positioning": segment_positioning,
            "implementation_roadmap": implementation_roadmap,
            "critical_insights": self._highlight_critical_insights(
                response=response,
                engagement_details=engagement_details,
                conversion_details=conversion_details
            )
        }
    
    @staticmethod
    def _generate_combined_insight(
        engagement,
        conversion,
        intent
    ) -> str:
        """
        Generate a single comprehensive insight statement.
        
        Args:
            engagement: Engagement analysis result
            conversion: Conversion analysis result
            intent: Intent classification result
            
        Returns:
            Single insight statement combining all dimensions
        """
        intent_segment = intent.intent_segment.value
        friction = conversion.conversion_friction_score
        emotional = engagement.emotional_resonance_score
        
        # Build insight based on all factors
        parts = []
        
        # Intent part
        if intent_segment == "Ready to Buy":
            parts.append(f"Ready-to-buy customer")
        elif intent_segment == "Solution Aware":
            parts.append(f"Solution-aware prospect evaluating options")
        elif intent_segment == "Problem Aware":
            parts.append(f"Problem-aware researcher gathering information")
        else:
            parts.append(f"Cold curiosity visitor exploring brand")
        
        # Engagement part
        if engagement.content_type.value == "Informational":
            parts.append(f"responding to educational content")
        elif engagement.content_type.value == "Viral":
            parts.append(f"drawn by viral/shareable content")
        else:
            parts.append(f"engaged with {engagement.content_type.value.lower()} content")
        
        # Friction part
        if friction > 0.6:
            parts.append(f"blocked by significant {conversion.primary_friction_point.lower()}")
        elif friction > 0.3:
            parts.append(f"slowed by {conversion.primary_friction_point.lower()}")
        
        base_insight = ", ".join(parts)
        
        # Add recommendation
        if intent_segment == "Ready to Buy":
            recommendation = f"Clear conversion path to maximize purchase"
        elif friction > 0.6:
            recommendation = f"Priority: Fix {conversion.primary_friction_point.lower()} to unlock revenue"
        elif intent.intent_strength > 0.7:
            recommendation = f"High conversion signal - Escalate nurture cadence"
        else:
            recommendation = f"Nurture with {engagement.recommendation.lower()}"
        
        return f"{base_insight}. {recommendation}."
    
    @staticmethod
    def _identify_emotional_trigger(content_type, emotional_resonance) -> str:
        """
        Identify the primary emotional trigger for the audience.
        
        Args:
            content_type: Type of content
            emotional_resonance: Emotional engagement score
            
        Returns:
            Primary emotional trigger description
        """
        content_triggers = {
            "Informational": "Educational value & expertise",
            "Viral": "Emotional entertainment & shareability",
            "Slow Burn": "Trust building & consistency",
            "Entertainment": "Entertainment with subtle value",
            "Hybrid": "Balanced emotion & information"
        }
        
        trigger = content_triggers.get(content_type.value, "General engagement")
        
        # Adjust intensity based on resonance
        if emotional_resonance > 0.2:
            return f"Strong {trigger.lower()}"
        elif emotional_resonance > 0.1:
            return f"Moderate {trigger.lower()}"
        else:
            return f"Subtle {trigger.lower()}"
    
    @staticmethod
    def _calculate_confidence(engagement, conversion, intent) -> float:
        """
        Calculate overall analysis confidence score.
        
        Args:
            engagement: Engagement result
            conversion: Conversion result
            intent: Intent result
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence on signal strength
        engagement_conf = max(
            engagement.emotional_resonance_score,
            engagement.information_value_score,
            engagement.viral_potential_score
        )
        
        conversion_conf = 1 - (conversion.conversion_friction_score * 0.3)
        intent_conf = intent.intent_strength
        
        # Average confidence across dimensions
        confidence = (engagement_conf + conversion_conf + intent_conf) / 3
        
        # Boost confidence if signals align
        if intent.intent_segment.value == "Ready to Buy" and conversion_conf > 0.5:
            confidence = min(1.0, confidence + 0.1)
        
        return round(confidence, 4)
    
    @staticmethod
    def _generate_next_actions(engagement, conversion, intent) -> list:
        """
        Generate prioritized next actions based on analysis.
        
        Args:
            engagement: Engagement result
            conversion: Conversion result
            intent: Intent result
            
        Returns:
            List of prioritized next actions
        """
        actions = []
        
        # Critical action: Address friction if high
        if conversion.conversion_friction_score > 0.6:
            actions.append(f"🔥 CRITICAL: Fix {conversion.primary_friction_point}")
        
        # Conversion action based on intent
        if intent.intent_segment.value == "Ready to Buy":
            actions.append("✅ Reduce conversion friction for immediate sales")
        elif intent.intent_segment.value == "Solution Aware":
            actions.append("🎯 Amplify social proof and overcome objections")
        elif intent.intent_segment.value == "Problem Aware":
            actions.append("📚 Provide comparative content and education")
        else:
            actions.append("🌱 Build brand awareness with engaging content")
        
        # Content action based on engagement
        if engagement.content_type.value in ["Informational", "Slow Burn"]:
            actions.append(f"📄 Double down on educational {engagement.content_type.value.lower()} content")
        elif engagement.content_type.value == "Viral":
            actions.append("🚀 Amplify viral potential through paid promotion")
        
        # Timing action based on intent strength
        if intent.intent_strength > 0.7:
            actions.append("⚡ Accelerate conversion - Strong intent signals detected")
        elif intent.intent_strength < 0.3:
            actions.append("⏱️ Extended nurture cycle - Build intent gradually")
        
        # Revenue action if significant loss
        if conversion.estimated_monthly_revenue_loss > 1000:
            actions.append(
                f"💰 Estimated monthly loss: ${conversion.estimated_monthly_revenue_loss:,.0f} "
                f"- ROI potential for fixes: 300%+"
            )
        
        return actions
    
    @staticmethod
    def _generate_strategic_recommendations(engagement, conversion, intent) -> dict:
        """
        Generate strategic recommendations for marketing.
        
        Args:
            engagement: Engagement result
            conversion: Conversion result
            intent: Intent result
            
        Returns:
            Dictionary with strategic recommendations
        """
        return {
            "positioning": {
                "target_audience": intent.intent_segment.value,
                "emotional_angle": engagement.recommendation,
                "content_strategy": engagement.content_type.value
            },
            "conversion_strategy": {
                "primary_focus": conversion.primary_friction_point,
                "secondary_focus": conversion.secondary_friction_point,
                "optimization_level": conversion.optimization_priority.value,
                "investment_priority": "High" if conversion.estimated_monthly_revenue_loss > 1000 else "Medium"
            },
            "nurture_approach": {
                "segment": intent.intent_segment.value,
                "recommended_strategies": intent.recommended_strategy,
                "content_focus": intent.content_focus,
                "expected_roas": f"{intent.roas_potential_min}x - {intent.roas_potential_max}x"
            }
        }
    
    @staticmethod
    def _generate_segment_positioning(intent_segment, emotional_trigger, revenue_loss) -> dict:
        """
        Generate positioning strategy for the identified segment.
        
        Args:
            intent_segment: Target intent segment
            emotional_trigger: Primary emotional appeal
            revenue_loss: Estimated revenue at risk
            
        Returns:
            Dictionary with segment positioning details
        """
        positioning_map = {
            "Cold Curiosity": {
                "message": "Introduce brand value",
                "channels": ["Social media", "Display ads", "Content marketing"],
                "urgency": "Low"
            },
            "Problem Aware": {
                "message": "Validate problem and compare solutions",
                "channels": ["Blog", "Email", "Webinars"],
                "urgency": "Medium"
            },
            "Solution Aware": {
                "message": "Overcome objections and prove ROI",
                "channels": ["Email", "Retargeting", "Sales"],
                "urgency": "High"
            },
            "Ready to Buy": {
                "message": "Remove friction and incentivize",
                "channels": ["Email", "SMS", "Direct"],
                "urgency": "Critical"
            }
        }
        
        base_positioning = positioning_map.get(intent_segment, {})
        
        return {
            **base_positioning,
            "emotional_trigger": emotional_trigger,
            "revenue_opportunity": f"${revenue_loss * 12:,.0f}/year" if revenue_loss > 0 else "No critical opportunity"
        }
    
    @staticmethod
    def _generate_implementation_roadmap(conversion_priority, intent_strength, confidence) -> list:
        """
        Generate implementation roadmap with priorities.
        
        Args:
            conversion_priority: Conversion optimization priority level
            intent_strength: Customer intent strength
            confidence: Overall analysis confidence
            
        Returns:
            List of implementation steps with timing
        """
        roadmap = []
        
        # Immediate actions (0-7 days)
        if conversion_priority in ["Critical", "High"]:
            roadmap.append({
                "phase": "Immediate (0-7 days)",
                "actions": [
                    "Audit conversion funnel and identify top abandonment point",
                    "Implement quick UX/UX wins to reduce friction",
                    "Set up abandonment recovery email sequence"
                ]
            })
        
        # Short-term (1-4 weeks)
        roadmap.append({
            "phase": "Short-term (1-4 weeks)",
            "actions": [
                "A/B test messaging based on emotional trigger",
                "Implement segment-specific content strategy",
                "Deploy retargeting campaign for intent segment"
            ]
        })
        
        # Medium-term (1-3 months)
        roadmap.append({
            "phase": "Medium-term (1-3 months)",
            "actions": [
                "Build predictive model for intent classification",
                "Automate content personalization by segment",
                "Implement advanced analytics tracking"
            ]
        })
        
        # Long-term (3-6 months)
        roadmap.append({
            "phase": "Long-term (3-6 months)",
            "actions": [
                "Develop AI-powered content recommendations",
                "Build customer journey orchestration",
                "Implement advanced attribution modeling"
            ]
        })
        
        return roadmap
    
    @staticmethod
    def _highlight_critical_insights(response, engagement_details, conversion_details) -> list:
        """
        Extract and highlight critical insights from detailed analysis.
        
        Args:
            response: Comprehensive analysis response
            engagement_details: Engagement analysis details
            conversion_details: Conversion analysis details
            
        Returns:
            List of critical insights
        """
        insights = []
        
        # Conversion insights
        conversion_resp = conversion_details.get("response", {})
        if conversion_resp.get("estimated_monthly_revenue_loss", 0) > 1000:
            insights.append({
                "category": "Revenue Impact",
                "severity": "🔴 Critical",
                "insight": f"Estimated monthly revenue loss: ${conversion_resp['estimated_monthly_revenue_loss']:,.0f}",
                "action": f"Fix {response.conversion.primary_friction_point}"
            })
        
        # Engagement insights
        if engagement_details.get("response", {}).get("viral_potential_score", 0) > 0.15:
            insights.append({
                "category": "Growth Opportunity",
                "severity": "🟢 Opportunity",
                "insight": "Content has viral potential",
                "action": "Amplify through paid promotion"
            })
        
        # Intent insights
        if response.intent.intent_strength > 0.7:
            insights.append({
                "category": "Conversion Readiness",
                "severity": "🟢 Opportunity",
                "insight": "High purchase intent signals detected",
                "action": "Accelerate conversion process"
            })
        
        # Alert if signals don't align
        if response.intent.intent_segment.value == "Ready to Buy" and response.conversion.conversion_friction_score > 0.5:
            insights.append({
                "category": "Misalignment",
                "severity": "🟠 Warning",
                "insight": "Ready-to-buy customer blocked by checkout friction",
                "action": "Urgent: Fix checkout experience"
            })
        
        return insights
