import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin, urlparse

class WebsiteCrawler:
    """
    Crawls a target competitor domain to extract key pages for intelligence gathering.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        # Focus on high-signal pages: Homepage, Pricing, Features, About
        self.target_keywords = ['pricing', 'features', 'product', 'about']

    async def fetch_page(self, url: str) -> str:
        """Fetch raw HTML content of a URL."""
        if url in self.visited:
            return ""
        
        self.visited.add(url)
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0, verify=False) as client:
                # Add typical headers to avoid basic anti-bot blocks
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 MarketingAIScraper/1.0"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return ""

    def extract_links(self, html: str) -> List[str]:
        """Extract internal links from HTML."""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(self.base_url, href)
            # Only keep exact domain internal links
            if urlparse(full_url).netloc == self.domain:
                links.append(full_url)
        return list(set(links))

    async def run_crawl(self, max_pages: int = 5) -> Dict[str, str]:
        """
        Crawls the homepage and up to `max_pages` of high-value internal links.
        Returns Dict mapping URL -> Raw HTML.
        """
        results = {}
        
        # 1. Fetch Homepage
        homepage_html = await self.fetch_page(self.base_url)
        if homepage_html:
            results[self.base_url] = homepage_html
            
        # 2. Find High-Signal Links
        internal_links = self.extract_links(homepage_html)
        priority_links = []
        
        for link in internal_links:
            if any(keyword in link.lower() for keyword in self.target_keywords):
                priority_links.append(link)
                
        # 3. Fetch Priority pages
        for link in priority_links[:max_pages - 1]: # -1 because homepage is 1
            html = await self.fetch_page(link)
            if html:
                 results[link] = html
                 
        return results
