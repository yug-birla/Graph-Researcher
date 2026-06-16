from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class DocumentStatus(BaseModel):
    document_id: str
    source_file_name: str
    file_type: Optional[str] = None

    status: str
    current_stage: str

    message: str
    error_message: Optional[str] = None

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)
