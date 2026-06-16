import uuid
import hashlib
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings
from app.ingestion.file_detector import detect_file_type
from app.ingestion.parser_registry import parser_registry
from app.chunking.chunking_service import chunk_blocks
from app.storage.processed_storage import save_processed_document
from app.storage.status_storage import (
    create_document_status,
    update_document_status
)
from app.storage.document_index import (
    find_duplicate_by_hash,
    register_document_hash
)


async def save_uploaded_file(file: UploadFile, document_id: str) -> tuple[str, str, int]:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(file.filename).name
    saved_filename = f"{document_id}_{safe_filename}"
    file_path = settings.UPLOAD_DIR / saved_filename

    content = await file.read()

    upload_size_bytes = len(content)
    max_upload_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if upload_size_bytes > max_upload_size_bytes:
        raise ValueError(
            f"File is too large. Maximum allowed size is "
            f"{settings.MAX_UPLOAD_SIZE_MB} MB, but uploaded file is "
            f"{round(upload_size_bytes / (1024 * 1024), 2)} MB."
        )

    file_hash = hashlib.sha256(content).hexdigest()

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path), file_hash, upload_size_bytes


async def process_uploaded_file(file: UploadFile):
    document_id = str(uuid.uuid4())

    try:
        file_path, file_hash, upload_size_bytes = await save_uploaded_file(
            file=file,
            document_id=document_id
        )

        duplicate_document = find_duplicate_by_hash(file_hash)

        if duplicate_document is not None:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception:
                pass

            return {
                "status": "duplicate",
                "message": "This exact file was already uploaded and processed.",
                "uploaded_file_name": file.filename,
                "existing_document": duplicate_document,
                "duplicate_detection": {
                    "method": "sha256_file_hash",
                    "file_hash": file_hash
                }
            }

        create_document_status(
            document_id=document_id,
            source_file_name=file.filename
        )

        file_type = detect_file_type(file.filename)

        update_document_status(
            document_id=document_id,
            status="processing",
            current_stage="file_type_detected",
            file_type=file_type,
            message=f"Detected file type: {file_type}",
            metadata={
                "uploaded_file_path": file_path,
                "file_hash": file_hash,
                "upload_size_bytes": upload_size_bytes,
                "upload_size_mb": round(upload_size_bytes / (1024 * 1024), 2),
                "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB
            }
        )

        parser = parser_registry.get_parser(file_type)

        if parser is None:
            update_document_status(
                document_id=document_id,
                status="failed",
                current_stage="parser_not_available",
                file_type=file_type,
                message="Parser for this file type is not implemented yet.",
                error_message="No parser registered for this file type."
            )

            return {
                "status": "failed",
                "document_id": document_id,
                "file_name": file.filename,
                "file_type": file_type,
                "message": "Parser for this file type is not implemented yet."
            }

        update_document_status(
            document_id=document_id,
            status="processing",
            current_stage="parsing",
            file_type=file_type,
            message="Parsing document into RichContentBlocks."
        )

        blocks = parser.parse(
            file_path=file_path,
            document_id=document_id,
            source_file_name=file.filename
        )

        update_document_status(
            document_id=document_id,
            status="processing",
            current_stage="chunking",
            file_type=file_type,
            message="Chunking RichContentBlocks.",
            metadata={
                "blocks_created": len(blocks)
            }
        )

        chunks = chunk_blocks(blocks)

        update_document_status(
            document_id=document_id,
            status="processing",
            current_stage="saving",
            file_type=file_type,
            message="Saving processed document.",
            metadata={
                "chunks_created": len(chunks)
            }
        )

        processed_metadata = save_processed_document(
            document_id=document_id,
            source_file_name=file.filename,
            file_type=file_type,
            file_hash=file_hash,
            blocks=blocks,
            chunks=chunks
        )

        register_document_hash(
            document_id=document_id,
            source_file_name=file.filename,
            file_type=file_type,
            file_hash=file_hash
        )

        update_document_status(
            document_id=document_id,
            status="processed",
            current_stage="processed",
            file_type=file_type,
            message="Document processed successfully.",
            metadata={
                "file_hash": file_hash,
                "processed_files": processed_metadata["processed_files"],
                "content_types_in_blocks": processed_metadata["content_types_in_blocks"],
                "content_types_in_chunks": processed_metadata["content_types_in_chunks"]
            }
        )

        return {
            "status": "success",
            "document_id": document_id,
            "file_name": file.filename,
            "file_type": file_type,
            "file_hash": file_hash,
            "upload_size_bytes": upload_size_bytes,
            "upload_size_mb": round(upload_size_bytes / (1024 * 1024), 2),
            "blocks_created": len(blocks),
            "chunks_created": len(chunks),
            "content_types_in_blocks": processed_metadata["content_types_in_blocks"],
            "content_types_in_chunks": processed_metadata["content_types_in_chunks"],
            "processed_files": processed_metadata["processed_files"],
            "status_file": f"data/processed/{document_id}/status.json",
            "preview": create_chunks_preview(chunks)
        }

    except ValueError as error:
        return {
            "status": "failed",
            "document_id": document_id,
            "file_name": file.filename,
            "message": "Upload rejected.",
            "error": str(error),
            "limit": {
                "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB
            }
        }

    except Exception as error:
        update_document_status(
            document_id=document_id,
            status="failed",
            current_stage="failed",
            message="Document processing failed.",
            error_message=str(error)
        )

        return {
            "status": "failed",
            "document_id": document_id,
            "file_name": file.filename,
            "message": "Document processing failed.",
            "error": str(error),
            "status_file": f"data/processed/{document_id}/status.json"
        }


def create_chunks_preview(chunks, max_chars: int = 400):
    preview = []

    for chunk in chunks[:3]:
        preview.append({
            "chunk_id": chunk.chunk_id,
            "parent_block_id": chunk.parent_block_id,
            "content_type": chunk.content_type,
            "page_number": chunk.page_number,
            "source_file_name": chunk.source_file_name,
            "content_preview": chunk.content[:max_chars]
        })

    return preview
