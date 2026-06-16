from pydantic import BaseModel, Field
from typing import Optional, Literal


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)

    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"

    use_reranker: bool = True
    use_llm: bool = True
