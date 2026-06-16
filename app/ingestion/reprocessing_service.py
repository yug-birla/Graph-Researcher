import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from app.ingestion.file_detector import detect_file_type
from app.ingestion.parser_registry import parser_registry
from app.chunking.chunking_service import chunk_blocks
from app.storage.processed_storage import save_processed_document
from app.storage.status_storage import (
    read_document_status,
    update_document_status
)
from app.storage.document_index import register_document_hash


def calculate_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def reprocess_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    existing_status = read_document_status(document_id)

    if existing_status is None:
        return None

    raw_upload_path = existing_status.metadata.get("uploaded_file_path")

    if not raw_upload_path:
        raise FileNotFoundError("Original uploaded file path is missing.")

    raw_file = Path(raw_upload_path)

    if not raw_file.exists():
        raise FileNotFoundError(f"Original uploaded file does not exist: {raw_upload_path}")

    source_file_name = existing_status.source_file_name
    file_type = detect_file_type(source_file_name)
    file_hash = calculate_file_hash(str(raw_file))

    parser = parser_registry.get_parser(file_type)

    if parser is None:
        return {
            "status": "failed",
            "message": "Parser for this file type is not implemented yet.",
            "document_id": document_id,
            "file_type": file_type
        }

    update_document_status(
        document_id=document_id,
        status="processing",
        current_stage="reprocessing",
        file_type=file_type,
        message="Re-processing document."
    )

    blocks = parser.parse(
        file_path=str(raw_file),
        document_id=document_id,
        source_file_name=source_file_name
    )

    chunks = chunk_blocks(blocks)

    processed_metadata = save_processed_document(
        document_id=document_id,
        source_file_name=source_file_name,
        file_type=file_type,
        file_hash=file_hash,
        blocks=blocks,
        chunks=chunks
    )

    register_document_hash(
        document_id=document_id,
        source_file_name=source_file_name,
        file_type=file_type,
        file_hash=file_hash
    )

    update_document_status(
        document_id=document_id,
        status="processed",
        current_stage="processed",
        file_type=file_type,
        message="Document re-processed successfully.",
        metadata={
            "last_operation": "reprocess",
            "processed_files": processed_metadata["processed_files"]
        }
    )

    return {
        "status": "success",
        "message": "Document re-processed successfully.",
        "document_id": document_id,
        "file_type": file_type,
        "blocks_created": len(blocks),
        "chunks_created": len(chunks)
    }
