
from typing import Dict, Any, List, Optional
import re

from app.graph.graph_context_service import build_graph_context_for_query
from app.storage.processed_storage import read_processed_chunks
from app.graph.graph_quality import (
    is_low_quality_chunk_text,
    is_meta_showcase_chunk_text,
    is_cover_or_marketing_chunk_text
)


def get_value(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def normalize_chunk_id(value) -> str:
    if value is None:
        return ""

    return str(value)


def build_chunk_lookup(chunks: List[Any]) -> Dict[str, Any]:
    lookup = {}

    for index, chunk in enumerate(chunks):
        chunk_id = (
            get_value(chunk, "chunk_id")
            or get_value(chunk, "id")
            or f"chunk_{index}"
        )

        lookup[normalize_chunk_id(chunk_id)] = chunk

    return lookup


def extract_text_preview(chunk, max_chars: int = 700) -> str:
    text = (
        get_value(chunk, "content")
        or get_value(chunk, "text")
        or ""
    )

    text = str(text).replace("\\n", " ").strip()

    if len(text) > max_chars:
        return text[:max_chars] + "..."

    return text


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", str(text or "").lower())


def query_text_relevance(query: str, text: str) -> float:
    """
    Adds text-level relevance so graph retrieval does not rank a chunk
    only because it has connected entities.
    """

    query_terms = [
        term for term in tokenize(query)
        if term not in {"what", "is", "are", "the", "a", "an", "of", "to", "and", "why", "how"}
    ]

    text_lower = str(text or "").lower()
    text_tokens = set(tokenize(text))

    score = 0.0

    for term in query_terms:
        if term in text_tokens:
            score += 4.0
        elif len(term) >= 4 and term in text_lower:
            score += 1.5

    # Definition questions should prefer chunks with definition-like language.
    if "what" in query.lower() and "rag" in query.lower():
        definition_markers = [
            "rag is",
            "rag stands for",
            "retrieval-augmented generation",
            "retrieval augmented generation",
            "adds a retrieval step",
            "before generation",
            "document corpus"
        ]

        for marker in definition_markers:
            if marker in text_lower:
                score += 5.0

    return score


def score_graph_chunks(
    graph_context: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:

    chunk_scores: Dict[str, Dict[str, Any]] = {}

    matched_entities = graph_context.get("matched_entities", [])
    matched_relations = graph_context.get("matched_relations", [])

    for entity in matched_entities:
        mention_count = entity.get("mention_count", 1) or 1
        base_score = 3.0 + min(mention_count, 10) * 0.2

        for chunk_id in entity.get("chunk_ids", []):
            cid = normalize_chunk_id(chunk_id)

            if not cid:
                continue

            if cid not in chunk_scores:
                chunk_scores[cid] = {
                    "score": 0.0,
                    "matched_entities": [],
                    "matched_relations": []
                }

            chunk_scores[cid]["score"] += base_score
            chunk_scores[cid]["matched_entities"].append(entity.get("name"))

    for relation in matched_relations:
        weight = relation.get("weight", 1) or 1
        base_score = 2.0 + min(weight, 10) * 0.3

        relation_label = (
            f'{relation.get("source")} '
            f'--{relation.get("relation_type")}--> '
            f'{relation.get("target")}'
        )

        for chunk_id in relation.get("chunk_ids", []):
            cid = normalize_chunk_id(chunk_id)

            if not cid:
                continue

            if cid not in chunk_scores:
                chunk_scores[cid] = {
                    "score": 0.0,
                    "matched_entities": [],
                    "matched_relations": []
                }

            chunk_scores[cid]["score"] += base_score
            chunk_scores[cid]["matched_relations"].append(relation_label)

    return chunk_scores


def graph_guided_retrieve(
    document_id: Optional[str],
    query: str,
    graph_entity_limit: int = 8,
    top_k: int = 5
) -> Dict[str, Any]:

    if not document_id:
        return {
            "status": "failed",
            "message": "document_id is required.",
            "results": []
        }

    chunks = read_processed_chunks(document_id)

    if chunks is None:
        return {
            "status": "failed",
            "message": "No processed chunks found. Upload/process the document first.",
            "document_id": document_id,
            "results": []
        }

    graph_context = build_graph_context_for_query(
        document_id=document_id,
        query=query,
        limit=graph_entity_limit
    )

    if not graph_context.get("graph_available"):
        return {
            "status": "failed",
            "message": graph_context.get("reason", "Graph context not available."),
            "document_id": document_id,
            "graph_context": graph_context,
            "results": []
        }

    chunk_lookup = build_chunk_lookup(chunks)
    chunk_scores = score_graph_chunks(graph_context)

    candidate_results = []

    for chunk_id, info in chunk_scores.items():
        chunk = chunk_lookup.get(chunk_id)

        if chunk is None:
            continue

        text_preview = extract_text_preview(chunk)

        if is_low_quality_chunk_text(text_preview):
            continue

        if is_meta_showcase_chunk_text(text_preview):
            continue

        if is_cover_or_marketing_chunk_text(text_preview):
            continue

        final_score = info["score"] + query_text_relevance(query, text_preview)

        candidate_results.append(
            {
                "chunk_id": chunk_id,
                "graph_score": round(final_score, 4),
                "page_number": get_value(chunk, "page_number"),
                "source_file_name": (
                    get_value(chunk, "source_file_name")
                    or get_value(chunk, "file_name")
                    or get_value(chunk, "filename")
                ),
                "matched_entities": sorted(set(info["matched_entities"])),
                "matched_relations": sorted(set(info["matched_relations"])),
                "text_preview": text_preview
            }
        )

    candidate_results = sorted(
        candidate_results,
        key=lambda item: item["graph_score"],
        reverse=True
    )

    results = []

    for rank, item in enumerate(candidate_results[:top_k], start=1):
        item["rank"] = rank
        results.append(item)

    return {
        "status": "success",
        "document_id": document_id,
        "query": query,
        "graph_available": True,
        "graph_entity_limit": graph_entity_limit,
        "top_k": top_k,
        "matched_entity_count": len(graph_context.get("matched_entities", [])),
        "matched_relation_count": len(graph_context.get("matched_relations", [])),
        "returned_chunks": len(results),
        "matched_entities": graph_context.get("matched_entities", []),
        "matched_relations": graph_context.get("matched_relations", []),
        "results": results
    }
