from pathlib import Path
import re

# =====================================================
# 1. Remove BOM from Python files
# =====================================================

for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")


# =====================================================
# 2. Graph context service
# =====================================================

Path("app/graph/graph_context_service.py").write_text(r'''
import re
from typing import Dict, Any, List, Optional

from app.graph.graph_storage import read_document_graph


STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "of", "to", "and", "or",
    "in", "on", "for", "with", "from", "by", "how", "why", "explain",
    "define", "meaning", "does", "do", "it", "this", "that"
}


def tokenize_query(query: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", (query or "").lower())

    return [
        word for word in words
        if word not in STOPWORDS and len(word) > 1
    ]


def entity_relevance_score(entity, query_terms: List[str]) -> float:
    if not query_terms:
        return 0.0

    name_lower = entity.name.lower()
    entity_id_lower = entity.entity_id.lower()

    score = 0.0

    for term in query_terms:
        if term == name_lower or term == entity_id_lower:
            score += 8.0
        elif term in name_lower:
            score += 4.0
        elif term in entity_id_lower:
            score += 3.0

    score += min(entity.mention_count, 10) * 0.15

    return score


def build_graph_context_for_query(
    document_id: Optional[str],
    query: str,
    limit: int = 8
) -> Dict[str, Any]:
    """
    Finds graph entities and relations related to the query.

    This does not replace vector retrieval.
    It adds structured graph context to the final answer pipeline.
    """

    if not document_id:
        return {
            "graph_available": False,
            "reason": "No document_id provided.",
            "matched_entities": [],
            "matched_relations": [],
            "context_text": ""
        }

    graph = read_document_graph(document_id)

    if graph is None:
        return {
            "graph_available": False,
            "reason": "Graph not built for this document.",
            "matched_entities": [],
            "matched_relations": [],
            "context_text": ""
        }

    query_terms = tokenize_query(query)

    scored_entities = []

    for entity in graph.entities:
        score = entity_relevance_score(entity, query_terms)

        if score > 0:
            scored_entities.append((score, entity))

    scored_entities.sort(key=lambda item: item[0], reverse=True)

    matched_entities = [
        entity for score, entity in scored_entities[:limit]
    ]

    matched_entity_ids = {
        entity.entity_id for entity in matched_entities
    }

    matched_relations = []

    for relation in graph.relations:
        if (
            relation.source_entity_id in matched_entity_ids
            or relation.target_entity_id in matched_entity_ids
        ):
            matched_relations.append(relation)

    matched_relations = sorted(
        matched_relations,
        key=lambda relation: relation.weight,
        reverse=True
    )[:limit]

    context_text = build_graph_context_text(
        matched_entities=matched_entities,
        matched_relations=matched_relations
    )

    return {
        "graph_available": True,
        "document_id": document_id,
        "source_file_name": graph.source_file_name,
        "query_terms": query_terms,
        "matched_entities": [
            {
                "entity_id": entity.entity_id,
                "name": entity.name,
                "entity_type": entity.entity_type,
                "mention_count": entity.mention_count,
                "pages": entity.pages[:10],
                "chunk_ids": entity.chunk_ids[:10]
            }
            for entity in matched_entities
        ],
        "matched_relations": [
            {
                "relation_id": relation.relation_id,
                "source": relation.source_name,
                "relation_type": relation.relation_type,
                "target": relation.target_name,
                "weight": relation.weight,
                "pages": relation.pages[:10],
                "chunk_ids": relation.chunk_ids[:10]
            }
            for relation in matched_relations
        ],
        "context_text": context_text
    }


def build_graph_context_text(
    matched_entities,
    matched_relations
) -> str:
    lines = []

    if matched_entities:
        lines.append("Relevant graph entities:")

        for entity in matched_entities:
            pages = ", ".join(str(page) for page in entity.pages[:5])
            lines.append(
                f"- {entity.name} ({entity.entity_type}), mentions={entity.mention_count}, pages={pages}"
            )

    if matched_relations:
        lines.append("")
        lines.append("Relevant graph relations:")

        for relation in matched_relations:
            lines.append(
                f"- {relation.source_name} --{relation.relation_type}--> {relation.target_name} "
                f"(weight={relation.weight})"
            )

    return "\n".join(lines).strip()
''', encoding="utf-8")


# =====================================================
# 3. Patch query_schema.py
# =====================================================

Path("app/schemas/query_schema.py").write_text(r'''
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[str] = None

    top_k: int = Field(default=5, ge=1, le=20)
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"

    use_reranker: bool = True
    use_llm: bool = True

    # Phase 15:
    # Adds graph context from entities and relations when document graph exists.
    use_graph: bool = True
    graph_entity_limit: int = Field(default=8, ge=1, le=30)
''', encoding="utf-8")


