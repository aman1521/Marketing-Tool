"""
Competitor Intelligence Engine — Orchestrator
=============================================
End-to-end pipeline coordinator.
Wires: Registry → Crawler → Ad Capture → Clean → Embed → Cluster → Pressure → Gap

Produces signals only. No execution side effects.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from .competitor_registry    import CompetitorRegistry
from .crawler_engine         import CrawlerEngine
from .ad_capture_engine      import AdCaptureEngine
from .content_cleaner        import ContentCleaner
from .embedding_engine       import EmbeddingEngine
from .similarity_engine      import SimilarityEngine
from .market_pressure_detector import MarketPressureDetector
from .strategy_gap_analyzer  import StrategyGapAnalyzer

logger = logging.getLogger(__name__)


class CompetitorIntelligenceEngine:
    """Full intelligence pipeline orchestrator."""

    def __init__(self):
        self.registry   = CompetitorRegistry()
        self.cleaner    = ContentCleaner()
        self.embedder   = EmbeddingEngine()
        self.similarity = SimilarityEngine()
        self.pressure   = MarketPressureDetector()
        self.gap        = StrategyGapAnalyzer()

    async def run(self, company_id: str,
                  competitor_domain: str,
                  competitor_name: str = "",
                  max_pages: int = 6) -> Dict[str, Any]:
        """
        Full single-competitor analysis pipeline.
        Returns complete intelligence payload.
        """
        logger.info(f"[CIE] Starting pipeline for [{competitor_domain}] | company=[{company_id}]")

        # 1. Register
        profile = self.registry.register(
            company_id=company_id,
            name=competitor_name or competitor_domain,
            domain=competitor_domain
        )
        competitor_id = profile["id"]

        # 2. Crawl website
        crawler = CrawlerEngine(
            base_url=f"https://{competitor_domain}" if not competitor_domain.startswith("http") else competitor_domain,
            max_pages=max_pages
        )
        pages = await crawler.crawl()
        self.registry.mark_crawled(company_id, competitor_domain)

        # 3. Capture ads (concurrent with page processing)
        ad_task = asyncio.create_task(
            AdCaptureEngine().capture_all(competitor_domain)
        )

        # 4. Clean and chunk pages
        all_chunks, page_texts = [], []
        for page in pages:
            clean = self.cleaner.clean_html(page["html"])
            page_texts.append(clean)
            chunks = self.cleaner.chunk_text(clean)
            all_chunks.extend(chunks)

            # 5. Embed + store chunks
            self.embedder.store_page_chunks(
                competitor_id=competitor_id,
                company_id=company_id,
                chunks=chunks,
                metadata={"url": page["url"], "page_type": page["page_type"]}
            )

        # 6. Get ads
        ads = await ad_task
        for ad in ads:
            ad_text = self.cleaner.clean_ad_text(ad)
            # Enrich tone / offer if not already detected
            if not ad.get("emotional_tone"):
                ad["emotional_tone"] = self.cleaner.detect_tone(ad_text)
            if not ad.get("offer_type"):
                ad["offer_type"] = self.cleaner.detect_offer_type(ad_text)
            pid = self.embedder.store_ad_creative(competitor_id, company_id, ad, ad_text)
            ad["qdrant_point_id"] = pid

        # 7. Cluster analysis
        cluster_data = self.similarity.analyze_ad_clusters(ads)

        # 8. Market pressure
        competitors = self.registry.list_competitors(company_id)
        pressure_signal = self.pressure.compute(
            competitor_count=len(competitors),
            cluster_data=cluster_data,
            ad_list=ads
        )
        pressure_signal["interpretation"] = self.pressure.interpret(pressure_signal)

        # 9. Strategy gaps
        gap_analysis = self.gap.analyze(
            company_id=company_id,
            competitor_profiles=competitors,
            cluster_data=cluster_data,
            pressure_signal=pressure_signal,
            ad_list=ads,
            page_texts=page_texts
        )

        result = {
            "company_id":      company_id,
            "competitor_id":   competitor_id,
            "competitor_name": competitor_name or competitor_domain,
            "domain":          competitor_domain,
            "pages_crawled":   len(pages),
            "chunks_embedded": len(all_chunks),
            "ads_captured":    len(ads),
            "cluster_analysis": cluster_data,
            "market_pressure":  pressure_signal,
            "strategy_gaps":    gap_analysis,
            "pipeline": "CIE v1.0 | crawl→embed→cluster→pressure→gap"
        }

        logger.info(
            f"[CIE] Complete: {len(pages)} pages | {len(ads)} ads | "
            f"pressure={pressure_signal['pressure_score']}/100 | "
            f"gaps={gap_analysis['summary']['total_gaps']}"
        )
        return result
