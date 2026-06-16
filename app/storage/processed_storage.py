import json
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.schemas.rich_content_block import RichContentBlock
from app.schemas.content_chunk import ContentChunk


def save_processed_document(
    document_id: str,
    source_file_name: str,
    file_type: str,
    file_hash: str,
    blocks: List[RichContentBlock],
    chunks: List[ContentChunk]
) -> Dict[str, Any]:

    document_dir = settings.PROCESSED_DIR / document_id
    document_dir.mkdir(parents=True, exist_ok=True)

    blocks_path = document_dir / "blocks.json"
    chunks_path = document_dir / "chunks.json"
    metadata_path = document_dir / "metadata.json"

    with open(blocks_path, "w", encoding="utf-8") as f:
        json.dump([block.model_dump() for block in blocks], f, indent=2, ensure_ascii=False)

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump([chunk.model_dump() for chunk in chunks], f, indent=2, ensure_ascii=False)

    metadata = {
        "document_id": document_id,
        "source_file_name": source_file_name,
        "file_type": file_type,
        "file_hash": file_hash,
        "total_blocks": len(blocks),
        "total_chunks": len(chunks),
        "content_types_in_blocks": count_content_types(blocks),
        "content_types_in_chunks": count_chunk_content_types(chunks),
        "processed_files": {
            "blocks_path": str(blocks_path),
            "chunks_path": str(chunks_path),
            "metadata_path": str(metadata_path)
        }
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return metadata


def read_processed_chunks(document_id: str) -> Optional[List[ContentChunk]]:
    chunks_path = settings.PROCESSED_DIR / document_id / "chunks.json"

    if not chunks_path.exists():
        return None

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    return [ContentChunk(**chunk) for chunk in chunks_data]


def read_processed_metadata(document_id: str) -> Optional[Dict[str, Any]]:
    metadata_path = settings.PROCESSED_DIR / document_id / "metadata.json"

    if not metadata_path.exists():
        return None

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_content_types(blocks: List[RichContentBlock]) -> Dict[str, int]:
    counts = {}

    for block in blocks:
        counts[block.content_type] = counts.get(block.content_type, 0) + 1

    return counts


def count_chunk_content_types(chunks: List[ContentChunk]) -> Dict[str, int]:
    counts = {}

    for chunk in chunks:
        counts[chunk.content_type] = counts.get(chunk.content_type, 0) + 1

    return counts
