import re
from typing import Optional, List, Dict, Any
from rank_bm25 import BM25Okapi

from app.storage.status_storage import list_document_statuses
from app.storage.processed_storage import read_processed_chunks


def tokenize(text: str) -> List[str]:
    text = text.lower()
    return re.findall(r"[a-zA-Z0-9_]+", text)


def load_candidate_chunks(document_id: Optional[str] = None):
    all_chunks = []

    if document_id:
        chunks = read_processed_chunks(document_id)

        if chunks:
            all_chunks.extend(chunks)

        return all_chunks

    documents = list_document_statuses()

    for document in documents:
        chunks = read_processed_chunks(document.document_id)

        if chunks:
            all_chunks.extend(chunks)

    return all_chunks


def keyword_search_chunks(
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:

    chunks = load_candidate_chunks(document_id=document_id)

    chunks = [
        chunk for chunk in chunks
        if chunk.content and chunk.content.strip()
    ]

    if not chunks:
        return {
            "query": query,
            "document_id_filter": document_id,
            "top_k": top_k,
            "results": []
        }

    tokenized_corpus = [tokenize(chunk.content) for chunk in chunks]
    tokenized_query = tokenize(query)

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    ranked_items = sorted(
        zip(chunks, scores),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for chunk, score in ranked_items[:top_k]:
        results.append(
            {
                "score": float(score),
                "keyword_score": float(score),
                "vector_score": None,
                "hybrid_score": None,
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "content_type": chunk.content_type,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "source_file_name": chunk.source_file_name,
                "metadata": chunk.metadata
            }
        )

    return {
        "query": query,
        "document_id_filter": document_id,
        "top_k": top_k,
        "results": results
    }
