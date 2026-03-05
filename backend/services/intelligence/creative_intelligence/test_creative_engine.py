"""
Creative Intelligence Test Suite
================================
Walks the system from collecting a raw ad, sequencing its DNA, finding
the mathematical pattern, and outputting the literal hallucinated
script based on the best-selling variables.
"""

import pytest
from backend.services.intelligence.creative_intelligence.models import CreativeGoal
from backend.services.intelligence.creative_intelligence.creative_collector import CreativeCollector
from backend.services.intelligence.creative_intelligence.creative_dna_encoder import CreativeDNAEncoder
from backend.services.intelligence.creative_intelligence.pattern_analyzer import PatternAnalyzer
from backend.services.intelligence.creative_intelligence.creative_generator import CreativeGeneratorCoordinator

@pytest.mark.asyncio
async def test_creative_intelligence_engine_e2e():
    """
    Takes 1 scraped ad -> DNA -> Insight -> Generates targeted Script.
    """
    
    # 1. Scrape raw historical ads
    collector = CreativeCollector()
    creatives = await collector.collect_creatives("Meta Ads", "B2B SaaS Analytics")
    
    assert len(creatives) >= 1
    raw_creative = creatives[0]
    
    # 2. Extract DNA Variables
    encoder = CreativeDNAEncoder()
    dna = await encoder.encode(raw_creative)
    
    assert dna.hook_type in ["curiosity", "pain_point", "social_proof", "controversial", "question", "story"]
    assert dna.emotion in ["fear", "aspiration", "curiosity", "urgency", "trust", "excitement"]
    assert dna.story_pattern in ["problem_solution", "hero_journey", "before_after", "testimonial", "demo_walkthrough"]
    
    # 3. Form a Pattern Insight block 
    analyzer = PatternAnalyzer()
    
    insights = await analyzer.analyze_patterns([{"dna": dna.model_dump(), "metrics": {"ctr": 0.05}}])
    assert len(insights) >= 1
    
    top_insight = insights[0]
    assert top_insight.hook == "pain_point"
    assert top_insight.story == "problem_solution"
    assert top_insight.visual_format == "ugc_video"
    
    # 4. Generate new Scripts entirely based on that Insight
    generator = CreativeGeneratorCoordinator()
    
    goal = CreativeGoal(
        product="AI Simulation Twin",
        audience="Growth Marketers",
        platform="Meta Reels"
    )
    
    new_campaign = await generator.generate_winning_creative(goal, top_insight)
    
    assert "concept_block" in new_campaign
    assert "alternative_hooks" in new_campaign
    assert "final_script" in new_campaign
    
    assert len(new_campaign["alternative_hooks"]) >= 3
    assert "Hook:" in new_campaign["final_script"]
    assert "Story:" in new_campaign["final_script"]
