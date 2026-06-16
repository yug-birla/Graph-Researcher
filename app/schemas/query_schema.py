
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[str] = None

    top_k: int = Field(default=5, ge=1, le=20)
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"

    use_reranker: bool = True
    use_llm: bool = True

    # Phase 15:
    # Adds graph context from entities and relations when document graph exists.
    use_graph: bool = True
    graph_entity_limit: int = Field(default=8, ge=1, le=30)
