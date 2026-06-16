from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ContentChunk(BaseModel):
    chunk_id: str
    document_id: str
    parent_block_id: str

    content_type: str
    content: str

    chunk_index: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    source_file_name: str

    start_char: Optional[int] = None
    end_char: Optional[int] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)
