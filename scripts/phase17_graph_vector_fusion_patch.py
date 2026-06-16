from pathlib import Path

# =====================================================
# 1. Remove BOM from Python files
# =====================================================

for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")


# =====================================================
# 2. Create graph-vector fusion service
# =====================================================

Path("app/graph/graph_retrieval_fusion.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# 3. Patch query_schema.py
# =====================================================

query_path = Path("app/schemas/query_schema.py")
text = query_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "use_graph_retrieval" not in text:
    text = text.replace(
'''    use_graph: bool = True
    graph_entity_limit: int = Field(default=8, ge=1, le=30)
''',
'''    use_graph: bool = True
    graph_entity_limit: int = Field(default=8, ge=1, le=30)

    # Phase 17:
    # Adds graph-selected chunks into the retrieval evidence list.
    use_graph_retrieval: bool = True
    graph_retrieval_top_k: int = Field(default=5, ge=1, le=20)
'''
    )

query_path.write_text(text, encoding="utf-8")


# =====================================================
# 4. Patch answer_service.py
# =====================================================

answer_path = Path("app/generation/answer_service.py")
text = answer_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph" not in text:
    text = "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph\n" + text

text = text.replace(
'''    use_graph: bool = True,
    graph_entity_limit: int = 8
) -> Dict[str, Any]:
''',
'''    use_graph: bool = True,
    graph_entity_limit: int = 8,
    use_graph_retrieval: bool = True,
    graph_retrieval_top_k: int = 5
) -> Dict[str, Any]:
'''
)

# Try common variable names used after retrieval.
# We only patch once.
if "fusion_result = fuse_retrieval_results_with_graph" not in text:
    candidates = [
        '''    sourced_results = add_citations_to_results(retrieved_results)
''',
        '''    sourced_results = add_source_ids(retrieved_results)
''',
        '''    sourced_results = retrieved_results
'''
    ]

    inserted = False

    for candidate in candidates:
        if candidate in text:
            replacement = candidate + '''
    fusion_result = fuse_retrieval_results_with_graph(
        document_id=document_id,
        query=query,
        retrieval_results=sourced_results,
        graph_entity_limit=graph_entity_limit,
        graph_top_k=graph_retrieval_top_k,
        final_top_k=max(top_k, graph_retrieval_top_k)
    ) if use_graph_retrieval else {
        "fused_results": sourced_results,
        "fusion_used": False,
        "reason": "Graph retrieval fusion disabled.",
        "graph_retrieval": {},
        "normal_count": len(sourced_results),
        "graph_added_count": 0,
        "graph_supported_count": 0,
        "final_count": len(sourced_results)
    }

    sourced_results = fusion_result.get("fused_results", sourced_results)
'''
            text = text.replace(candidate, replacement)
            inserted = True
            break

    if not inserted:
        print("WARNING: Could not auto-locate sourced_results assignment in answer_service.py")
        print("You may need to paste fusion call manually after sourced_results is created.")

# Add fusion info to final return
if '"retrieval_fusion": fusion_result' not in text:
    text = text.replace(
'''        "graph_used": bool(graph_context.get("matched_entities") or graph_context.get("matched_relations")),
        "graph_context": graph_context,
''',
'''        "graph_used": bool(graph_context.get("matched_entities") or graph_context.get("matched_relations")),
        "graph_context": graph_context,
        "retrieval_fusion": fusion_result if "fusion_result" in locals() else {
            "fusion_used": False,
            "reason": "Fusion result was not created."
        },
'''
    )

answer_path.write_text(text, encoding="utf-8")


# =====================================================
# 5. Patch main.py
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

old_call = '''        use_graph=request.use_graph,
        graph_entity_limit=request.graph_entity_limit
'''

new_call = '''        use_graph=request.use_graph,
        graph_entity_limit=request.graph_entity_limit,
        use_graph_retrieval=request.use_graph_retrieval,
        graph_retrieval_top_k=request.graph_retrieval_top_k
'''

if old_call in text and "use_graph_retrieval=request.use_graph_retrieval" not in text:
    text = text.replace(old_call, new_call)

old_phases = [
    "Phase 16 - Graph-Guided Retrieval Debug Layer",
    "Phase 15 - Graph-Augmented Answering",
    "Phase 14.1 - Graph Visualization UI"
]

for old in old_phases:
    text = text.replace(old, "Phase 17 - Graph Vector Retrieval Fusion")

main_path.write_text(text, encoding="utf-8")

print("Phase 17 graph-vector retrieval fusion patch applied.")
