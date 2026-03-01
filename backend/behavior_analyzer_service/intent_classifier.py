"""
Intent Classifier - Classifies customers into 4 intent segments.
Determines customer readiness to purchase and recommends targeted strategies.
"""

from shared.utils.feature_library import (
    IntentCalculator,
    IntentSegment,
)
from backend.behavior_analyzer_service.models import (
    IntentSignalsRequest,
    IntentFeaturesResponse,
    IntentSegmentEnum,
)


class IntentClassifier:
    """
    Classifies customers into 4 intent segments based on behavioral signals.
    
    Segments:
    - Cold Curiosity: Low engagement, high bounce rate
    - Problem Aware: Researching, comparing solutions
    - Solution Aware: Evaluated solutions, considering purchase
    - Ready to Buy: Previous customer or actively purchasing
    
    Outputs:
    - Intent segment classification
    - Confidence score
    - Recommended content strategy
    - Expected ROAS potential
    """
    
    # Intent segment characteristics and thresholds
    SEGMENT_PROFILES = {
        IntentSegment.COLD_CURIOSITY: {
            "description": "Curiosity-driven with minimal commitment",
            "characteristics": [
                "Low engagement depth",
                "High bounce rate",
                "Limited page views",
                "No purchase signals"
            ],
            "typical_behavior": "Accidental traffic, brand discovery",
            "expected_roas": "0.5x - 1.0x"
        },
        IntentSegment.PROBLEM_AWARE: {
            "description": "Actively researching problems and solutions",
            "characteristics": [
                "Multiple page visits",
                "Good time on site",
                "Research behavior",
                "Solution comparison"
            ],
            "typical_behavior": "Visiting product pages, reading reviews",
            "expected_roas": "1.0x - 1.5x"
        },
        IntentSegment.SOLUTION_AWARE: {
            "description": "Evaluated solutions, considering purchase",
            "characteristics": [
                "Cart additions",
                "Long product page time",
                "Checkout attempts",
                "Decision in progress"
            ],
            "typical_behavior": "Cart adds, product comparisons, price inquiry",
            "expected_roas": "2.0x - 3.5x"
        },
        IntentSegment.READY_TO_BUY: {
            "description": "Ready to transact or repeat customer",
            "characteristics": [
                "Previous purchases",
                "Cart additions",
                "High intent signals",
                "Repeat visitor"
            ],
            "typical_behavior": "Quick checkout, loyalty program interest",
            "expected_roas": "3.5x - 5.0x"
        }
    }
    
    def __init__(self):
        """Initialize the intent classifier."""
        self.calculator = IntentCalculator()
    
    def classify(self, signals: IntentSignalsRequest) -> IntentFeaturesResponse:
        """
        Classify customer intent based on behavioral signals.
        
        Args:
            signals: IntentSignalsRequest with behavioral metrics
            
        Returns:
            IntentFeaturesResponse with segment classification and strategy
        """
        # Calculate intent strength
        intent_strength = self.calculator.calculate_intent_strength(
            scroll_depth=signals.scroll_depth,
            pages_visited=signals.pages_visited,
            time_on_site=signals.time_on_site,
            has_added_to_cart=signals.has_added_to_cart
        )
        
        # Classify into intent segment
        intent_segment = self.calculator.classify_intent(
            intent_strength=intent_strength,
            pages_visited=signals.pages_visited,
            has_added_to_cart=signals.has_added_to_cart,
            is_previous_purchaser=signals.is_previous_purchaser,
            email_opens=signals.email_opens,
            abandoned_carts=signals.abandoned_carts
        )
        
        # Get recommended strategy
        recommended_strategy = self.calculator.get_recommended_strategy(intent_segment)
        
        # Get content focus
        content_focus = self.calculator.get_content_focus(intent_segment)
        
        # Get ROAS potential
        roas_min, roas_max = self.calculator.get_roas_potential_range(intent_segment)
        
        return IntentFeaturesResponse(
            intent_segment=IntentSegmentEnum(intent_segment.value),
            intent_strength=round(intent_strength, 4),
            recommended_strategy=recommended_strategy,
            content_focus=content_focus,
            roas_potential_min=roas_min,
            roas_potential_max=roas_max
        )
    
    def classify_with_details(self, signals: IntentSignalsRequest) -> dict:
        """
        Classify intent with detailed breakdown and insights.
        
        Includes:
        - Segment profile information
        - Behavioral analysis
        - Personalized strategy recommendations
        - Risk assessment
        
        Args:
            signals: IntentSignalsRequest with behavioral metrics
            
        Returns:
            Dictionary with comprehensive classification analysis
        """
        response = self.classify(signals)
        
        # Get segment profile
        intent_segment_enum = IntentSegment(response.intent_segment.value)
        segment_profile = self.SEGMENT_PROFILES.get(intent_segment_enum, {})
        
        # Behavioral breakdown
        behavioral_analysis = self._analyze_behaviors(
            signals=signals,
            segment=intent_segment_enum
        )
        
        # Risk assessment
        risk_assessment = self._assess_risk(signals=signals, segment=intent_segment_enum)
        
        # Content recommendations
        content_recommendations = self._get_content_recommendations(
            segment=intent_segment_enum,
            strength=response.intent_strength
        )
        
        return {
            "response": response.dict(),
            "segment_profile": segment_profile,
            "behavioral_analysis": behavioral_analysis,
            "risk_assessment": risk_assessment,
            "content_recommendations": content_recommendations,
            "personalization_hints": self._get_personalization_hints(
                segment=intent_segment_enum,
                signals=signals
            )
        }
    
    @staticmethod
    def _analyze_behaviors(
        signals: IntentSignalsRequest,
        segment: IntentSegment
    ) -> dict:
        """
        Analyze individual behavioral signals.
        
        Args:
            signals: Customer signals
            segment: Classified intent segment
            
        Returns:
            Dictionary with behavior analysis
        """
        return {
            "engagement_signals": {
                "scroll_depth": {
                    "value": signals.scroll_depth,
                    "interpretation": "Deep engagement" if signals.scroll_depth > 0.7 else "Surface interaction"
                },
                "pages_visited": {
                    "value": signals.pages_visited,
                    "interpretation": "High research" if signals.pages_visited > 3 else "Limited exploration"
                },
                "time_on_site": {
                    "value": signals.time_on_site,
                    "interpretation": "Strong interest" if signals.time_on_site > 300 else "Quick browse"
                }
            },
            "purchase_signals": {
                "has_added_to_cart": signals.has_added_to_cart,
                "abandoned_carts": signals.abandoned_carts,
                "is_previous_purchaser": signals.is_previous_purchaser
            },
            "communication_signals": {
                "email_opens": signals.email_opens,
                "engagement_frequency": "Active" if signals.email_opens > 0 else "Inactive"
            }
        }
    
    @staticmethod
    def _assess_risk(signals: IntentSignalsRequest, segment: IntentSegment) -> dict:
        """
        Assess risk of losing customer to competitors.
        
        Args:
            signals: Customer signals
            segment: Classified intent segment
            
        Returns:
            Dictionary with risk assessment
        """
        risk_score = 0.0
        risk_factors = []
        
        # High abandonment risk
        if signals.abandoned_carts > 2:
            risk_score += 0.3
            risk_factors.append("Multiple cart abandonments - High churn risk")
        
        # Low engagement risk
        if signals.time_on_site < 180:
            risk_score += 0.2
            risk_factors.append("Low engagement time - Quick to bounce")
        
        # Limited purchase signals
        if not signals.has_added_to_cart and not signals.is_previous_purchaser:
            risk_score += 0.2
            risk_factors.append("No purchase signals - Uncertain intent")
        
        # Inactive email engagement
        if signals.email_opens == 0 and segment == IntentSegment.PROBLEM_AWARE:
            risk_score += 0.15
            risk_factors.append("Not opening emails - Low communication engagement")
        
        risk_level = "Low"
        if risk_score > 0.6:
            risk_level = "Critical"
        elif risk_score > 0.4:
            risk_level = "High"
        elif risk_score > 0.2:
            risk_level = "Medium"
        
        return {
            "risk_score": round(min(risk_score, 1.0), 4),
            "risk_level": risk_level,
            "risk_factors": risk_factors
        }
    
    @staticmethod
    def _get_content_recommendations(segment: IntentSegment, strength: float) -> dict:
        """
        Get specific content recommendations for segment.
        
        Args:
            segment: Intent segment
            strength: Intent strength score
            
        Returns:
            Dictionary with content recommendations
        """
        recommendations = {
            IntentSegment.COLD_CURIOSITY: {
                "content_types": ["Brand story", "Educational content", "Entertainment"],
                "tone": "Friendly, approachable, non-pushy",
                "frequency": "Low (1-2x per week)",
                "channels": ["Social media", "Display ads", "Blog"],
                "key_metrics": ["Engagement rate", "Time on page", "Return visits"]
            },
            IntentSegment.PROBLEM_AWARE: {
                "content_types": ["How-to guides", "Product comparisons", "Case studies"],
                "tone": "Educational, authoritative, helpful",
                "frequency": "Medium (2-3x per week)",
                "channels": ["Email", "Blog", "Webinars"],
                "key_metrics": ["Page visits", "Content shares", "Email opens"]
            },
            IntentSegment.SOLUTION_AWARE: {
                "content_types": ["Product demos", "Testimonials", "ROI calculators"],
                "tone": "Persuasive, benefit-focused, social proof",
                "frequency": "High (3-5x per week)",
                "channels": ["Email", "Retargeting ads", "Product pages"],
                "key_metrics": ["Conversion rate", "Time to conversion", "AOV"]
            },
            IntentSegment.READY_TO_BUY: {
                "content_types": ["Limited offers", "Urgency messages", "Customer success stories"],
                "tone": "Urgent, supportive, incentive-focused",
                "frequency": "Strategic (targeted, not frequent)",
                "channels": ["Email", "SMS", "Push notifications"],
                "key_metrics": ["Purchase rate", "Customer LTV", "Repeat rate"]
            }
        }
        
        base_recommendation = recommendations.get(segment, {})
        
        # Adjust based on strength
        if strength < 0.3:
            base_recommendation["note"] = "Weak signals - Nurture before pushing"
        elif strength > 0.7:
            base_recommendation["note"] = "Strong signals - Aggressive conversion push"
        
        return base_recommendation
    
    @staticmethod
    def _get_personalization_hints(segment: IntentSegment, signals: IntentSignalsRequest) -> list:
        """
        Get personalization hints for customer engagement.
        
        Args:
            segment: Intent segment
            signals: Customer signals
            
        Returns:
            List of personalization insights
        """
        hints = []
        
        # Based on segment
        if segment == IntentSegment.COLD_CURIOSITY:
            hints.append("Focus on brand building and awareness - Long nurture cycle")
        
        elif segment == IntentSegment.PROBLEM_AWARE:
            hints.append("Provide comparative information - Help with decision")
            hints.append("Share thought leadership - Position as expert")
        
        elif segment == IntentSegment.SOLUTION_AWARE:
            hints.append("Use customer testimonials - Build social proof")
            hints.append("Offer limited-time incentives - Create urgency")
            if signals.abandoned_carts > 0:
                hints.append("Address checkout friction - Cart abandonment suggests UX issue")
        
        elif segment == IntentSegment.READY_TO_BUY:
            hints.append("Make purchase frictionless - Remove barriers")
            if signals.is_previous_purchaser:
                hints.append("Implement loyalty program - Maximize lifetime value")
            else:
                hints.append("Offer strong guarantee - Reduce purchase anxiety")
        
        # Based on behavior patterns
        if signals.pages_visited > 5:
            hints.append("They've researched thoroughly - Respect their decision journey")
        
        if signals.time_on_site > 600:
            hints.append("High engagement - They're invested, convert carefully")
        
        if signals.abandoned_carts > 0:
            hints.append("Use abandon cart recovery email - 3-hour window optimal")
        
        if signals.email_opens == 0 and signals.is_previous_purchaser:
            hints.append("Re-engage via SMS or push notification - Email ineffective")
        
        return hints
