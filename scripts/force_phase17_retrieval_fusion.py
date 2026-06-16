from pathlib import Path

path = Path("app/generation/answer_service.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

# 1. Ensure import exists
if "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph" not in text:
    text = "from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph\n" + text

# 2. Ensure function signature supports graph retrieval
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

# 3. Insert fusion block after sourced_results is created
target = '''    cleaned_results = clean_retrieved_results(retrieved_results)
    sourced_results = attach_source_ids(cleaned_results)

    citations = create_citation_objects(sourced_results)
'''

replacement = '''    cleaned_results = clean_retrieved_results(retrieved_results)
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

    # Re-attach source IDs after fusion because graph-added chunks also need source IDs.
    sourced_results = attach_source_ids(sourced_results)

    citations = create_citation_objects(sourced_results)
'''

if "fusion_result = fuse_retrieval_results_with_graph" not in text:
    if target in text:
        text = text.replace(target, replacement)
        print("Inserted fusion block.")
    else:
        print("ERROR: Could not find sourced_results block.")
else:
    print("Fusion block already exists.")

# 4. Ensure retrieval_fusion appears in final response
if '"retrieval_fusion":' not in text:
    final_target = '''        "graph_context": graph_context,
        "citations": citations,
'''

    final_replacement = '''        "graph_context": graph_context,
        "retrieval_fusion": fusion_result if "fusion_result" in locals() else {
            "fusion_used": False,
            "reason": "Fusion result was not created."
        },
        "citations": citations,
'''

    if final_target in text:
        text = text.replace(final_target, final_replacement)
        print("Inserted retrieval_fusion in final response.")
    else:
        print("ERROR: Could not find graph_context return block.")
else:
    print("retrieval_fusion already exists in return.")

path.write_text(text, encoding="utf-8")
print("Phase 17 force patch completed.")
