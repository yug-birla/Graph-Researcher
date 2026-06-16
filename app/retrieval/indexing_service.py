from typing import Dict, Any

from app.storage.processed_storage import read_processed_chunks
from app.storage.status_storage import update_document_status
from app.retrieval.embedding_service import embed_texts
from app.retrieval.vector_store import upsert_chunk_vectors


def index_document_chunks(document_id: str) -> Dict[str, Any]:
    chunks = read_processed_chunks(document_id)

    if chunks is None:
        return {
            "status": "failed",
            "message": "Chunks not found. Process the document before indexing.",
            "document_id": document_id
        }

    indexable_chunks = [
        chunk for chunk in chunks
        if chunk.content and chunk.content.strip()
    ]

    if not indexable_chunks:
        return {
            "status": "failed",
            "message": "No indexable chunks found.",
            "document_id": document_id
        }

    update_document_status(
        document_id=document_id,
        status="processing",
        current_stage="embedding",
        message="Creating embeddings for document chunks.",
        metadata={
            "chunks_to_index": len(indexable_chunks)
        }
    )

    texts = [
        build_embedding_text(chunk)
        for chunk in indexable_chunks
    ]

    vectors = embed_texts(texts)

    points = []

    for chunk, vector in zip(indexable_chunks, vectors):
        payload = {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "parent_block_id": chunk.parent_block_id,
            "content_type": chunk.content_type,
            "content": chunk.content,
            "page_number": chunk.page_number,
            "section_title": chunk.section_title,
            "source_file_name": chunk.source_file_name,
            "metadata": chunk.metadata
        }

        points.append({
            "chunk_id": chunk.chunk_id,
            "vector": vector,
            "payload": payload
        })

    indexed_count = upsert_chunk_vectors(points)

    update_document_status(
        document_id=document_id,
        status="processed",
        current_stage="indexed",
        message="Document chunks indexed successfully.",
        metadata={
            "indexed": True,
            "indexed_chunks": indexed_count
        }
    )

    return {
        "status": "success",
        "message": "Document indexed successfully.",
        "document_id": document_id,
        "indexed_chunks": indexed_count
    }


def build_embedding_text(chunk) -> str:
    prefix = f"Content type: {chunk.content_type}\n"

    if chunk.section_title:
        prefix += f"Section: {chunk.section_title}\n"

    if chunk.page_number:
        prefix += f"Page: {chunk.page_number}\n"

    return prefix + chunk.content
