"""
Retrieval Engine
================
AI agents query this engine with standard English contexts 
(e.g., 'We have a high bounce rate on SaaS trials'). 
It pings Qdrant to pull back the exactly correct loaded Skill Playbook names.
"""

import os
import logging
from typing import Dict, List, Optional
try:
    from openai import AsyncOpenAI
    from qdrant_client import AsyncQdrantClient
except ImportError:
    pass

from .models import MarketingContext, SkillRegistryItem
from .skill_registry import SkillRegistry

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """Uses Semantic Search to map current Strategy problems to stored AI Playbooks."""

    def __init__(self):
        self.registry = SkillRegistry()
        self.embedding_model = "text-embedding-3-small"
        self.collection_name = "marketing_skills"
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    async def _embed_context(self, context: MarketingContext) -> List[float]:
        """Flatten context into a query string for vector mapping."""
        query_string = f"Goal: {context.campaign_goal} | Problem: {context.current_problem} | Audience: {context.audience}"
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.embeddings.create(
                input=[query_string],
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[Retrieval] Fallback embedding failed: {e}")
            return []

    async def retrieve_relevant_skills(self, context: MarketingContext, top_k: int = 2) -> List[SkillRegistryItem]:
        """Searches vector DB for the highest similarity playbooks matching the context."""
        logger.info(f"[Retrieval] Extracting playbooks for problem: {context.current_problem}")
        
        # MOCK VECTOR BYPASS (No API Key mode for local testing)
        if not self.openai_api_key or not self.qdrant_url:
            logger.warning("[Retrieval] No external connections found. Falling back to explicit substring match.")
            all_skills = self.registry.get_all_skills()
            problem = (context.current_problem or "").lower()
            
            # Simple fallback heuristic router
            if "conversion" in problem or "landing_page" in problem:
                 return [s for s in all_skills if s.name == "CRO Analysis"]
            if "copy" in problem or "fatigue" in problem:
                 return [s for s in all_skills if s.name == "Copywriting Frameworks"]
            if "idea" in problem or "growth" in problem:
                 return [s for s in all_skills if s.skill_type == "experimentation"]
                 
            return all_skills[:top_k]

        # -------------------------------------------------------------
        # Physical Vector Integration (Production)
        # -------------------------------------------------------------
        query_vector = await self._embed_context(context)
        if not query_vector:
             # Fallback
             return []

        try:
            qdrant = AsyncQdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
            search_result = await qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=0.65 # Require decent similarity
            )
            
            # Map Qdrant ID back to our SkillRegistry list
            retrieved_skills = []
            for hit in search_result:
                skill_name = hit.payload.get("skill_name")
                if skill_name:
                    registry_item = self.registry.get_skill(skill_name)
                    if registry_item:
                        retrieved_skills.append(registry_item)

            if retrieved_skills:
                logger.debug(f"[Retrieval] Hits: {[s.name for s in retrieved_skills]}")
                return retrieved_skills
            else:
                return []
                
        except Exception as e:
            logger.error(f"[Retrieval] Qdrant semantic search failed. Mapping empty: {e}")
            return []
