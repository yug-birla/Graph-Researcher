import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.document_status import DocumentStatus


def get_status_path(document_id: str):
    document_dir = settings.PROCESSED_DIR / document_id
    document_dir.mkdir(parents=True, exist_ok=True)
    return document_dir / "status.json"


def create_document_status(
    document_id: str,
    source_file_name: str,
    file_type: Optional[str] = None
) -> DocumentStatus:

    status = DocumentStatus(
        document_id=document_id,
        source_file_name=source_file_name,
        file_type=file_type,
        status="processing",
        current_stage="uploaded",
        message="File uploaded successfully."
    )

    save_status(status)
    return status


def update_document_status(
    document_id: str,
    status: str,
    current_stage: str,
    message: str,
    file_type: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> DocumentStatus:

    existing_status = read_document_status(document_id)

    if existing_status is None:
        source_file_name = "unknown"
        existing_metadata = {}
        created_at = datetime.now(timezone.utc).isoformat()
        existing_file_type = None
    else:
        source_file_name = existing_status.source_file_name
        existing_metadata = existing_status.metadata
        created_at = existing_status.created_at
        existing_file_type = existing_status.file_type

    if metadata:
        existing_metadata.update(metadata)

    updated_status = DocumentStatus(
        document_id=document_id,
        source_file_name=source_file_name,
        file_type=file_type or existing_file_type,
        status=status,
        current_stage=current_stage,
        message=message,
        error_message=error_message,
        created_at=created_at,
        updated_at=datetime.now(timezone.utc).isoformat(),
        metadata=existing_metadata
    )

    save_status(updated_status)
    return updated_status


def save_status(status: DocumentStatus) -> None:
    status_path = get_status_path(status.document_id)

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status.model_dump(), f, indent=2, ensure_ascii=False)


def read_document_status(document_id: str) -> Optional[DocumentStatus]:
    status_path = get_status_path(document_id)

    if not status_path.exists():
        return None

    with open(status_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return DocumentStatus(**data)


def list_document_statuses() -> List[DocumentStatus]:
    if not settings.PROCESSED_DIR.exists():
        return []

    statuses = []

    for document_dir in settings.PROCESSED_DIR.iterdir():
        if not document_dir.is_dir():
            continue

        status_path = document_dir / "status.json"

        if not status_path.exists():
            continue

        try:
            with open(status_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            statuses.append(DocumentStatus(**data))
        except Exception:
            continue

    statuses.sort(key=lambda item: item.updated_at, reverse=True)
    return statuses
