from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from app.config import settings
from typing import List, Dict, Any
import uuid

class CompetitorQdrantDB:
    """
    Handles Vector Database Operations for Storing and Querying Embeddings.
    Screaming fast cosine similarity mapping of the SaaS positioning.
    """
    
    COLLECTION_NAME = "competitor_intelligence"

    def __init__(self):
        # Using Docker service name 'qdrant'
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    async def init_collection(self):
        """Creates the Qdrant Collection with 1536 OpenAI dims if not exists"""
        # In modern Qdrant, check if collection exists first
        collections = await self.client.get_collections()
        exists = any(col.name == self.COLLECTION_NAME for col in collections.collections)
        
        if not exists:
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    async def insert_embeddings(self, company_id: str, competitor_domain: str, page_type: str, embeddings: List[Dict[str, Any]]):
        """
        Takes the [{chunk: str, vector: [float]}] array and stores them inside Qdrant mapping to company_id.
        """
        await self.init_collection()
        points = []
        for em in embeddings:
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=em["vector"],
                    payload={
                        "company_id": company_id,
                        "competitor_domain": competitor_domain,
                        "page_type": page_type,
                        "text_chunk": em["chunk"]
                    }
                )
            )
        
        await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            wait=True,
            points=points
        )

    async def search_similar(self, company_id: str, query_vector: List[float], limit: int = 5) -> List[Any]:
        """Query Qdrant by cosine similarity using Client's embedding against competition"""
        search_result = await self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter={
                 "must": [
                     {
                         "key": "company_id",
                         "match": {"value": company_id} 
                     }
                 ]
            },
            limit=limit,
            with_payload=True
        )
        return search_result
