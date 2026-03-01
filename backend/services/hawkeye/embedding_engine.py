import logging
import hashlib
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """
    Solid Matter Intelligence Layer
    Converts visual, copy, and structural logic arrays into float tensors and
    interfaces with Vector Databases (Qdrant/Pinecone) to track ad lifecycles mathematically.
    """

    def generate_embedding(self, payload: Dict[str, Any]) -> List[float]:
        """
        Fake semantic embedding generator utilizing SHA256 deterministic arrays.
        Production environment maps this identically to OpenAI Text-Embedding API or local sentence-transformers.
        """
        logger.info(f"Hawkeye abstracting intelligence schemas into float vectors...")
        raw_str = json.dumps(payload, sort_keys=True).encode("utf-8")
        hash_obj = hashlib.sha256(raw_str).digest()
        
        # Generate 16 dimensional deterministic floats for validation mocks
        vector = [(b / 255.0) for b in hash_obj[:16]]
        return vector

    def check_similarity(self, new_vector: List[float], history_vectors: List[List[float]]) -> float:
        """
        Calculates simple deterministic Cosine Similarity bounding boxes.
        Returns highest similarity score matched against historical arrays.
        """
        if not history_vectors or not new_vector:
             return 0.0
             
        max_sim = 0.0
        for vec in history_vectors:
             if len(vec) != len(new_vector):
                  continue
                  
             # Cosine similarity logic
             dot_product = sum(a * b for a, b in zip(new_vector, vec))
             norm_a = sum(a * a for a in new_vector) ** 0.5
             norm_b = sum(b * b for b in vec) ** 0.5
             
             if norm_a == 0 or norm_b == 0:
                  continue
                  
             sim = dot_product / (norm_a * norm_b)
             if sim > max_sim:
                 max_sim = sim
                 
        return max_sim