# =====================================================
# 4. Patch prompt_builder.py
# =====================================================

Path("app/generation/prompt_builder.py").write_text(r'''
from app.generation.question_classifier import get_answer_instruction


def build_grounded_prompt(
    query: str,
    evidence_context: str,
    question_type: str
) -> str:
    """
    Builds a compact prompt.

    In Phase 15, evidence_context may contain:
    - retrieved source evidence
    - graph entity context
    - graph relation context

    The LLM still must answer only from supplied context.
    """

    instruction = get_answer_instruction(question_type)

    return f"""
Answer the question using only the supplied context.

Question type: {question_type}

Instruction: {instruction}

Rules:
- Do not use outside knowledge.
- Preserve citations like [S1] and [S2] when making factual claims from retrieved sources.
- Graph context can help explain entity relationships, but do not invent facts from it.
- If retrieved source evidence and graph context disagree, trust retrieved source evidence.
- Give a clear final answer, not notes.

Question:
{query}

Context:
{evidence_context}

Final answer:
""".strip()
''', encoding="utf-8")


# =====================================================
# 5. Patch answer_service.py safely
# =====================================================

answer_path = Path("app/generation/answer_service.py")
text = answer_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.graph.graph_context_service import build_graph_context_for_query" not in text:
    text = "from app.graph.graph_context_service import build_graph_context_for_query\n" + text

# Add graph params to function signature
text = text.replace(
'''    use_reranker: bool = True,
    use_llm: bool = True
) -> Dict[str, Any]:
''',
'''    use_reranker: bool = True,
    use_llm: bool = True,
    use_graph: bool = True,
    graph_entity_limit: int = 8
) -> Dict[str, Any]:
'''
)

# Add graph context after evidence_context construction
old_context_line = '''    evidence_context = build_evidence_context(evidence_items)
'''

new_context_block = '''    evidence_context = build_evidence_context(evidence_items)

    graph_context = build_graph_context_for_query(
        document_id=document_id,
        query=query,
        limit=graph_entity_limit
    ) if use_graph else {
        "graph_available": False,
        "reason": "Graph usage disabled.",
        "matched_entities": [],
        "matched_relations": [],
        "context_text": ""
    }

    graph_context_text = graph_context.get("context_text", "")

    if graph_context_text:
        evidence_context = (
            evidence_context
            + "\\n\\nStructured graph context:\\n"
            + graph_context_text
        )
'''

if old_context_line in text and "Structured graph context" not in text:
    text = text.replace(old_context_line, new_context_block)

# Add graph info to final return dictionary before citations
old_return_part = '''        "citations": citations,
        "evidence": evidence_items,
        "sources": sourced_results
'''

new_return_part = '''        "graph_used": bool(graph_context.get("matched_entities") or graph_context.get("matched_relations")),
        "graph_context": graph_context,
        "citations": citations,
        "evidence": evidence_items,
        "sources": sourced_results
'''

if old_return_part in text and '"graph_context": graph_context' not in text:
    text = text.replace(old_return_part, new_return_part)

answer_path.write_text(text, encoding="utf-8")


# =====================================================
# 6. Patch main.py
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

old_call = '''        use_reranker=request.use_reranker,
        use_llm=request.use_llm
'''

new_call = '''        use_reranker=request.use_reranker,
        use_llm=request.use_llm,
        use_graph=request.use_graph,
        graph_entity_limit=request.graph_entity_limit
'''

if old_call in text and "graph_entity_limit=request.graph_entity_limit" not in text:
    text = text.replace(old_call, new_call)

if "from app.graph.graph_context_service import build_graph_context_for_query" not in text:
    text = "from app.graph.graph_context_service import build_graph_context_for_query\n" + text

old_phases = [
    "Phase 14.1 - Graph Visualization UI",
    "Phase 14 - Graph Foundation Entity Relation Extraction",
    "Phase 13 - Deployment Demo Stabilization",
    "Phase 12 - Hugging Face Hosted LLM Provider Hardening",
]

for old in old_phases:
    text = text.replace(old, "Phase 15 - Graph-Augmented Answering")

if "# Graph context debug endpoint" not in text:
    text += '''

# Graph context debug endpoint

@app.get("/documents/{document_id}/graph/context")
def get_graph_context_for_question(
    document_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(8, ge=1, le=30)
):
    return build_graph_context_for_query(
        document_id=document_id,
        query=query,
        limit=limit
    )
'''

main_path.write_text(text, encoding="utf-8")

print("Phase 15 graph-augmented answering patch applied successfully.")
