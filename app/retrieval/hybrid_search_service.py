from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.retrieval.search_service import search_relevant_chunks
from app.retrieval.keyword_search_service import keyword_search_chunks


def min_max_normalize(score_map: Dict[str, float]) -> Dict[str, float]:
    if not score_map:
        return {}

    values = list(score_map.values())
    min_value = min(values)
    max_value = max(values)

    if max_value == min_value:
        return {key: 1.0 for key in score_map}

    return {
        key: (value - min_value) / (max_value - min_value)
        for key, value in score_map.items()
    }


def hybrid_search_chunks(
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    candidate_k: Optional[int] = None
) -> Dict[str, Any]:

    if candidate_k is None:
        candidate_k = max(top_k * 4, 20)

    vector_output = search_relevant_chunks(
        query=query,
        document_id=document_id,
        top_k=candidate_k
    )

    keyword_output = keyword_search_chunks(
        query=query,
        document_id=document_id,
        top_k=candidate_k
    )

    combined = {}

    vector_scores = {}
    keyword_scores = {}

    for result in vector_output["results"]:
        chunk_id = result["chunk_id"]
        combined[chunk_id] = result
        vector_scores[chunk_id] = float(result.get("vector_score") or result.get("score") or 0.0)

    for result in keyword_output["results"]:
        chunk_id = result["chunk_id"]

        if chunk_id not in combined:
            combined[chunk_id] = result

        keyword_scores[chunk_id] = float(result.get("keyword_score") or result.get("score") or 0.0)

    normalized_vector_scores = min_max_normalize(vector_scores)
    normalized_keyword_scores = min_max_normalize(keyword_scores)

    ranked_results = []

    for chunk_id, result in combined.items():
        vector_score = normalized_vector_scores.get(chunk_id, 0.0)
        keyword_score = normalized_keyword_scores.get(chunk_id, 0.0)

        hybrid_score = (
            settings.HYBRID_VECTOR_WEIGHT * vector_score
            + settings.HYBRID_KEYWORD_WEIGHT * keyword_score
        )

        result = dict(result)
        result["vector_score"] = vector_scores.get(chunk_id)
        result["keyword_score"] = keyword_scores.get(chunk_id)
        result["hybrid_score"] = hybrid_score
        result["score"] = hybrid_score

        ranked_results.append(result)

    ranked_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    return {
        "query": query,
        "document_id_filter": document_id,
        "top_k": top_k,
        "candidate_k": candidate_k,
        "retrieval_mode": "hybrid",
        "weights": {
            "vector": settings.HYBRID_VECTOR_WEIGHT,
            "keyword": settings.HYBRID_KEYWORD_WEIGHT
        },
        "results": ranked_results[:top_k]
    }


def retrieve_chunks(
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    retrieval_mode: str = "hybrid"
) -> Dict[str, Any]:

    if retrieval_mode == "vector":
        output = search_relevant_chunks(
            query=query,
            document_id=document_id,
            top_k=top_k
        )
        output["retrieval_mode"] = "vector"
        return output

    if retrieval_mode == "keyword":
        output = keyword_search_chunks(
            query=query,
            document_id=document_id,
            top_k=top_k
        )
        output["retrieval_mode"] = "keyword"
        return output

    return hybrid_search_chunks(
        query=query,
        document_id=document_id,
        top_k=top_k
    )
