"""
Behavior Analyzer Service - FastAPI Microservice
Analyzes customer behavior signals and generates strategic insights.

Service Port: 8009
Endpoints:
  - POST /api/v1/analyze/engagement
  - POST /api/v1/analyze/conversion
  - POST /api/v1/classify/intent
  - POST /api/v1/analyze/comprehensive
  - GET /health
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os
import logging

from backend.behavior_analyzer_service.models import (
    EngagementSignalsRequest,
    EngagementFeaturesResponse,
    ConversionSignalsRequest,
    ConversionFeaturesResponse,
    IntentSignalsRequest,
    IntentFeaturesResponse,
    ComprehensiveAnalysisRequest,
    HealthResponse,
)
from backend.behavior_analyzer_service.engagement_analyzer import EngagementAnalyzer
from backend.behavior_analyzer_service.conversion_analyzer import ConversionAnalyzer
from backend.behavior_analyzer_service.intent_classifier import IntentClassifier
from backend.behavior_analyzer_service.feature_calculator import FeatureCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Behavior Analyzer Service",
    description="Analyzes customer behavior signals for strategic marketing intelligence",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
engagement_analyzer = EngagementAnalyzer()
conversion_analyzer = ConversionAnalyzer()
intent_classifier = IntentClassifier()
feature_calculator = FeatureCalculator()

# Service info
SERVICE_NAME = "Behavior Analyzer Service"
SERVICE_VERSION = "0.1.0"


# ==================== HEALTH CHECK ====================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with service status
    """
    logger.info("Health check request received")
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=datetime.utcnow()
    )


# ==================== ENGAGEMENT ANALYSIS ====================

@app.post(
    "/api/v1/analyze/engagement",
    response_model=EngagementFeaturesResponse,
    tags=["Engagement Analysis"],
    summary="Analyze social engagement metrics",
    description="Convert platform engagement signals into behavioral features"
)
async def analyze_engagement(signals: EngagementSignalsRequest):
    """
    Analyze social media engagement metrics.
    
    Converts engagement signals (watch retention, saves, shares, comments)
    into actionable features (emotional resonance, information value, viral potential).
    
    Args:
        signals: EngagementSignalsRequest with platform metrics
        
    Returns:
        EngagementFeaturesResponse with calculated features
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing engagement for platform: {signals.platform}")
        result = engagement_analyzer.analyze(signals)
        logger.info(f"Engagement analysis complete - Content type: {result.content_type}")
        return result
    except Exception as e:
        logger.error(f"Error in engagement analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Engagement analysis failed: {str(e)}")


@app.post(
    "/api/v1/analyze/engagement/detailed",
    tags=["Engagement Analysis"],
    summary="Analyze engagement with detailed breakdown",
    description="Get detailed engagement analysis with platform-specific insights"
)
async def analyze_engagement_detailed(signals: EngagementSignalsRequest):
    """
    Analyze engagement with detailed breakdown.
    
    Args:
        signals: EngagementSignalsRequest with platform metrics
        
    Returns:
        Detailed analysis with platform insights
    """
    try:
        logger.info(f"Performing detailed engagement analysis for: {signals.platform}")
        result = engagement_analyzer.analyze_with_details(signals)
        return result
    except Exception as e:
        logger.error(f"Error in detailed engagement analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Engagement analysis failed: {str(e)}")


# ==================== CONVERSION ANALYSIS ====================

@app.post(
    "/api/v1/analyze/conversion",
    response_model=ConversionFeaturesResponse,
    tags=["Conversion Analysis"],
    summary="Analyze conversion funnel metrics",
    description="Identify friction points and estimate revenue impact"
)
async def analyze_conversion(signals: ConversionSignalsRequest):
    """
    Analyze conversion funnel metrics.
    
    Identifies bottlenecks, quantifies friction, and estimates revenue impact.
    
    Args:
        signals: ConversionSignalsRequest with funnel metrics
        
    Returns:
        ConversionFeaturesResponse with friction analysis
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info("Analyzing conversion funnel")
        result = conversion_analyzer.analyze(signals)
        logger.info(
            f"Conversion analysis complete - Primary friction: {result.primary_friction_point}"
        )
        return result
    except Exception as e:
        logger.error(f"Error in conversion analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversion analysis failed: {str(e)}")


