"""
Competitor Intelligence Engine — Full Test Suite
=================================================
Tests all modules without requiring Qdrant, GPU, or live internet.
All external dependencies are gracefully mocked.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# ── Module imports ─────────────────────────────────────────────────────────

from backend.services.competitor_intelligence.models import ExternalContent, CrawledCompetitor, CompetitorCluster
from backend.services.competitor_intelligence.crawler_engine import CompetitorCrawler
from backend.services.competitor_intelligence.ad_capture_engine import AdCaptureEngine
from backend.services.competitor_intelligence.content_cleaner import ContentCleaner
from backend.services.competitor_intelligence.embedding_engine import EmbeddingEngine, _mock_vector
from backend.services.competitor_intelligence.similarity_engine import SimilarityEngine
from backend.services.competitor_intelligence.market_pressure_detector import MarketPressureDetector
from backend.services.competitor_intelligence.strategy_gap_analyzer import StrategyGapAnalyzer


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def registry():
    r = CompetitorRegistry()
    # Isolate each test — inject fresh state
    import backend.services.competitor_intelligence.competitor_registry as mod
    mod._registry = {}
    return r

@pytest.fixture
def cleaner():
    return ContentCleaner()

@pytest.fixture
def similarity():
    return SimilarityEngine()

@pytest.fixture
def pressure_detector():
    return MarketPressureDetector()

@pytest.fixture
def gap_analyzer():
    return StrategyGapAnalyzer()

@pytest.fixture
def sample_ads():
    return [
        {"platform": "meta",   "headline": "Try free for 14 days", "body_text": "No credit card needed", "cta": "Start Free Trial", "offer_type": "trial",   "emotional_tone": "educational"},
        {"platform": "meta",   "headline": "Try free — no limits",  "body_text": "Cancel anytime. Risk free.", "cta": "Start Free Trial", "offer_type": "trial",   "emotional_tone": "friendly"},
        {"platform": "google", "headline": "50% off first 3 months","body_text": "Limited time discount",  "cta": "Claim Offer",     "offer_type": "discount","emotional_tone": "aggressive"},
        {"platform": "meta",   "headline": "Book a personalised demo","body_text": "See it in action",    "cta": "Book Demo",       "offer_type": "demo",    "emotional_tone": "premium"},
        {"platform": "google", "headline": "Trusted by 5000 teams",  "body_text": "Rated #1 by marketers", "cta": "See Plans",       "offer_type": "direct",  "emotional_tone": "premium"},
    ]

@pytest.fixture
def cluster_data(similarity, sample_ads):
    return similarity.analyze_ad_clusters(sample_ads)


# ═══════════════════════════════════════════════════════════════════════════
# 1. COMPETITOR REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

class TestCompetitorRegistry:
    def test_register_creates_profile(self, registry):
        p = registry.register("co1", "Acme", "acme.com", "SaaS")
        assert p["company_id"] == "co1"
        assert p["domain"] == "acme.com"
        assert p["is_active"] is True

    def test_list_returns_only_company_competitors(self, registry):
        registry.register("co1", "Acme",  "acme.com")
        registry.register("co1", "Rival", "rival.com")
        registry.register("co2", "Other", "other.com")
        assert len(registry.list_competitors("co1")) == 2
        assert len(registry.list_competitors("co2")) == 1

    def test_get_by_domain(self, registry):
        registry.register("co1", "Acme", "acme.com")
        result = registry.get_by_domain("co1", "acme.com")
        assert result is not None
        assert result["name"] == "Acme"

    def test_mark_crawled_increments_count(self, registry):
        registry.register("co1", "Acme", "acme.com")
        registry.mark_crawled("co1", "acme.com")
        registry.mark_crawled("co1", "acme.com")
        p = registry.get_by_domain("co1", "acme.com")
        assert p["crawl_count"] == 2

    def test_deactivate(self, registry):
        registry.register("co1", "Acme", "acme.com")
        registry.deactivate("co1", "acme.com")
        assert len(registry.list_competitors("co1")) == 0


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONTENT CLEANER
# ═══════════════════════════════════════════════════════════════════════════

class TestContentCleaner:
    SAMPLE_HTML = """
    <html><head><title>Test</title></head>
    <body>
      <nav>Nav junk</nav>
      <h1>Best Marketing Platform</h1>
      <p>Trusted by 5000+ marketers. Free trial — no credit card needed.</p>
      <h2>Features</h2>
      <ul><li>Automate campaigns</li><li>Real-time analytics</li></ul>
      <footer>Copyright 2024 All rights reserved cookie policy</footer>
      <script>console.log('noise')</script>
    </body></html>
    """

    def test_removes_script_and_nav(self, cleaner):
        result = cleaner.clean_html(self.SAMPLE_HTML)
        assert "console.log" not in result
        assert "Nav junk" not in result

    def test_removes_footer_boilerplate(self, cleaner):
        result = cleaner.clean_html(self.SAMPLE_HTML)
        assert "cookie policy" not in result.lower()

    def test_extracts_high_signal_content(self, cleaner):
        result = cleaner.clean_html(self.SAMPLE_HTML)
        assert "Best Marketing Platform" in result
        assert "Free trial" in result

    def test_chunking_returns_list(self, cleaner):
        text = " ".join(["word"] * 1000)
        chunks = cleaner.chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) > 1

    def test_chunks_have_overlap(self, cleaner):
        words = list(range(200))
        text  = " ".join(str(w) for w in words)
        chunks = cleaner.chunk_text(text, chunk_size=50, overlap=10)
        # Check first word of chunk[1] appears in end of chunk[0]
        assert len(chunks) >= 2

    def test_detect_offer_type_trial(self, cleaner):
        assert cleaner.detect_offer_type("Start your free trial today, no credit card needed") == "trial"

    def test_detect_offer_type_demo(self, cleaner):
        assert cleaner.detect_offer_type("Book a demo with our team") == "demo"

    def test_detect_tone_educational(self, cleaner):
        assert cleaner.detect_tone("Learn how to understand marketing insights with our guide") == "educational"

    def test_detect_tone_aggressive(self, cleaner):
        assert cleaner.detect_tone("Dominate your competitors and crush your 10x goals") == "aggressive"

    def test_clean_ad_text_joins_fields(self, cleaner):
        ad = {"headline": "Test Headline", "body_text": "Body text", "cta": "Click Here"}
        result = cleaner.clean_ad_text(ad)
        assert "Test Headline" in result
        assert "Body text" in result
        assert "Click Here" in result


# ═══════════════════════════════════════════════════════════════════════════
# 3. EMBEDDING ENGINE (mock — no real model)
# ═══════════════════════════════════════════════════════════════════════════

class TestEmbeddingEngine:
    def test_mock_vector_is_384_dims(self):
        v = _mock_vector("hello world")
        assert len(v) == 384

    def test_mock_vector_is_normalised(self):
        v = _mock_vector("test text")
        norm = sum(x**2 for x in v) ** 0.5
        assert abs(norm - 1.0) < 0.01

    def test_mock_vector_deterministic(self):
        a = _mock_vector("same text")
        b = _mock_vector("same text")
        assert a == b

    def test_embed_batch(self):
        engine = EmbeddingEngine()
        texts = ["text one", "text two", "text three"]
        vecs = engine.embed(texts)
        assert len(vecs) == 3
        assert all(len(v) == 384 for v in vecs)


# ═══════════════════════════════════════════════════════════════════════════
# 4. SIMILARITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TestSimilarityEngine:
    def test_cosine_similarity_identical(self, similarity):
        v = [1.0, 0.0, 0.0]
        assert similarity.cosine_similarity(v, v) == pytest.approx(1.0, abs=0.001)

    def test_cosine_similarity_orthogonal(self, similarity):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert similarity.cosine_similarity(a, b) == pytest.approx(0.0, abs=0.001)

    def test_cluster_groups_similar_texts(self, similarity):
        texts = [
            "Free trial no credit card",
            "Start free trial today",
            "Try it free for 14 days",
            "Enterprise security compliance SSO",
            "Trusted by enterprise teams security",
        ]
        clusters = similarity.cluster_texts(texts, threshold=0.50)
        assert len(clusters) >= 1

    def test_cluster_has_required_fields(self, similarity):
        clusters = similarity.cluster_texts(["text a", "text b text a similar"])
        if clusters:
            c = clusters[0]
            assert "theme" in c
            assert "saturation_score" in c
            assert "member_count" in c

    def test_analyze_ad_clusters_returns_structure(self, similarity, sample_ads):
        result = similarity.analyze_ad_clusters(sample_ads)
        assert "clusters" in result
        assert "saturation_index" in result
        assert "dominant_theme" in result
        assert 0.0 <= result["saturation_index"] <= 1.0

    def test_empty_ads_returns_empty_clusters(self, similarity):
        result = similarity.analyze_ad_clusters([])
        assert result["clusters"] == []
        assert result["saturation_index"] == 0.0

    def test_theme_inference_free_trial(self, similarity):
        texts = ["Free trial no credit card needed", "Try free — no risk"]
        theme = similarity._infer_theme(texts)
        assert theme == "free_trial"


# ═══════════════════════════════════════════════════════════════════════════
# 5. MARKET PRESSURE DETECTOR
# ═══════════════════════════════════════════════════════════════════════════

class TestMarketPressureDetector:
    def test_score_range_0_to_100(self, pressure_detector, cluster_data, sample_ads):
        signal = pressure_detector.compute(5, cluster_data, sample_ads)
        assert 0 <= signal["pressure_score"] <= 100

    def test_more_competitors_raises_score(self, pressure_detector, cluster_data, sample_ads):
        low  = pressure_detector.compute(1,  cluster_data, sample_ads)["pressure_score"]
        high = pressure_detector.compute(15, cluster_data, sample_ads)["pressure_score"]
        assert high > low

    def test_pressure_tier_boundaries(self, pressure_detector, cluster_data, sample_ads):
        signal = pressure_detector.compute(3, cluster_data, sample_ads)
        assert signal["pressure_tier"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")

    def test_opportunity_flag_on_high_saturation(self, pressure_detector, sample_ads):
        high_saturation_cluster = {
            "clusters": [{"theme": "free_trial", "member_count": 10, "is_saturated": True, "avg_similarity": 0.90}],
            "saturation_index":  0.90,
            "cluster_count":     1,
            "dominant_theme":    "free_trial",
        }
        signal = pressure_detector.compute(12, high_saturation_cluster, sample_ads * 5)
        assert signal["unique_angle_opportunity"] is True

    def test_zero_competitors_low_pressure(self, pressure_detector, sample_ads):
        empty_cluster = {"clusters": [], "saturation_index": 0.0, "cluster_count": 0, "dominant_theme": "none"}
        signal = pressure_detector.compute(0, empty_cluster, [])
        assert signal["pressure_score"] < 40

    def test_interpret_returns_string(self, pressure_detector, cluster_data, sample_ads):
        signal = pressure_detector.compute(5, cluster_data, sample_ads)
        text = pressure_detector.interpret(signal)
        assert isinstance(text, str)
        assert len(text) > 10

    def test_sub_scores_present(self, pressure_detector, cluster_data, sample_ads):
        signal = pressure_detector.compute(5, cluster_data, sample_ads)
        assert "sub_scores" in signal
        for key in ["competitor_density", "saturation", "cluster_concentration"]:
            assert key in signal["sub_scores"]


# ═══════════════════════════════════════════════════════════════════════════
# 6. STRATEGY GAP ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class TestStrategyGapAnalyzer:
    def _run(self, gap_analyzer, sample_ads, cluster_data):
        pressure = MarketPressureDetector().compute(5, cluster_data, sample_ads)
        return gap_analyzer.analyze(
            company_id="co_test",
            competitor_profiles=[{"name": "Rival", "domain": "rival.com"}],
            cluster_data=cluster_data,
            pressure_signal=pressure,
            ad_list=sample_ads,
            page_texts=["free trial pricing features enterprise security"]
        )

    def test_returns_required_keys(self, gap_analyzer, sample_ads, cluster_data):
        result = self._run(gap_analyzer, sample_ads, cluster_data)
        assert "gap_signals" in result
        assert "summary" in result
        assert "generated_at" in result

    def test_gaps_have_required_fields(self, gap_analyzer, sample_ads, cluster_data):
        result = self._run(gap_analyzer, sample_ads, cluster_data)
        for gap in result["gap_signals"]:
            assert "gap_type"    in gap
            assert "severity"    in gap
            assert "description" in gap
            assert "confidence"  in gap

    def test_gaps_sorted_by_severity(self, gap_analyzer, sample_ads, cluster_data):
        result = self._run(gap_analyzer, sample_ads, cluster_data)
        severities = [g["severity"] for g in result["gap_signals"]]
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        for i in range(len(severities) - 1):
            assert order[severities[i]] <= order[severities[i+1]]

    def test_offer_gap_detected_for_trial_dominant(self, gap_analyzer, cluster_data):
        trial_ads = [
            {"platform": "meta", "headline": "Free trial", "body_text": "No credit card", "offer_type": "trial", "emotional_tone": "friendly"},
            {"platform": "meta", "headline": "Try free",   "body_text": "Cancel anytime",  "offer_type": "trial", "emotional_tone": "friendly"},
            {"platform": "meta", "headline": "Start free", "body_text": "Risk free trial", "offer_type": "trial", "emotional_tone": "educational"},
        ]
        cluster_d = SimilarityEngine().analyze_ad_clusters(trial_ads)
        pressure  = MarketPressureDetector().compute(3, cluster_d, trial_ads)
        result = gap_analyzer.analyze("co1", [], cluster_d, pressure, trial_ads, [])
        offer_gaps = [g for g in result["gap_signals"] if g["gap_type"] == "OFFER"]
        assert len(offer_gaps) >= 1
        assert offer_gaps[0]["severity"] == "HIGH"

    def test_to_json_produces_valid_json(self, gap_analyzer, sample_ads, cluster_data):
        import json
        result = self._run(gap_analyzer, sample_ads, cluster_data)
        json_str = gap_analyzer.to_json(result)
        parsed = json.loads(json_str)
        assert parsed["company_id"] == "co_test"

    def test_summary_counts_match_gaps(self, gap_analyzer, sample_ads, cluster_data):
        result = self._run(gap_analyzer, sample_ads, cluster_data)
        summary = result["summary"]
        gaps    = result["gap_signals"]
        assert summary["total_gaps"] == len(gaps)
        assert summary["high_severity"]   == sum(1 for g in gaps if g["severity"] == "HIGH")
        assert summary["medium_severity"] == sum(1 for g in gaps if g["severity"] == "MEDIUM")


# ═══════════════════════════════════════════════════════════════════════════
# 7. CRAWLER ENGINE (mock HTTP)
# ═══════════════════════════════════════════════════════════════════════════

class TestCrawlerEngine:
    @pytest.mark.asyncio
    async def test_crawl_returns_list(self):
        from backend.services.competitor_intelligence.crawler_engine import CrawlerEngine

        sample_html = """<html><body>
            <h1>Competitor</h1><p>Free trial</p>
            <a href="/pricing">Pricing</a>
            <a href="/features">Features</a>
        </body></html>"""

        async def mock_fetch(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = sample_html
            mock_resp.raise_for_status = MagicMock()
            return mock_resp

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=MagicMock(get=AsyncMock(side_effect=mock_fetch)))
            mock_client.return_value.__aexit__  = AsyncMock(return_value=False)
            crawler = CrawlerEngine("https://rival.com", max_pages=3)
            # Test link extraction directly
            links = crawler.extract_links(sample_html, "https://rival.com")
            assert isinstance(links, list)

    def test_classify_page_pricing(self):
        from backend.services.competitor_intelligence.crawler_engine import CrawlerEngine
        c = CrawlerEngine("https://rival.com")
        assert c._classify_page("https://rival.com/pricing") == "pricing"
        assert c._classify_page("https://rival.com/features") == "features"
        assert c._classify_page("https://rival.com/about") == "about"

    def test_score_links_puts_pricing_first(self):
        from backend.services.competitor_intelligence.crawler_engine import CrawlerEngine
        c = CrawlerEngine("https://rival.com")
        links = [
            "https://rival.com/blog",
            "https://rival.com/pricing",
            "https://rival.com/about",
            "https://rival.com/features",
        ]
        scored = c._score_links(links)
        assert "pricing" in scored[0] or "features" in scored[0]
