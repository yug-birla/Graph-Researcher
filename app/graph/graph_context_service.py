
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
