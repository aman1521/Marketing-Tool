"""
Creative Parser
===============
Extracts structural blocks (Hook, Body, CTA, Offer) from raw text/transcripts.
"""

import logging
from typing import Dict, Any, Optional

from .models import Creative, CreativeStructure

logger = logging.getLogger(__name__)

class CreativeParser:
    """Uses heuristical or zero-shot LLM logic to split an ad logically."""

    async def parse_structure(self, creative: Creative) -> CreativeStructure:
        """
        Deconstructs the ad copy into 4 core functional blocks.
        """
        logger.debug(f"[CreativeParser] Deconstructing ad ID {creative.id}")
        
        # MOCK IMPLEMENTATION
        # An actual LLM call here would be to OpenAI extracting the JSON parts.
        
        full_text = creative.ad_text + "\n" + (creative.headline or "")
        
        # Naive split logic for simulation
        sentences = [s.strip() for s in full_text.split('.') if s.strip()]
        
        hook = sentences[0] if sentences else "Unknown Hook"
        cta = sentences[-1] if len(sentences) > 1 else "Learn More"
        body = " ".join(sentences[1:-1]) if len(sentences) > 2 else "Product highlights."
        offer = "7-Day Free Trial" if "trial" in full_text.lower() else "Standard"

        struct = CreativeStructure(
            hook=hook,
            body_message=body,
            CTA=cta,
            offer=offer
        )
        return struct
