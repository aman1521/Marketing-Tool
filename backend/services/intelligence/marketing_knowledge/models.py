"""
Marketing Knowledge Engine Models
===================================
Data structures representing the modular skills, execution results, 
and embeddings used by the AI Agent council to retrieve marketing playbooks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MarketingContext(BaseModel):
    """Context built to retrieve the proper marketing skills."""
    product_type: str = "unknown"
    audience: str = "unknown"
    campaign_goal: str = "unknown"
    platform: str = "unknown"
    current_problem: Optional[str] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)

class SkillObject(BaseModel):
    """A fully loaded and parsed marketing playbook skill."""
    name: str
    title: str
    description: str
    frameworks: List[Dict[str, str]] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    raw_markdown: str

class SkillRegistryItem(BaseModel):
    """Registry pointer for a specific marketing skill."""
    name: str
    description: str
    skill_type: str
    input_requirements: List[str]
    output_format: str

class KnowledgeEmbedding(BaseModel):
    """Vector database representation of a skill chunk."""
    skill_name: str
    chunk_id: str
    content_chunk: str
    embedding_vector: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SkillResult(BaseModel):
    """The structured LLM output after executing a playbook against an Environment Context."""
    skill_used: str
    analysis: str
    recommendations: List[str]
    expected_impact: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    proposed_actions: List[Dict[str, Any]] = Field(default_factory=list)

class SkillExecutionLog(BaseModel):
    """Persistence model tracking how/when the AI uses marketing skills."""
    skill_name: str
    context_summary: str
    result_analysis: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
