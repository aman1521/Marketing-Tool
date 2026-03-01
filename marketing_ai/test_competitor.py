import asyncio
from app.services.competitor_intelligence.crawler import WebsiteCrawler
from app.services.competitor_intelligence.content_cleaner import ContentCleaner
from app.services.competitor_intelligence.pageindex_adapter import PageIndexAdapter
from app.services.competitor_intelligence.analyzer import CompetitorAnalyzer

async def run_test():
    print("1. Crawling mock competitor: https://stripe.com")
    crawler = WebsiteCrawler(base_url="https://stripe.com")
    pages = await crawler.run_crawl(max_pages=2)
    
    print(f"   Found {len(pages)} pages.")
    
    print("2. Cleaning and Chunking...")
    adapter = PageIndexAdapter()
    all_chunks = []
    for url, html in pages.items():
        clean_text = ContentCleaner.clean_html(html)
        chunks = adapter.chunk_text(clean_text)
        all_chunks.extend(chunks)
        
    print(f"   Generated {len(all_chunks)} semantic chunks.")
    
    if len(all_chunks) == 0:
        print("   No text chunks to analyze. Exiting.")
        return
        
    print("3. Sending to Claude for Gap Analysis...")
    analyzer = CompetitorAnalyzer()
    report = await analyzer.generate_gap_report("My Fast SaaS Enterprise", all_chunks)
    
    print("\n\n======== COMPLETED GAP REPORT ========\n")
    print(report)
    print("\n========================================")

if __name__ == "__main__":
    asyncio.run(run_test())
