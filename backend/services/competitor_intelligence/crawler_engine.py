"""
Crawler Engine
==============
Async website crawler — extends and productionises the existing WebsiteCrawler.
Targets high-signal pages: homepage, pricing, features, about, blog.
Respects rate limits. Tenant-isolated.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Pages we want most for competitive intelligence
HIGH_SIGNAL_KEYWORDS = [
    "pricing", "price", "features", "product", "about", "solution",
    "platform", "compare", "vs", "versus", "why", "case-study",
    "customers", "blog", "resources"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

CRAWL_TIMEOUT = 20.0
MAX_CONCURRENT = 3


class CrawlerEngine:
    """
    Production async crawler for competitive intelligence.
    Returns structured page records, not raw HTML blobs.
    """

    def __init__(self, base_url: str, max_pages: int = 8,
                 rate_limit_seconds: float = 1.0):
        self.base_url = base_url.rstrip("/")
        self.domain   = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.rate_limit = rate_limit_seconds
        self.visited: set = set()

    # ── Core fetch ─────────────────────────────────────────

    async def fetch(self, url: str, client: httpx.AsyncClient) -> Tuple[str, int]:
        """Fetch a URL. Returns (html, status_code)."""
        if url in self.visited:
            return "", 0
        self.visited.add(url)
        try:
            resp = await client.get(url, headers=HEADERS, follow_redirects=True, timeout=CRAWL_TIMEOUT)
            return resp.text, resp.status_code
        except Exception as exc:
            logger.warning(f"Fetch failed [{url}]: {exc}")
            return "", 0

    # ── Link extraction ─────────────────────────────────────

    def extract_links(self, html: str, source_url: str) -> List[str]:
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all("a", href=True):
            full = urljoin(source_url, tag["href"])
            parsed = urlparse(full)
            if parsed.netloc == self.domain and parsed.scheme in ("http", "https"):
                clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                links.append(clean)
        return list(set(links))

    def _classify_page(self, url: str) -> str:
        low = url.lower()
        for kw in HIGH_SIGNAL_KEYWORDS:
            if kw in low:
                return kw
        return "general"

    def _score_links(self, links: List[str]) -> List[str]:
        """Prioritise high-signal URLs."""
        priority, rest = [], []
        for l in links:
            low = l.lower()
            if any(k in low for k in ["pricing", "features", "compare", "vs"]):
                priority.append(l)
            else:
                rest.append(l)
        return priority + rest

    # ── Public crawl ────────────────────────────────────────

    async def crawl(self) -> List[Dict]:
        """
        Full async crawl.
        Returns list of page records:
          {url, page_type, html, status, length}
        """
        results = []
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        async with httpx.AsyncClient(verify=False) as client:

            # Step 1: Homepage
            html, status = await self.fetch(self.base_url, client)
            if html:
                results.append({
                    "url":       self.base_url,
                    "page_type": "homepage",
                    "html":      html,
                    "status":    status,
                    "length":    len(html)
                })

            # Step 2: Discover and score links
            all_links = self._score_links(self.extract_links(html, self.base_url))
            targets = all_links[: self.max_pages - 1]

            # Step 3: Concurrent fetch with rate limiting
            async def fetch_with_limit(url: str):
                async with semaphore:
                    await asyncio.sleep(self.rate_limit)
                    page_html, page_status = await self.fetch(url, client)
                    if page_html:
                        return {
                            "url":       url,
                            "page_type": self._classify_page(url),
                            "html":      page_html,
                            "status":    page_status,
                            "length":    len(page_html)
                        }
                    return None

            tasks = [fetch_with_limit(u) for u in targets]
            pages = await asyncio.gather(*tasks, return_exceptions=True)

            for p in pages:
                if isinstance(p, dict):
                    results.append(p)

        logger.info(f"Crawled [{self.base_url}] → {len(results)} pages")
        return results
