from pydantic import BaseModel
from typing import Optional, Dict, Any


class SourceCitation(BaseModel):
    source_id: str
    chunk_id: str
    document_id: str
    source_file_name: str

    page_number: Optional[int] = None
    section_title: Optional[str] = None
    content_type: str

    score: Optional[float] = None
    citation_text: str
    content_preview: str

    metadata: Dict[str, Any] = {}
