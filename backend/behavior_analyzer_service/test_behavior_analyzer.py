"""
Test suite for Behavior Analyzer Service.
Comprehensive tests for all analyzers and feature calculations.
"""

import pytest
from datetime import datetime

# Test fixtures
from backend.behavior_analyzer_service.models import (
    EngagementSignalsRequest,
    ConversionSignalsRequest,
    IntentSignalsRequest,
    ComprehensiveAnalysisRequest,
)
from backend.behavior_analyzer_service.engagement_analyzer import EngagementAnalyzer
from backend.behavior_analyzer_service.conversion_analyzer import ConversionAnalyzer
from backend.behavior_analyzer_service.intent_classifier import IntentClassifier
from backend.behavior_analyzer_service.feature_calculator import FeatureCalculator
from shared.utils.feature_library import (
    EngagementCalculator,
    ConversionCalculator,
    IntentCalculator,
    ContentType,
    IntentSegment,
)


# ==================== FIXTURES ====================

@pytest.fixture
def engagement_signals_viral():
    """Sample viral content engagement signals."""
    return EngagementSignalsRequest(
        platform="tiktok",
        watch_retention=0.85,
        save_rate=0.08,
        share_rate=0.15,
        comment_rate=0.12,
        view_count=120000
    )


@pytest.fixture
def engagement_signals_educational():
    """Sample educational content engagement signals."""
    return EngagementSignalsRequest(
        platform="youtube",
        watch_retention=0.72,
        save_rate=0.12,
        share_rate=0.05,
        comment_rate=0.08,
        view_count=45000
    )


@pytest.fixture
def engagement_signals_low():
    """Sample low engagement signals."""
    return EngagementSignalsRequest(
        platform="instagram",
        watch_retention=0.35,
        save_rate=0.02,
        share_rate=0.01,
        comment_rate=0.03,
        view_count=5000
    )


@pytest.fixture
def conversion_signals_high_friction():
    """Sample conversion signals with high friction."""
    return ConversionSignalsRequest(
        add_to_cart_rate=0.18,
        checkout_abandon_rate=0.60,
        avg_product_page_time=150,
        avg_session_duration=240,
        repeat_purchase_rate=0.20
    )


@pytest.fixture
def conversion_signals_low_friction():
    """Sample conversion signals with low friction."""
    return ConversionSignalsRequest(
        add_to_cart_rate=0.25,
        checkout_abandon_rate=0.15,
        avg_product_page_time=280,
        avg_session_duration=450,
        repeat_purchase_rate=0.45
    )


@pytest.fixture
def intent_signals_ready_to_buy():
    """Sample intent signals for ready-to-buy customer."""
    return IntentSignalsRequest(
        scroll_depth=0.95,
        pages_visited=6,
        time_on_site=580,
        has_added_to_cart=True,
        is_previous_purchaser=True,
        email_opens=3,
        abandoned_carts=1
    )


@pytest.fixture
def intent_signals_cold_curiosity():
    """Sample intent signals for cold curiosity visitor."""
    return IntentSignalsRequest(
        scroll_depth=0.15,
        pages_visited=0.5,
        time_on_site=30,
        has_added_to_cart=False,
        is_previous_purchaser=False,
        email_opens=0,
        abandoned_carts=0
    )


# ==================== FEATURE LIBRARY TESTS ====================

class TestEngagementCalculator:
    """Test engagement feature calculations."""
    
    def test_emotional_resonance_high(self):
        """Test emotional resonance with high engagement."""
        score = EngagementCalculator.emotional_resonance(
            save_rate=0.15,
            comment_rate=0.12
        )
        assert 0.13 < score < 0.14  # Should be ~0.135
        assert score > 0.1
    
    def test_emotional_resonance_low(self):
        """Test emotional resonance with low engagement."""
        score = EngagementCalculator.emotional_resonance(
            save_rate=0.01,
            comment_rate=0.02
        )
        assert score < 0.02
    
    def test_information_value(self):
        """Test information value calculation."""
        score = EngagementCalculator.information_value(
            watch_retention=0.72,
            share_rate=0.05
        )
        assert 0.67 < score < 0.68
    
    def test_viral_potential(self):
        """Test viral potential calculation."""
        score = EngagementCalculator.viral_potential(
            share_rate=0.15,
            comment_rate=0.12
        )
        assert score > 0.1
        assert score <= 1.0  # Should be clamped
    
    def test_content_type_classification_informational(self):
        """Test classification as informational."""
        content_type = EngagementCalculator.classify_content_type(
            emotional_resonance=0.10,
            information_value=0.65,
            viral_potential=0.08
        )
        assert content_type == ContentType.INFORMATIONAL
    
    def test_content_type_classification_viral(self):
        """Test classification as viral."""
        content_type = EngagementCalculator.classify_content_type(
            emotional_resonance=0.12,
            information_value=0.50,
            viral_potential=0.20
        )
        assert content_type == ContentType.VIRAL


