"""
Content Cleaner
===============
Strips HTML noise, normalises text, and chunks content into
embedding-ready segments.

Extends the existing content_cleaner.py in marketing_ai but
is fully standalone and production-hardened.
"""

import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Chunk config
CHUNK_SIZE    = 400    # words per chunk
CHUNK_OVERLAP = 60     # word overlap between chunks

# Tags that carry high signal
HIGH_SIGNAL_TAGS = ["h1", "h2", "h3", "h4", "p", "li", "blockquote", "span"]

# Boilerplate patterns to strip
BOILERPLATE = re.compile(
    r"(cookie policy|privacy policy|terms of service|copyright \d{4}|"
    r"all rights reserved|subscribe to our newsletter|follow us on|"
    r"\d{1,2}/\d{1,2}/\d{2,4})",
    flags=re.IGNORECASE
)

WHITESPACE = re.compile(r"\s{2,}")


class ContentCleaner:
    """Cleans raw HTML and produces embedding-ready text chunks."""

    # ── HTML → clean text ─────────────────────────────────────────

    @staticmethod
    def clean_html(raw_html: str) -> str:
        """Extract meaningful text from raw HTML."""
        if not raw_html:
            return ""
        try:
            soup = BeautifulSoup(raw_html, "html.parser")

            # Remove script / style / nav / footer noise
            for tag in soup.find_all(["script", "style", "nav", "footer",
                                       "header", "noscript", "meta", "link",
                                       "iframe", "svg"]):
                tag.decompose()

            # Extract from high-signal tags
            texts = []
            for tag in soup.find_all(HIGH_SIGNAL_TAGS):
                t = tag.get_text(separator=" ", strip=True)
                if t and len(t) > 15:
                    texts.append(t)

            combined = " ".join(texts)
            combined = BOILERPLATE.sub("", combined)
            combined = WHITESPACE.sub(" ", combined).strip()
            return combined
        except Exception as exc:
            logger.warning(f"HTML clean error: {exc}")
            return ""

    @staticmethod
    def clean_ad_text(ad: dict) -> str:
        """Concatenate ad fields into a single clean string for embedding."""
        parts = [
            ad.get("headline", ""),
            ad.get("body_text", ""),
            ad.get("cta", ""),
            ad.get("offer_type", ""),
            ad.get("emotional_tone", ""),
        ]
        return " | ".join(p for p in parts if p)

    # ── Chunking ──────────────────────────────────────────────────

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
                   overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping word-window chunks."""
        words = text.split()
        if not words:
            return []
        chunks = []
        step   = chunk_size - overlap
        for i in range(0, max(1, len(words) - overlap), step):
            window = words[i: i + chunk_size]
            chunk  = " ".join(window)
            if len(chunk) > 30:   # skip trivially short chunks
                chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
        return chunks

    # ── Normalisation helpers ─────────────────────────────────────

    @staticmethod
    def normalise(text: str) -> str:
        """Lowercase, collapse whitespace, strip non-ASCII."""
        text = text.lower()
        text = re.sub(r"[^\x00-\x7f]", " ", text)
        text = WHITESPACE.sub(" ", text)
        return text.strip()

    @staticmethod
    def detect_offer_type(text: str) -> str:
        """Heuristic offer type detection from cleaned text."""
        low = text.lower()
        if any(w in low for w in ["free trial", "try free", "no credit card"]):
            return "trial"
        if any(w in low for w in ["demo", "book a demo", "request demo"]):
            return "demo"
        if any(w in low for w in ["% off", "discount", "save", "limited offer"]):
            return "discount"
        if any(w in low for w in ["download", "ebook", "guide", "report", "whitepaper"]):
            return "content"
        return "direct"

    @staticmethod
    def detect_tone(text: str) -> str:
        """Heuristic emotional tone detection."""
        low = text.lower()
        score = {"aggressive": 0, "educational": 0, "premium": 0, "friendly": 0}
        score["aggressive"]  += sum(1 for w in ["dominate", "crush", "beat", "10x", "explode", "fastest"] if w in low)
        score["educational"] += sum(1 for w in ["learn", "guide", "how to", "understand", "insight"] if w in low)
        score["premium"]     += sum(1 for w in ["enterprise", "trusted", "leader", "#1", "award", "top"] if w in low)
        score["friendly"]    += sum(1 for w in ["easy", "simple", "help", "love", "join", "community"] if w in low)
        return max(score, key=score.get)
