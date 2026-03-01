"""
Conversion Analyzer - Identifies friction points in the customer funnel.
Analyzes conversion metrics to locate bottlenecks and estimate revenue impact.
"""

from shared.utils.feature_library import (
    ConversionCalculator,
    ConversionFeatures,
)
from backend.behavior_analyzer_service.models import (
    ConversionSignalsRequest,
    ConversionFeaturesResponse,
    OptimizationPriorityEnum,
)


class ConversionAnalyzer:
    """
    Analyzes conversion funnel metrics to identify and quantify friction points.
    
    Metrics Analyzed:
    - Add to cart rate: How many visitors engage with products
    - Checkout abandon rate: How many conversions are lost
    - Page time: Engagement depth on product pages
    - Session duration: Overall engagement quality
    - Repeat purchase: Customer lifetime value signal
    
    Output:
    - Purchase intent: Likelihood to convert
    - Conversion friction: Amount of friction in the funnel
    - Friction points: Specific barriers identified
    - Revenue impact: Estimated lost revenue
    """
    
    def __init__(self):
        """Initialize the conversion analyzer."""
        self.calculator = ConversionCalculator()
    
    def analyze(self, signals: ConversionSignalsRequest) -> ConversionFeaturesResponse:
        """
        Analyze conversion signals and return friction analysis.
        
        Args:
            signals: ConversionSignalsRequest with funnel metrics
            
        Returns:
            ConversionFeaturesResponse with friction analysis and recommendations
        """
        # Calculate purchase intent
        purchase_intent = self.calculator.purchase_intent(
            add_to_cart_rate=signals.add_to_cart_rate,
            avg_page_time=signals.avg_product_page_time,
            avg_session_duration=signals.avg_session_duration
        )
        
        # Calculate friction score
        friction_score = self.calculator.conversion_friction(
            checkout_abandon_rate=signals.checkout_abandon_rate,
            add_to_cart_rate=signals.add_to_cart_rate
        )
        
        # Identify friction points
        primary_friction, secondary_friction = self.calculator.identify_friction_points(
            checkout_abandon_rate=signals.checkout_abandon_rate,
            avg_product_page_time=signals.avg_product_page_time,
            avg_session_duration=signals.avg_session_duration
        )
        
        # Determine optimization priority
        priority = self.calculator.optimization_priority(friction_score)
        
        # Estimate revenue loss
        revenue_loss = self.calculator.estimated_revenue_loss(
            checkout_abandon_rate=signals.checkout_abandon_rate,
            add_to_cart_rate=signals.add_to_cart_rate,
            monthly_sessions=signals.monthly_sessions,
            avg_order_value=signals.avg_order_value
        )
        
        return ConversionFeaturesResponse(
            purchase_intent_score=round(purchase_intent, 4),
            conversion_friction_score=round(friction_score, 4),
            primary_friction_point=primary_friction,
            secondary_friction_point=secondary_friction,
            optimization_priority=OptimizationPriorityEnum(priority),
            estimated_monthly_revenue_loss=round(revenue_loss, 2)
        )
    
    def analyze_with_details(self, signals: ConversionSignalsRequest) -> dict:
        """
        Analyze conversion metrics with detailed breakdown.
        
        Includes:
        - Full funnel visualization
        - Conversion rate calculations
        - Bottleneck identification
        - ROI impact analysis
        
        Args:
            signals: ConversionSignalsRequest with funnel metrics
            
        Returns:
            Dictionary with comprehensive conversion analysis
        """
        response = self.analyze(signals)
        
        # Calculate conversion rates
        checkout_conversion_rate = (1 - signals.checkout_abandon_rate) * signals.add_to_cart_rate
        
        # Create funnel visualization
        funnel = self._build_funnel_visualization(
            add_to_cart=signals.add_to_cart_rate,
            abandon=signals.checkout_abandon_rate,
            repeat_purchase=signals.repeat_purchase_rate
        )
        
        # Segment analysis
        segments = self._segment_behavior(
            checkout_abandon_rate=signals.checkout_abandon_rate,
            avg_page_time=signals.avg_product_page_time,
            avg_session_duration=signals.avg_session_duration,
            repeat_rate=signals.repeat_purchase_rate
        )
        
        return {
            "response": response.dict(),
            "conversion_metrics": {
                "add_to_cart_rate": signals.add_to_cart_rate,
                "checkout_conversion_rate": round(checkout_conversion_rate, 4),
                "checkout_abandon_rate": signals.checkout_abandon_rate,
                "repeat_purchase_rate": signals.repeat_purchase_rate
            },
            "engagement_metrics": {
                "avg_product_page_time_sec": signals.avg_product_page_time,
                "avg_session_duration_sec": signals.avg_session_duration,
                "engagement_ratio": round(
                    signals.avg_product_page_time / signals.avg_session_duration,
                    4
                ) if signals.avg_session_duration > 0 else 0
            },
            "funnel_visualization": funnel,
            "behavior_segments": segments,
            "roi_impact": self._calculate_roi_impact(
                revenue_loss=response.estimated_monthly_revenue_loss,
                avg_order_value=signals.avg_order_value
            )
        }
    
    @staticmethod
    def _build_funnel_visualization(
        add_to_cart: float,
        abandon: float,
        repeat_purchase: float
    ) -> dict:
        """
        Build a visualization of the conversion funnel.
        
        Args:
            add_to_cart: Add to cart conversion rate
            abandon: Checkout abandonment rate
            repeat_purchase: Repeat purchase rate
            
        Returns:
            Dictionary with funnel stages and conversion rates
        """
        # Assume 100 visitors start
        visitors = 100
        cart_adds = int(visitors * add_to_cart)
        completions = int(cart_adds * (1 - abandon))
        repeats = int(completions * repeat_purchase)
        
        return {
            "stage_1_visitors": visitors,
            "stage_2_cart_adds": {
                "count": cart_adds,
                "conversion_rate": round(add_to_cart, 4),
                "loss_percentage": round(100 - (cart_adds / visitors * 100), 1)
            },
            "stage_3_completions": {
                "count": completions,
                "conversion_rate": round(1 - abandon, 4),
                "loss_percentage": round(100 - (completions / cart_adds * 100), 1) if cart_adds > 0 else 0
            },
            "stage_4_repeats": {
                "count": repeats,
                "conversion_rate": round(repeat_purchase, 4),
                "loss_percentage": round(100 - (repeats / completions * 100), 1) if completions > 0 else 0
            },
            "final_conversion_rate": round(completions / visitors, 4)
        }
    
    @staticmethod
    def _segment_behavior(
        checkout_abandon_rate: float,
        avg_page_time: float,
        avg_session_duration: float,
        repeat_rate: float
    ) -> dict:
        """
        Segment users by behavior patterns.
        
        Args:
            checkout_abandon_rate: Checkout abandonment rate
            avg_page_time: Average product page time
            avg_session_duration: Average session length
            repeat_rate: Repeat purchase rate
            
        Returns:
            Dictionary with identified behavior segments
        """
        segments = {}
        
        # High abandoners (potential security/payment concerns)
        if checkout_abandon_rate > 0.5:
            segments["high_abandoners"] = {
                "percentage": round(checkout_abandon_rate * 100, 1),
                "characteristic": "Checkout barriers",
                "potential_cause": "Payment options, security concerns, unexpected charges",
                "recovery_strategy": "Trust signals, payment flexibility, transparent pricing"
            }
        
        # Low engagement shoppers
        if avg_page_time < 100:
            segments["low_engagement"] = {
                "avg_time_sec": avg_page_time,
                "characteristic": "Quick exits",
                "potential_cause": "Unclear product info, poor images, navigation issues",
                "recovery_strategy": "Better product presentation, UX improvements"
            }
        
        # Loyal customers
        if repeat_rate > 0.4:
            segments["loyal_customers"] = {
                "repeat_rate": round(repeat_rate * 100, 1),
                "characteristic": "High lifetime value",
                "potential_cause": "Strong product-market fit",
                "retention_strategy": "Loyalty programs, early access, VIP perks"
            }
        
        return segments
    
    @staticmethod
    def _calculate_roi_impact(revenue_loss: float, avg_order_value: float) -> dict:
        """
        Calculate ROI impact of addressing friction points.
        
        Args:
            revenue_loss: Estimated monthly revenue loss
            avg_order_value: Average order value
            
        Returns:
            Dictionary with ROI projections
        """
        if revenue_loss == 0:
            return {"status": "No significant friction identified"}
        
        lost_orders = revenue_loss / avg_order_value if avg_order_value > 0 else 0
        
        # ROI scenarios for different improvements
        improvement_scenarios = {
            "reduce_abandon_10percent": {
                "description": "Reduce abandonment by 10%",
                "monthly_gain": round(revenue_loss * 0.1, 2),
                "annual_gain": round(revenue_loss * 0.1 * 12, 2),
                "orders_recovered": int(lost_orders * 0.1)
            },
            "reduce_abandon_25percent": {
                "description": "Reduce abandonment by 25%",
                "monthly_gain": round(revenue_loss * 0.25, 2),
                "annual_gain": round(revenue_loss * 0.25 * 12, 2),
                "orders_recovered": int(lost_orders * 0.25)
            },
            "reduce_abandon_50percent": {
                "description": "Reduce abandonment by 50%",
                "monthly_gain": round(revenue_loss * 0.5, 2),
                "annual_gain": round(revenue_loss * 0.5 * 12, 2),
                "orders_recovered": int(lost_orders * 0.5)
            }
        }
        
        return {
            "current_monthly_loss": revenue_loss,
            "lost_orders_per_month": int(lost_orders),
            "annual_loss_projection": round(revenue_loss * 12, 2),
            "improvement_scenarios": improvement_scenarios
        }
