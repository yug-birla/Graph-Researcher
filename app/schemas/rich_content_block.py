from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RichContentBlock(BaseModel):
    block_id: str
    document_id: str
    content_type: str
    content: str

    page_number: Optional[int] = None
    section_title: Optional[str] = None
    source_file_name: str

    metadata: Dict[str, Any] = Field(default_factory=dict)
