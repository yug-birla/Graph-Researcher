
from typing import Dict, Any, Optional

from app.graph.graph_storage import read_document_graph


def list_entities(
    document_id: str,
    limit: int = 50,
    entity_type: Optional[str] = None
) -> Dict[str, Any]:

    graph = read_document_graph(document_id)

    if graph is None:
        return {
            "status": "failed",
            "message": "Graph not found. Build the graph first.",
            "entities": []
        }

    entities = graph.entities

    if entity_type:
        entities = [
            entity for entity in entities
            if entity.entity_type.lower() == entity_type.lower()
        ]

    return {
        "status": "success",
        "document_id": document_id,
        "total_entities": len(entities),
        "returned_entities": len(entities[:limit]),
        "entities": entities[:limit]
    }


def search_entities(
    document_id: str,
    query: str,
    limit: int = 20
) -> Dict[str, Any]:

    graph = read_document_graph(document_id)

    if graph is None:
        return {
            "status": "failed",
            "message": "Graph not found. Build the graph first.",
            "entities": []
        }

    query_lower = query.lower().strip()

    matched = [
        entity for entity in graph.entities
        if query_lower in entity.name.lower()
        or query_lower in entity.entity_id.lower()
    ]

    return {
        "status": "success",
        "document_id": document_id,
        "query": query,
        "total_matches": len(matched),
        "entities": matched[:limit]
    }


def get_entity_neighborhood(
    document_id: str,
    entity: str,
    limit: int = 50
) -> Dict[str, Any]:

    graph = read_document_graph(document_id)

    if graph is None:
        return {
            "status": "failed",
            "message": "Graph not found. Build the graph first.",
            "nodes": [],
            "edges": []
        }

    entity_lower = entity.lower().strip()

    matched_entity = None

    for item in graph.entities:
        if (
            item.entity_id.lower() == entity_lower
            or item.name.lower() == entity_lower
            or entity_lower in item.name.lower()
        ):
            matched_entity = item
            break

    if matched_entity is None:
        return {
            "status": "failed",
            "message": "Entity not found in graph.",
            "entity": entity,
            "nodes": [],
            "edges": []
        }

    related_edges = []

    for relation in graph.relations:
        if (
            relation.source_entity_id == matched_entity.entity_id
            or relation.target_entity_id == matched_entity.entity_id
        ):
            related_edges.append(relation)

    related_edges = related_edges[:limit]

    node_ids = {matched_entity.entity_id}

    for edge in related_edges:
        node_ids.add(edge.source_entity_id)
        node_ids.add(edge.target_entity_id)

    nodes = [
        graph_entity for graph_entity in graph.entities
        if graph_entity.entity_id in node_ids
    ]

    return {
        "status": "success",
        "document_id": document_id,
        "center_entity": matched_entity,
        "total_related_edges": len(related_edges),
        "nodes": nodes,
        "edges": related_edges
    }
