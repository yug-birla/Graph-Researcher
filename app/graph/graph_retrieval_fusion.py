
from typing import List, Dict, Any, Optional

from app.graph.graph_guided_retriever import graph_guided_retrieve


def get_value(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def set_value(obj, key: str, value):
    if isinstance(obj, dict):
        obj[key] = value
        return obj

    try:
        setattr(obj, key, value)
    except Exception:
        pass

    return obj


def normalize_chunk_id(value) -> str:
    if value is None:
        return ""

    return str(value)


def result_chunk_id(result, fallback_index: int) -> str:
    chunk_id = (
        get_value(result, "chunk_id")
        or get_value(result, "id")
        or get_value(result, "chunk", None)
    )

    if chunk_id:
        return normalize_chunk_id(chunk_id)

    content = (
        get_value(result, "content")
        or get_value(result, "text")
        or ""
    )

    return f"fallback_{fallback_index}_{hash(content)}"


def convert_graph_result_to_retrieval_result(
    graph_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Converts a graph-guided chunk into a retrieval-like result.

    We keep it as a dict because the rest of the pipeline already supports
    dict-style results in multiple places.
    """

    graph_score = graph_result.get("graph_score", 0.0)

    return {
        "chunk_id": graph_result.get("chunk_id"),
        "content": graph_result.get("text_preview", ""),
        "text": graph_result.get("text_preview", ""),
        "page_number": graph_result.get("page_number"),
        "source_file_name": graph_result.get("source_file_name"),
        "score": graph_score,
        "retrieval_source": "graph",
        "graph_score": graph_score,
        "matched_entities": graph_result.get("matched_entities", []),
        "matched_relations": graph_result.get("matched_relations", [])
    }


def fuse_retrieval_results_with_graph(
    document_id: Optional[str],
    query: str,
    retrieval_results: List[Any],
    graph_entity_limit: int = 8,
    graph_top_k: int = 5,
    final_top_k: int = 8
) -> Dict[str, Any]:
    """
    Fuses normal retrieval results with graph-guided chunks.

    Strategy:
    - Keep normal retrieval results.
    - Add graph-guided chunks if they are not already present.
    - If same chunk appears in both, mark it as graph-supported and boost score.
    """

    normal_results = retrieval_results or []

    graph_result = graph_guided_retrieve(
        document_id=document_id,
        query=query,
        graph_entity_limit=graph_entity_limit,
        top_k=graph_top_k
    )

    if graph_result.get("status") != "success":
        return {
            "fused_results": normal_results[:final_top_k],
            "fusion_used": False,
            "reason": graph_result.get("message", "Graph retrieval unavailable."),
            "graph_retrieval": graph_result,
            "normal_count": len(normal_results),
            "graph_added_count": 0,
            "final_count": len(normal_results[:final_top_k])
        }

    result_map: Dict[str, Any] = {}

    # Add normal retrieval first
    for index, item in enumerate(normal_results):
        chunk_id = result_chunk_id(item, index)

        set_value(item, "retrieval_source", get_value(item, "retrieval_source", "vector_or_hybrid"))
        set_value(item, "graph_supported", False)

        result_map[chunk_id] = item

    graph_added_count = 0
    graph_supported_count = 0

    for graph_chunk in graph_result.get("results", []):
        chunk_id = normalize_chunk_id(graph_chunk.get("chunk_id"))

        if not chunk_id:
            continue

        if chunk_id in result_map:
            existing = result_map[chunk_id]

            set_value(existing, "graph_supported", True)
            set_value(existing, "retrieval_source", "retrieval_and_graph")
            set_value(existing, "graph_score", graph_chunk.get("graph_score"))
            set_value(existing, "matched_entities", graph_chunk.get("matched_entities", []))
            set_value(existing, "matched_relations", graph_chunk.get("matched_relations", []))

            old_score = get_value(existing, "score", 0) or 0

            try:
                boosted_score = float(old_score) + float(graph_chunk.get("graph_score", 0)) * 0.05
                set_value(existing, "score", boosted_score)
            except Exception:
                pass

            graph_supported_count += 1

        else:
            result_map[chunk_id] = convert_graph_result_to_retrieval_result(graph_chunk)
            graph_added_count += 1

    fused_results = list(result_map.values())

    def sort_score(item):
        score = get_value(item, "score", 0) or 0

        try:
            return float(score)
        except Exception:
            return 0.0

    fused_results = sorted(
        fused_results,
        key=sort_score,
        reverse=True
    )[:final_top_k]

    return {
        "fused_results": fused_results,
        "fusion_used": True,
        "reason": "Normal retrieval results fused with graph-guided chunks.",
        "graph_retrieval": graph_result,
        "normal_count": len(normal_results),
        "graph_added_count": graph_added_count,
        "graph_supported_count": graph_supported_count,
        "final_count": len(fused_results)
    }
