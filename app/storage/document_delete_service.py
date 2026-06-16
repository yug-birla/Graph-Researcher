import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings
from app.storage.status_storage import read_document_status
from app.storage.processed_storage import read_processed_metadata
from app.storage.document_index import remove_document_from_index


def delete_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    document_dir = settings.PROCESSED_DIR / document_id

    status = read_document_status(document_id)
    metadata = read_processed_metadata(document_id)

    if status is None and metadata is None and not document_dir.exists():
        return None

    raw_upload_path = None

    if status is not None:
        raw_upload_path = status.metadata.get("uploaded_file_path")

    removed_index_entry = remove_document_from_index(document_id)

    deleted_vectors = False

    try:
        from app.retrieval.vector_store import delete_vectors_for_document

        delete_vectors_for_document(document_id)
        deleted_vectors = True
    except Exception:
        deleted_vectors = False

    deleted_raw_upload = False
    deleted_processed_folder = False

    if raw_upload_path:
        raw_path = Path(raw_upload_path)

        if raw_path.exists() and raw_path.is_file():
            raw_path.unlink()
            deleted_raw_upload = True

    if document_dir.exists() and document_dir.is_dir():
        shutil.rmtree(document_dir)
        deleted_processed_folder = True

    return {
        "document_id": document_id,
        "source_file_name": (
            status.source_file_name if status is not None
            else metadata.get("source_file_name") if metadata is not None
            else None
        ),
        "file_type": (
            status.file_type if status is not None
            else metadata.get("file_type") if metadata is not None
            else None
        ),
        "deleted_processed_folder": deleted_processed_folder,
        "deleted_raw_upload": deleted_raw_upload,
        "deleted_vectors": deleted_vectors,
        "removed_duplicate_index_entry": removed_index_entry is not None,
        "removed_index_entry": removed_index_entry
    }
