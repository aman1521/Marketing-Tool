"""
Knowledge Embeddings
====================
Takes loaded Markdown Playbooks and segments them into semantic chunks
before injecting them into OpenAI's text-embedding-3-small and saving to Qdrant.
"""

import os
import logging
import uuid
from typing import Dict, List, Optional
try:
    from openai import AsyncOpenAI
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qdrant_models
except ImportError:
    pass

from .models import SkillObject, KnowledgeEmbedding

logger = logging.getLogger(__name__)

class KnowledgeEmbedder:
    """Pipelines SkillObjects into Vector Space for AI Retrieval."""

    def __init__(self):
        """Initializes Embeddings config and Qdrant backend mappings."""
        self.embedding_model = "text-embedding-3-small"
        self.collection_name = "marketing_skills"
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    async def generate_embedding(self, text: str) -> List[float]:
        """Calls OpenAI explicitly to map the text to a vector point."""
        try:
            client = AsyncOpenAI(api_key=self.openai_api_key)
            response = await client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[KnowledgeEmbedder] Failed to generate embedding: {e}")
            return []

    async def store_skill(self, skill: SkillObject) -> bool:
        """
        Chunks the playbook string, maps chunks to vectors, and injects into Qdrant.
        """
        if not self.openai_api_key:
             logger.warning("[KnowledgeEmbedder] Skipping skill indexing (No OpenAI Key)")
             return False
             
        # Combine instructions and examples for holistic context mapping
        full_text = skill.title + "\n" + "\n".join(skill.instructions) + "\n" + "\n".join(skill.examples)
        
        # We assume 1 chunk per playbook for simplicity since these are concise schemas
        vector = await self.generate_embedding(full_text)
        if not vector:
            return False

        record = KnowledgeEmbedding(
            skill_name=skill.name,
            chunk_id=str(uuid.uuid4()),
            content_chunk=full_text,
            embedding_vector=vector,
            metadata={"title": skill.title, "length": len(full_text)}
        )

        try:
             # Connect to Vector DB
             qdrant = AsyncQdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
             
             # Create collection if missing
             try:
                 await qdrant.get_collection(self.collection_name)
             except:
                 await qdrant.create_collection(
                     collection_name=self.collection_name,
                     vectors_config=qdrant_models.VectorParams(
                         size=1536, # OpenAI small dimensions
                         distance=qdrant_models.Distance.COSINE
                     )
                 )

             # Upsert the chunk
             payload = {
                 "skill_name": record.skill_name,
                 "content": record.content_chunk,
                 **record.metadata
             }

             await qdrant.upsert(
                 collection_name=self.collection_name,
                 points=[
                     qdrant_models.PointStruct(
                         id=record.chunk_id,
                         vector=record.embedding_vector,
                         payload=payload
                     )
                 ]
             )
             logger.info(f"[KnowledgeEmbedder] Stored `{skill.name}` Vector Profile successfully.")
             return True

        except Exception as e:
             logger.error(f"[KnowledgeEmbedder] Failed storing skill to Qdrant: {e}")
             return False