@app.post(
    "/api/v1/analyze/conversion/detailed",
    tags=["Conversion Analysis"],
    summary="Analyze conversion with detailed breakdown",
    description="Get detailed conversion analysis with funnel visualization and ROI impact"
)
async def analyze_conversion_detailed(signals: ConversionSignalsRequest):
    """
    Analyze conversion with detailed breakdown.
    
    Args:
        signals: ConversionSignalsRequest with funnel metrics
        
    Returns:
        Detailed analysis with funnel visualization
    """
    try:
        logger.info("Performing detailed conversion analysis")
        result = conversion_analyzer.analyze_with_details(signals)
        return result
    except Exception as e:
        logger.error(f"Error in detailed conversion analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversion analysis failed: {str(e)}")


# ==================== INTENT CLASSIFICATION ====================

@app.post(
    "/api/v1/classify/intent",
    response_model=IntentFeaturesResponse,
    tags=["Intent Classification"],
    summary="Classify customer intent",
    description="Segment customer into 4 intent levels with strategy recommendations"
)
async def classify_intent(signals: IntentSignalsRequest):
    """
    Classify customer intent based on behaviors.
    
    Segments customer into: Cold Curiosity, Problem Aware, Solution Aware, Ready to Buy.
    
    Args:
        signals: IntentSignalsRequest with behavioral metrics
        
    Returns:
        IntentFeaturesResponse with segment classification
        
    Raises:
        HTTPException: If classification fails
    """
    try:
        logger.info("Classifying customer intent")
        result = intent_classifier.classify(signals)
        logger.info(f"Intent classification complete - Segment: {result.intent_segment}")
        return result
    except Exception as e:
        logger.error(f"Error in intent classification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {str(e)}")


@app.post(
    "/api/v1/classify/intent/detailed",
    tags=["Intent Classification"],
    summary="Classify intent with detailed analysis",
    description="Get detailed intent analysis with risk assessment and personalization hints"
)
async def classify_intent_detailed(signals: IntentSignalsRequest):
    """
    Classify intent with detailed breakdown.
    
    Args:
        signals: IntentSignalsRequest with behavioral metrics
        
    Returns:
        Detailed analysis with risk assessment
    """
    try:
        logger.info("Performing detailed intent classification")
        result = intent_classifier.classify_with_details(signals)
        return result
    except Exception as e:
        logger.error(f"Error in detailed intent classification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {str(e)}")


# ==================== COMPREHENSIVE ANALYSIS ====================

@app.post(
    "/api/v1/analyze/comprehensive",
    tags=["Comprehensive Analysis"],
    summary="Comprehensive multi-dimensional analysis",
    description="Analyze engagement, conversion, and intent together for strategic insights"
)
async def analyze_comprehensive(request: ComprehensiveAnalysisRequest):
    """
    Perform comprehensive analysis combining all three dimensions.
    
    Analyzes engagement, conversion, and intent together to provide
    unified strategic intelligence.
    
    Args:
        request: ComprehensiveAnalysisRequest with all signal types
        
    Returns:
        Unified analysis response with combined insights
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info("Performing comprehensive multi-dimensional analysis")
        result = feature_calculator.analyze_comprehensive(
            engagement=request.engagement,
            conversion=request.conversion,
            intent=request.intent
        )
        logger.info("Comprehensive analysis complete")
        return result
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@app.post(
    "/api/v1/analyze/comprehensive/detailed",
    tags=["Comprehensive Analysis"],
    summary="Comprehensive analysis with full details",
    description="Get complete analysis breakdown with strategic recommendations and roadmap"
)
async def analyze_comprehensive_detailed(request: ComprehensiveAnalysisRequest):
    """
    Perform comprehensive analysis with detailed breakdowns.
    
    Args:
        request: ComprehensiveAnalysisRequest with all signal types
        
    Returns:
        Complete analysis with strategic recommendations
    """
    try:
        logger.info("Performing detailed comprehensive analysis")
        result = feature_calculator.analyze_comprehensive_with_details(
            engagement=request.engagement,
            conversion=request.conversion,
            intent=request.intent
        )
        logger.info("Detailed comprehensive analysis complete")
        return result
    except Exception as e:
        logger.error(f"Error in detailed comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


# ==================== INFO & DOCUMENTATION ====================

@app.get("/info", tags=["Info"])
async def service_info():
    """Get service information."""
    return {
        "name": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Behavior feature engineering for marketing intelligence",
        "endpoints": {
            "engagement": "/api/v1/analyze/engagement",
            "conversion": "/api/v1/analyze/conversion",
            "intent": "/api/v1/classify/intent",
            "comprehensive": "/api/v1/analyze/comprehensive"
        },
        "health": "/health",
        "docs": "/docs"
    }


# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info("Service is ready to analyze behavioral signals")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info(f"Shutting down {SERVICE_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8009))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