class TestConversionCalculator:
    """Test conversion feature calculations."""
    
    def test_purchase_intent(self):
        """Test purchase intent score."""
        score = ConversionCalculator.purchase_intent(
            add_to_cart_rate=0.18,
            avg_page_time=187.5,
            avg_session_duration=245
        )
        assert 0.1 < score < 0.2
    
    def test_conversion_friction_high(self):
        """Test friction score with high abandonment."""
        score = ConversionCalculator.conversion_friction(
            checkout_abandon_rate=0.60,
            add_to_cart_rate=0.18
        )
        assert score > 0.5
    
    def test_conversion_friction_low(self):
        """Test friction score with low abandonment."""
        score = ConversionCalculator.conversion_friction(
            checkout_abandon_rate=0.15,
            add_to_cart_rate=0.25
        )
        assert score < 0.3
    
    def test_friction_point_identification(self):
        """Test identifying friction points."""
        primary, secondary = ConversionCalculator.identify_friction_points(
            checkout_abandon_rate=0.60,
            avg_product_page_time=150,
            avg_session_duration=240
        )
        assert "Checkout" in primary or "checkout" in primary.lower()
    
    def test_revenue_loss_estimation(self):
        """Test revenue loss calculation."""
        loss = ConversionCalculator.estimated_revenue_loss(
            checkout_abandon_rate=0.42,
            add_to_cart_rate=0.18,
            monthly_sessions=10000,
            avg_order_value=75.0
        )
        assert loss > 0
        assert loss < 100000  # Sanity check


class TestIntentCalculator:
    """Test intent classification calculations."""
    
    def test_intent_strength_high(self):
        """Test intent strength with high engagement."""
        strength = IntentCalculator.calculate_intent_strength(
            scroll_depth=0.85,
            pages_visited=4,
            time_on_site=400,
            has_added_to_cart=True
        )
        assert strength > 0.5
    
    def test_intent_strength_low(self):
        """Test intent strength with low engagement."""
        strength = IntentCalculator.calculate_intent_strength(
            scroll_depth=0.2,
            pages_visited=0.5,
            time_on_site=30,
            has_added_to_cart=False
        )
        assert strength < 0.3
    
    def test_classify_ready_to_buy(self):
        """Test classification as ready-to-buy."""
        segment = IntentCalculator.classify_intent(
            intent_strength=0.8,
            pages_visited=5,
            has_added_to_cart=True,
            is_previous_purchaser=True,
            abandoned_carts=1
        )
        assert segment == IntentSegment.READY_TO_BUY
    
    def test_classify_solution_aware(self):
        """Test classification as solution-aware."""
        segment = IntentCalculator.classify_intent(
            intent_strength=0.6,
            pages_visited=3,
            has_added_to_cart=True,
            is_previous_purchaser=False,
            abandoned_carts=0
        )
        assert segment == IntentSegment.SOLUTION_AWARE
    
    def test_classify_problem_aware(self):
        """Test classification as problem-aware."""
        segment = IntentCalculator.classify_intent(
            intent_strength=0.6,
            pages_visited=4,
            has_added_to_cart=False,
            is_previous_purchaser=False,
            abandoned_carts=0
        )
        assert segment == IntentSegment.PROBLEM_AWARE
    
    def test_classify_cold_curiosity(self):
        """Test classification as cold curiosity."""
        segment = IntentCalculator.classify_intent(
            intent_strength=0.2,
            pages_visited=0.5,
            has_added_to_cart=False,
            is_previous_purchaser=False,
            abandoned_carts=0
        )
        assert segment == IntentSegment.COLD_CURIOSITY


# ==================== ANALYZER TESTS ====================

