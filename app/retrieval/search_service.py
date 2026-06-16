from typing import Optional, Dict, Any

from app.core.config import settings
from app.retrieval.embedding_service import embed_text
from app.retrieval.vector_store import search_vectors


def search_relevant_chunks(
    query: str,
    document_id: Optional[str] = None,
    top_k: Optional[int] = None
) -> Dict[str, Any]:

    if top_k is None:
        top_k = settings.DEFAULT_TOP_K

    query_vector = embed_text(query)

    hits = search_vectors(
        query_vector=query_vector,
        top_k=top_k,
        document_id=document_id
    )

    results = []

    for hit in hits:
        payload = hit.payload
        score = float(hit.score)

        results.append(
            {
                "score": score,
                "vector_score": score,
                "keyword_score": None,
                "hybrid_score": None,
                "chunk_id": payload.get("chunk_id"),
                "document_id": payload.get("document_id"),
                "content_type": payload.get("content_type"),
                "content": payload.get("content"),
                "page_number": payload.get("page_number"),
                "section_title": payload.get("section_title"),
                "source_file_name": payload.get("source_file_name"),
                "metadata": payload.get("metadata", {})
            }
        )

    return {
        "query": query,
        "document_id_filter": document_id,
        "top_k": top_k,
        "results": results
    }
