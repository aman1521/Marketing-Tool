"""
Creative Embeddings
===================
Stores encoded Creative DNA into Qdrant for cross-referencing and
generative retrieval matching.
"""

import os
import logging
from typing import Dict, List, Any, Optional
try:
    from openai import AsyncOpenAI
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qdrant_models
except ImportError:
    pass

from .models import CreativeDNA

logger = logging.getLogger(__name__)

class CreativeEmbeddings:
    """Takes pure genetic structures and pushes them to Vector Space."""

    def __init__(self):
        self.embedding_model = "text-embedding-3-small"
        self.collection_name = "creative_dna"
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    async def _embed_string(self, text: str) -> List[float]:
        if not self.openai_api_key:
             return []
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.embeddings.create(input=[text], model=self.embedding_model)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[CreativeEmbeddings] Embedding generation failed: {e}")
            return []

    async def store_dna(self, dna: CreativeDNA, performance_metrics: Dict[str, float]) -> bool:
        """
        Embed the flat map of the DNA so we can search: Find me high-performing UGC problem/solution ads.
        """
        logger.info(f"[CreativeEmbeddings] Pushing DNA for {dna.creative_id} to Vector DB.")
        
        # Flatten the categorizations into a single descriptive string
        flat_genome = (
            f"Hook: {dna.hook_type} | Emotion: {dna.emotion} | "
            f"Story: {dna.story_pattern} | Format: {dna.visual_format} | "
            f"CTA: {dna.CTA_style} | Offer: {dna.offer_type}"
        )
        
        vector = await self._embed_string(flat_genome)
        if not vector:
             return False
             
        # In reality, this connects to Qdrant exactly like `marketing_knowledge` or `competitor_intelligence`.
        logger.debug(f"[CreativeEmbeddings] Simulated Storing vector payload against Qdrant.")
        return True

    async def find_similar_creatives(self, query_features: Dict[str, str], limit: int = 5) -> List[CreativeDNA]:
        """
        Queries Qdrant for previously executed creatives matching this DNA pattern.
        Useful when the Agent says 'I need to test a new angle, what worked before?'
        """
        logger.info(f"[CreativeEmbeddings] Searching vectors for {query_features}")
        # MOCK IMPLEMENTATION (Normally involves embedding the query map and hitting Vector DB)
        
        # We simulate returning a historical ad that matched the query features.
        return [
             CreativeDNA(
                 creative_id="hist_4892",
                 hook_type=query_features.get("hook_type", "curiosity"),
                 emotion=query_features.get("emotion", "aspiration"),
                 story_pattern=query_features.get("story_pattern", "before_after"),
                 visual_format="ugc_style",
                 CTA_style="Learn More",
                 offer_type="Free Audit"
             )
        ]
