
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class GraphEntity(BaseModel):
    entity_id: str
    name: str
    entity_type: str = "CONCEPT"

    mention_count: int = 0
    pages: List[int] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)

    aliases: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class GraphRelation(BaseModel):
    relation_id: str
    source_entity_id: str
    target_entity_id: str

    source_name: str
    target_name: str

    relation_type: str = "RELATED_TO"
    weight: int = 1

    pages: List[int] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class DocumentGraph(BaseModel):
    document_id: str
    source_file_name: Optional[str] = None

    total_entities: int = 0
    total_relations: int = 0

    entities: List[GraphEntity] = Field(default_factory=list)
    relations: List[GraphRelation] = Field(default_factory=list)

    build_metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
