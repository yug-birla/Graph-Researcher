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
# 2. Create graph-guided retriever
# =====================================================

Path("app/graph/graph_guided_retriever.py").write_text(r'''
from typing import Dict, Any, List, Optional

from app.graph.graph_context_service import build_graph_context_for_query
from app.storage.processed_storage import read_processed_chunks


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


def extract_text_preview(chunk, max_chars: int = 500) -> str:
    text = (
        get_value(chunk, "content")
        or get_value(chunk, "text")
        or ""
    )

    text = str(text).replace("\\n", " ").strip()

    if len(text) > max_chars:
        return text[:max_chars] + "..."

    return text


def score_graph_chunks(
    graph_context: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Scores chunks using matched graph entities and relations.

    Higher score means the chunk is more graph-relevant to the query.
    """

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
    """
    Returns graph-selected chunks for a query.

    This is a debug/research endpoint.
    It helps us inspect whether the graph is selecting useful evidence.
    """

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

    ranked = sorted(
        chunk_scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

    results = []

    for rank, (chunk_id, info) in enumerate(ranked[:top_k], start=1):
        chunk = chunk_lookup.get(chunk_id)

        if chunk is None:
            continue

        results.append(
            {
                "rank": rank,
                "chunk_id": chunk_id,
                "graph_score": round(info["score"], 4),
                "page_number": get_value(chunk, "page_number"),
                "source_file_name": (
                    get_value(chunk, "source_file_name")
                    or get_value(chunk, "file_name")
                    or get_value(chunk, "filename")
                ),
                "matched_entities": sorted(set(info["matched_entities"])),
                "matched_relations": sorted(set(info["matched_relations"])),
                "text_preview": extract_text_preview(chunk)
            }
        )

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
''', encoding="utf-8")


# =====================================================
# 3. Patch main.py
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.graph.graph_guided_retriever import graph_guided_retrieve" not in text:
    text = "from app.graph.graph_guided_retriever import graph_guided_retrieve\n" + text

old_phases = [
    "Phase 15 - Graph-Augmented Answering",
    "Phase 14.1 - Graph Visualization UI",
    "Phase 14 - Graph Foundation Entity Relation Extraction"
]

for old in old_phases:
    text = text.replace(old, "Phase 16 - Graph-Guided Retrieval Debug Layer")

if "# Graph-guided retrieval endpoint" not in text:
    text += '''

# Graph-guided retrieval endpoint

@app.get("/documents/{document_id}/graph/retrieve")
def graph_guided_retrieval_endpoint(
    document_id: str,
    query: str = Query(..., min_length=1),
    graph_entity_limit: int = Query(8, ge=1, le=30),
    top_k: int = Query(5, ge=1, le=20)
):
    result = graph_guided_retrieve(
        document_id=document_id,
        query=query,
        graph_entity_limit=graph_entity_limit,
        top_k=top_k
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result
'''

main_path.write_text(text, encoding="utf-8")

print("Phase 16 graph-guided retrieval patch applied successfully.")
