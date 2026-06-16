
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.evaluation.graph_fusion_evaluator import compare_graph_fusion_retrieval


DEFAULT_GRAPHRAG_TEST_QUERIES = [
    "What is RAG?",
    "Why does RAG exist?",
    "What are the main components of a RAG system?",
    "What is vectorless RAG?",
    "Why can vector search fail?",
    "How does BM25 help in retrieval?",
    "How does RAG reduce hallucination?",
    "What is the role of citations in RAG?"
]


def parse_custom_queries(custom_queries: Optional[str]) -> List[str]:
    if not custom_queries:
        return []

    # User can pass queries separated by ||
    # Example: What is RAG?||Why does RAG exist?
    queries = [
        item.strip()
        for item in custom_queries.split("||")
        if item.strip()
    ]

    return queries


def safe_number(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def summarize_batch_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)

    if total == 0:
        return {
            "total_questions": 0,
            "fusion_improved_count": 0,
            "fusion_same_count": 0,
            "fusion_worse_count": 0,
            "average_normal_quality": 0.0,
            "average_graph_quality": 0.0,
            "average_fused_quality": 0.0,
            "average_fusion_delta": 0.0,
            "total_graph_added_chunks": 0,
            "total_graph_supported_chunks": 0,
            "final_verdict": "no_questions_evaluated"
        }

    normal_scores = []
    graph_scores = []
    fused_scores = []
    deltas = []

    fusion_improved_count = 0
    fusion_same_count = 0
    fusion_worse_count = 0

    total_graph_added_chunks = 0
    total_graph_supported_chunks = 0

    for result in results:
        comparison = result.get("comparison", {})
        fusion_stats = result.get("fusion_stats", {})

        normal_score = safe_number(comparison.get("normal_average_quality"))
        graph_score = safe_number(comparison.get("graph_average_quality"))
        fused_score = safe_number(comparison.get("fused_average_quality"))
        delta = safe_number(comparison.get("fusion_quality_delta"))

        normal_scores.append(normal_score)
        graph_scores.append(graph_score)
        fused_scores.append(fused_score)
        deltas.append(delta)

        if delta > 0:
            fusion_improved_count += 1
        elif delta == 0:
            fusion_same_count += 1
        else:
            fusion_worse_count += 1

        total_graph_added_chunks += int(fusion_stats.get("graph_added_count") or 0)
        total_graph_supported_chunks += int(fusion_stats.get("graph_supported_count") or 0)

    average_normal = round(sum(normal_scores) / total, 4)
    average_graph = round(sum(graph_scores) / total, 4)
    average_fused = round(sum(fused_scores) / total, 4)
    average_delta = round(sum(deltas) / total, 4)

    if fusion_improved_count > fusion_worse_count and average_delta > 0:
        final_verdict = "graph_fusion_helped_overall"
    elif fusion_worse_count > fusion_improved_count and average_delta < 0:
        final_verdict = "graph_fusion_added_noise_overall"
    else:
        final_verdict = "graph_fusion_mixed_or_neutral"

    return {
        "total_questions": total,
        "fusion_improved_count": fusion_improved_count,
        "fusion_same_count": fusion_same_count,
        "fusion_worse_count": fusion_worse_count,
        "average_normal_quality": average_normal,
        "average_graph_quality": average_graph,
        "average_fused_quality": average_fused,
        "average_fusion_delta": average_delta,
        "total_graph_added_chunks": total_graph_added_chunks,
        "total_graph_supported_chunks": total_graph_supported_chunks,
        "final_verdict": final_verdict
    }


def build_compact_question_result(
    query: str,
    full_result: Dict[str, Any]
) -> Dict[str, Any]:
    comparison = full_result.get("comparison", {})
    fusion_stats = full_result.get("fusion_stats", {})

    normal_results = (
        full_result
        .get("normal_retrieval", {})
        .get("results", [])
    )

    fused_results = (
        full_result
        .get("fused_retrieval", {})
        .get("results", [])
    )

    return {
        "query": query,
        "comparison": comparison,
        "fusion_stats": fusion_stats,
        "top_normal_chunks": [
            {
                "rank": item.get("rank"),
                "chunk_id": item.get("chunk_id"),
                "page_number": item.get("page_number"),
                "quality_score": item.get("quality_score"),
                "penalties": item.get("penalties"),
                "preview": item.get("content_preview")
            }
            for item in normal_results[:3]
        ],
        "top_fused_chunks": [
            {
                "rank": item.get("rank"),
                "chunk_id": item.get("chunk_id"),
                "page_number": item.get("page_number"),
                "retrieval_source": item.get("retrieval_source"),
                "graph_supported": item.get("graph_supported"),
                "quality_score": item.get("quality_score"),
                "penalties": item.get("penalties"),
                "preview": item.get("content_preview")
            }
            for item in fused_results[:3]
        ]
    }


def run_graphrag_batch_evaluation(
    document_id: str,
    custom_queries: Optional[str] = None,
    top_k: int = 5,
    retrieval_mode: str = "hybrid",
    use_reranker: bool = True,
    graph_entity_limit: int = 8,
    graph_retrieval_top_k: int = 5,
    compact: bool = True
) -> Dict[str, Any]:

    queries = parse_custom_queries(custom_queries)

    if not queries:
        queries = DEFAULT_GRAPHRAG_TEST_QUERIES

    detailed_results = []
    compact_results = []
    failed_questions = []

    for query in queries:
        try:
            result = compare_graph_fusion_retrieval(
                document_id=document_id,
                query=query,
                top_k=top_k,
                retrieval_mode=retrieval_mode,
                use_reranker=use_reranker,
                graph_entity_limit=graph_entity_limit,
                graph_retrieval_top_k=graph_retrieval_top_k
            )

            detailed_results.append(result)
            compact_results.append(
                build_compact_question_result(
                    query=query,
                    full_result=result
                )
            )

        except Exception as error:
            failed_questions.append(
                {
                    "query": query,
                    "error": str(error)
                }
            )

    summary = summarize_batch_results(detailed_results)

    response = {
        "status": "success",
        "document_id": document_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_type": "graphrag_batch_fusion_evaluation",
        "settings": {
            "top_k": top_k,
            "retrieval_mode": retrieval_mode,
            "use_reranker": use_reranker,
            "graph_entity_limit": graph_entity_limit,
            "graph_retrieval_top_k": graph_retrieval_top_k,
            "custom_queries_used": bool(custom_queries)
        },
        "summary": summary,
        "failed_questions": failed_questions,
        "questions": compact_results if compact else detailed_results,
        "notes": [
            "This is a heuristic debug report, not a final academic benchmark.",
            "The report helps inspect whether graph fusion improves retrieval quality across multiple questions.",
            "For formal metrics, create a labeled benchmark with ground-truth relevant chunks."
        ]
    }

    return response
