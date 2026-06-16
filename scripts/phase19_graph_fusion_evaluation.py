from pathlib import Path

# Remove BOM from Python files
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")


# =====================================================
# 1. Create GraphRAG fusion evaluator
# =====================================================

Path("app/evaluation/graph_fusion_evaluator.py").write_text(r'''
import re
from typing import Dict, Any, List, Optional

from app.retrieval.hybrid_search_service import retrieve_chunks
from app.retrieval.reranking_service import rerank_results
from app.retrieval.citation_service import attach_source_ids
from app.generation.context_cleaner import clean_retrieved_results
from app.graph.graph_guided_retriever import graph_guided_retrieve
from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph

try:
    from app.graph.graph_quality import (
        is_low_quality_chunk_text,
        is_meta_showcase_chunk_text,
        is_cover_or_marketing_chunk_text
    )
except Exception:
    def is_low_quality_chunk_text(text: str) -> bool:
        return False

    def is_meta_showcase_chunk_text(text: str) -> bool:
        return False

    def is_cover_or_marketing_chunk_text(text: str) -> bool:
        return False


def get_value(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", str(text or "").lower())


def get_content(result: Any) -> str:
    return (
        get_value(result, "content")
        or get_value(result, "text")
        or get_value(result, "raw_content")
        or ""
    )


def get_chunk_id(result: Any) -> str:
    return str(
        get_value(result, "chunk_id")
        or get_value(result, "id")
        or ""
    )


def preview(text: str, max_chars: int = 350) -> str:
    text = str(text or "").replace("\n", " ").strip()

    if len(text) > max_chars:
        return text[:max_chars] + "..."

    return text


def query_terms(query: str) -> List[str]:
    stopwords = {
        "what", "is", "are", "the", "a", "an", "of", "to", "and",
        "or", "why", "how", "does", "do", "explain", "define"
    }

    return [
        term for term in tokenize(query)
        if term not in stopwords and len(term) > 1
    ]


def quality_score_for_result(query: str, result: Any) -> Dict[str, Any]:
    content = get_content(result)
    lower = content.lower()
    tokens = set(tokenize(content))
    terms = query_terms(query)

    score = 0.0
    reasons = []

    for term in terms:
        if term in tokens:
            score += 2.0
            reasons.append(f"contains query term: {term}")
        elif len(term) >= 4 and term in lower:
            score += 1.0
            reasons.append(f"contains query substring: {term}")

    if "rag" in terms:
        definition_markers = [
            "rag is",
            "rag stands for",
            "retrieval-augmented generation",
            "retrieval augmented generation",
            "adds a retrieval step",
            "before generation",
            "document corpus",
            "reduces hallucination"
        ]

        for marker in definition_markers:
            if marker in lower:
                score += 3.0
                reasons.append(f"definition marker: {marker}")

    if get_value(result, "graph_supported", False):
        score += 1.5
        reasons.append("supported by graph and retrieval")

    retrieval_source = get_value(result, "retrieval_source")

    if retrieval_source == "graph":
        score += 0.5
        reasons.append("selected by graph retrieval")

    penalties = []

    if is_low_quality_chunk_text(content):
        score -= 5.0
        penalties.append("low quality / TOC-like chunk")

    if is_meta_showcase_chunk_text(content):
        score -= 5.0
        penalties.append("meta / LinkedIn / resume-style chunk")

    if is_cover_or_marketing_chunk_text(content):
        score -= 5.0
        penalties.append("cover / marketing chunk")

    score = round(score, 4)

    return {
        "quality_score": score,
        "positive_reasons": reasons,
        "penalties": penalties
    }


def summarize_results(query: str, results: List[Any], label: str) -> Dict[str, Any]:
    rows = []

    for rank, result in enumerate(results, start=1):
        quality = quality_score_for_result(query, result)

        rows.append(
            {
                "rank": rank,
                "chunk_id": get_chunk_id(result),
                "page_number": get_value(result, "page_number"),
                "source_file_name": get_value(result, "source_file_name"),
                "retrieval_source": get_value(result, "retrieval_source"),
                "graph_supported": get_value(result, "graph_supported", False),
                "score": get_value(result, "score"),
                "graph_score": get_value(result, "graph_score"),
                "quality_score": quality["quality_score"],
                "positive_reasons": quality["positive_reasons"],
                "penalties": quality["penalties"],
                "content_preview": preview(get_content(result))
            }
        )

    avg_quality = 0.0

    if rows:
        avg_quality = round(
            sum(row["quality_score"] for row in rows) / len(rows),
            4
        )

    noisy_count = sum(1 for row in rows if row["penalties"])

    return {
        "label": label,
        "count": len(rows),
        "average_quality_score": avg_quality,
        "noisy_chunk_count": noisy_count,
        "results": rows
    }


def compare_graph_fusion_retrieval(
    document_id: str,
    query: str,
    top_k: int = 5,
    retrieval_mode: str = "hybrid",
    use_reranker: bool = True,
    graph_entity_limit: int = 8,
    graph_retrieval_top_k: int = 5
) -> Dict[str, Any]:

    retrieval_output = retrieve_chunks(
        query=query,
        document_id=document_id,
        top_k=top_k,
        retrieval_mode=retrieval_mode
    )

    normal_results = retrieval_output.get("results", [])

    if use_reranker:
        normal_results = rerank_results(
            query=query,
            results=normal_results,
            top_k=top_k
        )
    else:
        normal_results = normal_results[:top_k]

    cleaned_normal_results = clean_retrieved_results(normal_results)
    sourced_normal_results = attach_source_ids(cleaned_normal_results)

    graph_result = graph_guided_retrieve(
        document_id=document_id,
        query=query,
        graph_entity_limit=graph_entity_limit,
        top_k=graph_retrieval_top_k
    )

    fusion_result = fuse_retrieval_results_with_graph(
        document_id=document_id,
        query=query,
        retrieval_results=sourced_normal_results,
        graph_entity_limit=graph_entity_limit,
        graph_top_k=graph_retrieval_top_k,
        final_top_k=max(top_k, graph_retrieval_top_k)
    )

    fused_results = fusion_result.get("fused_results", [])

    normal_summary = summarize_results(
        query=query,
        results=sourced_normal_results,
        label="normal_retrieval"
    )

    graph_summary = summarize_results(
        query=query,
        results=graph_result.get("results", []),
        label="graph_guided_retrieval"
    )

    fused_summary = summarize_results(
        query=query,
        results=fused_results,
        label="fused_retrieval"
    )

    improvement = round(
        fused_summary["average_quality_score"]
        - normal_summary["average_quality_score"],
        4
    )

    if improvement > 0:
        verdict = "fusion_improved_retrieval_quality"
    elif improvement == 0:
        verdict = "fusion_quality_same_as_normal_retrieval"
    else:
        verdict = "fusion_may_be_adding_noise"

    return {
        "status": "success",
        "document_id": document_id,
        "query": query,
        "retrieval_mode": retrieval_mode,
        "use_reranker": use_reranker,
        "comparison": {
            "normal_average_quality": normal_summary["average_quality_score"],
            "graph_average_quality": graph_summary["average_quality_score"],
            "fused_average_quality": fused_summary["average_quality_score"],
            "fusion_quality_delta": improvement,
            "verdict": verdict
        },
        "fusion_stats": {
            "fusion_used": fusion_result.get("fusion_used", False),
            "normal_count": fusion_result.get("normal_count"),
            "graph_added_count": fusion_result.get("graph_added_count"),
            "graph_supported_count": fusion_result.get("graph_supported_count"),
            "final_count": fusion_result.get("final_count"),
            "reason": fusion_result.get("reason")
        },
        "normal_retrieval": normal_summary,
        "graph_guided_retrieval": graph_summary,
        "fused_retrieval": fused_summary,
        "notes": [
            "This is a heuristic debug evaluator, not a benchmark metric.",
            "Use it to inspect whether graph retrieval is adding useful evidence or noisy chunks.",
            "For formal evaluation, use labeled questions and relevance judgments."
        ]
    }
''', encoding="utf-8")


