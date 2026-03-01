from fastapi import APIRouter, HTTPException
from app.services.competitor_intelligence.crawler import WebsiteCrawler
from app.services.competitor_intelligence.content_cleaner import ContentCleaner
from app.services.competitor_intelligence.pageindex_adapter import PageIndexAdapter
from app.services.competitor_intelligence.analyzer import CompetitorAnalyzer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze")
async def analyze_competitor(url: str, company_name: str = "My SaaS"):
    """
    Triggers Crawler -> ContentCleaner -> PageIndex (Embeddings)
    and then immediately runs Claude to output a Gap Report based on chunks.
    """
    try:
        # Step 1: Crawl
        logger.info(f"Crawling {url}...")
        crawler = WebsiteCrawler(base_url=url)
        pages_dict = await crawler.run_crawl(max_pages=3)
        
        if not pages_dict:
            raise HTTPException(status_code=400, detail="Failed to scrape any content from domain.")
            
        # Step 2: Clean and Chunk
        adapter = PageIndexAdapter()
        all_chunks = []
        for raw_html in pages_dict.values():
            clean_text = ContentCleaner.clean_html(raw_html)
            chunks = adapter.chunk_text(clean_text)
            all_chunks.extend(chunks)
            
        # Optional Step 3: We can embed them into Qdrant using adapter.generate_embeddings(all_chunks)
        # For instant reporting to the user, we'll route straight to Claude right now
        
        # Step 4: Claude strategic analysis
        analyzer = CompetitorAnalyzer()
        gap_report_md = await analyzer.generate_gap_report(company_name, all_chunks)
        
        return {
            "status": "success",
            "competitor_url": url,
            "pages_scraped": list(pages_dict.keys()),
            "total_chunks_processed": len(all_chunks),
            "gap_analysis": gap_report_md
        }
        
    except Exception as e:
        logger.error(f"Competitor Intelligence Pipeline Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gap-report")
async def gap_report(competitor_id: str):
    # Stub for future feature where reports are cached in the DB
    return {"status": "Use POST /analyze to generate dynamic reports for now."}
