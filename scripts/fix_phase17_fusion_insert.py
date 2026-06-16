from pathlib import Path

path = Path("app/generation/answer_service.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph" not in text:
    text = "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph\n" + text

old = '''    cleaned_results = clean_retrieved_results(retrieved_results)
    sourced_results = attach_source_ids(cleaned_results)

    citations = create_citation_objects(sourced_results)
'''

new = '''    cleaned_results = clean_retrieved_results(retrieved_results)
    sourced_results = attach_source_ids(cleaned_results)

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

    # Re-attach source IDs after fusion because graph-added chunks also need citations.
    sourced_results = attach_source_ids(sourced_results)

    citations = create_citation_objects(sourced_results)
'''

if old not in text:
    print("Could not find exact target block. No change made.")
else:
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print("Fusion block inserted successfully into answer_service.py")
