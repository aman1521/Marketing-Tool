from typing import List, Dict, Any
import openai
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class PageIndexAdapter:
    """
    Handles unstructured clean text string limits.
    Chunks content intelligently, creates embeddings using OpenAI API.
    Provides semantic search capability across chunks.
    """
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.chunk_size = 500  # Default chunk token approximation limit

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits clean text output into PageIndex overlapping chunks.
        """
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - 50): # 50 words overlap
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        return chunks

    async def generate_embeddings(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Receives PageIndex chunks and returns OpenAI Vector Embeddings (1536 dimensions).
        """
        embeddings_payload = []
        
        try:
            # Note: For production batch 10-20 at a time to avoid rate limits
            response = await self.client.embeddings.create(
                input=chunks,
                model="text-embedding-3-small" # Fast, cheap, 1536 dim
            )
            
            for index, obj in enumerate(response.data):
                embeddings_payload.append({
                    "chunk": chunks[index],
                    "vector": obj.embedding
                })
                
            return embeddings_payload
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return []
