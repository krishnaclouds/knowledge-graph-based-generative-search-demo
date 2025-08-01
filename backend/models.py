from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="The search query")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to return")

class NodeData(BaseModel):
    id: int
    text: str
    labels: List[str]
    name: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    topic: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    type: Optional[str] = None
    citations: Optional[int] = None
    doi: Optional[str] = None

class SearchResult(BaseModel):
    node: NodeData
    similarity: float

class Citation(BaseModel):
    source: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    
class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    answer: str
    citations: List[Citation] = []


class HealthStatus(BaseModel):
    status: str
    db: Optional[int] = None
    detail: Optional[str] = None

# LLM Judge Models
class SourceCounts(BaseModel):
    documents: int = 0
    citations: int = 0
    knowledge_graph: int = 0

class SearchSummary(BaseModel):
    summary: str
    source_counts: SourceCounts

class EvaluationRequest(BaseModel):
    query: str
    # Blind evaluation - no method identification
    summary_a: str
    summary_b: str
    evaluation_criteria: List[str] = []

class CriteriaScores(BaseModel):
    summary_a: int = Field(..., ge=1, le=10)
    summary_b: int = Field(..., ge=1, le=10)

class EvaluationResponse(BaseModel):
    winner: str = Field(..., pattern="^(summary_a|summary_b)$")
    confidence: int = Field(..., ge=1, le=100)
    reasoning: str
    criteria_scores: Dict[str, CriteriaScores]