# =====================================================
# 2. Patch main.py
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.evaluation.graph_fusion_evaluator import compare_graph_fusion_retrieval" not in text:
    text = "from app.evaluation.graph_fusion_evaluator import compare_graph_fusion_retrieval\n" + text

old_phases = [
    "Phase 18 - Graph Quality Cleanup",
    "Phase 17 - Graph Vector Retrieval Fusion",
    "Phase 16 - Graph-Guided Retrieval Debug Layer"
]

for old in old_phases:
    text = text.replace(old, "Phase 19 - GraphRAG Retrieval Fusion Evaluation")

if "# GraphRAG fusion evaluation endpoint" not in text:
    text += '''

# GraphRAG fusion evaluation endpoint

@app.get("/documents/{document_id}/evaluation/graph-fusion")
def evaluate_graph_fusion_for_document(
    document_id: str,
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    retrieval_mode: str = Query("hybrid"),
    use_reranker: bool = True,
    graph_entity_limit: int = Query(8, ge=1, le=30),
    graph_retrieval_top_k: int = Query(5, ge=1, le=20)
):
    return compare_graph_fusion_retrieval(
        document_id=document_id,
        query=query,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        use_reranker=use_reranker,
        graph_entity_limit=graph_entity_limit,
        graph_retrieval_top_k=graph_retrieval_top_k
    )
'''

main_path.write_text(text, encoding="utf-8")

print("Phase 19 GraphRAG retrieval fusion evaluation added.")