class TestEngagementAnalyzer:
    """Test engagement analyzer."""
    
    def test_analyze_viral_content(self, engagement_signals_viral):
        """Test analyzing viral content signals."""
        analyzer = EngagementAnalyzer()
        result = analyzer.analyze(engagement_signals_viral)
        
        assert result.viral_potential_score > 0.1
        assert result.content_type.value in ["Viral", "Entertainment"]
    
    def test_analyze_educational_content(self, engagement_signals_educational):
        """Test analyzing educational content signals."""
        analyzer = EngagementAnalyzer()
        result = analyzer.analyze(engagement_signals_educational)
        
        assert result.information_value_score > 0.6
        assert "Informational" in result.content_type.value
    
    def test_analyze_low_engagement(self, engagement_signals_low):
        """Test analyzing low engagement content."""
        analyzer = EngagementAnalyzer()
        result = analyzer.analyze(engagement_signals_low)
        
        assert result.viral_potential_score < 0.1
        assert result.emotional_resonance_score < 0.05


class TestConversionAnalyzer:
    """Test conversion analyzer."""
    
    def test_analyze_high_friction(self, conversion_signals_high_friction):
        """Test analyzing high friction funnel."""
        analyzer = ConversionAnalyzer()
        result = analyzer.analyze(conversion_signals_high_friction)
        
        assert result.conversion_friction_score > 0.5
        assert result.optimization_priority.value in ["High", "Critical"]
    
    def test_analyze_low_friction(self, conversion_signals_low_friction):
        """Test analyzing low friction funnel."""
        analyzer = ConversionAnalyzer()
        result = analyzer.analyze(conversion_signals_low_friction)
        
        assert result.conversion_friction_score < 0.4
        assert result.optimization_priority.value in ["Low", "Medium"]
    
    def test_revenue_loss_estimation(self, conversion_signals_high_friction):
        """Test revenue loss estimation."""
        analyzer = ConversionAnalyzer()
        result = analyzer.analyze(conversion_signals_high_friction)
        
        assert result.estimated_monthly_revenue_loss > 0


class TestIntentClassifier:
    """Test intent classifier."""
    
    def test_classify_ready_to_buy(self, intent_signals_ready_to_buy):
        """Test classifying ready-to-buy customer."""
        classifier = IntentClassifier()
        result = classifier.classify(intent_signals_ready_to_buy)
        
        assert result.intent_segment.value == "Ready to Buy"
        assert result.intent_strength > 0.6
        assert result.roas_potential_min >= 3.5
    
    def test_classify_cold_curiosity(self, intent_signals_cold_curiosity):
        """Test classifying cold curiosity visitor."""
        classifier = IntentClassifier()
        result = classifier.classify(intent_signals_cold_curiosity)
        
        assert result.intent_segment.value == "Cold Curiosity"
        assert result.roas_potential_max <= 1.0


class TestFeatureCalculator:
    """Test comprehensive feature calculator."""
    
    def test_comprehensive_analysis(
        self,
        engagement_signals_educational,
        conversion_signals_low_friction,
        intent_signals_ready_to_buy
    ):
        """Test comprehensive analysis."""
        calc = FeatureCalculator()
        result = calc.analyze_comprehensive(
            engagement=engagement_signals_educational,
            conversion=conversion_signals_low_friction,
            intent=intent_signals_ready_to_buy
        )
        
        assert result.engagement is not None
        assert result.conversion is not None
        assert result.intent is not None
        assert result.combined_insight is not None
        assert 0 <= result.confidence_score <= 1
        assert len(result.next_actions) > 0


# ==================== INTEGRATION TESTS ====================

class TestServiceIntegration:
    """Integration tests for the full service."""
    
    def test_end_to_end_analysis(
        self,
        engagement_signals_educational,
        conversion_signals_high_friction,
        intent_signals_ready_to_buy
    ):
        """Test complete end-to-end analysis."""
        calc = FeatureCalculator()
        
        result = calc.analyze_comprehensive_with_details(
            engagement=engagement_signals_educational,
            conversion=conversion_signals_high_friction,
            intent=intent_signals_ready_to_buy
        )
        
        # Verify comprehensive response
        assert "comprehensive_response" in result
        assert "engagement_details" in result
        assert "conversion_details" in result
        assert "intent_details" in result
        assert "strategic_recommendations" in result
        assert "critical_insights" in result
        assert "implementation_roadmap" in result


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
