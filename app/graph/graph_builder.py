
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.storage.processed_storage import (
    read_processed_chunks,
    read_processed_metadata
)
from app.schemas.graph_schema import (
    DocumentGraph,
    GraphEntity,
    GraphRelation
)
from app.graph.entity_extractor import extract_entities_from_text
from app.graph.relation_extractor import extract_relations_from_text
from app.graph.graph_storage import save_document_graph


def get_value(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def add_unique(existing_list: List, value):
    if value is None:
        return

    if value not in existing_list:
        existing_list.append(value)


def build_document_graph(document_id: str) -> Dict[str, Any]:
    chunks = read_processed_chunks(document_id)

    if chunks is None:
        return {
            "status": "failed",
            "message": "No processed chunks found for this document. Upload and process the document first.",
            "document_id": document_id
        }

    metadata = read_processed_metadata(document_id) or {}
    source_file_name = None

    if isinstance(metadata, dict):
        source_file_name = metadata.get("source_file_name") or metadata.get("filename")

    entity_map: Dict[str, GraphEntity] = {}
    relation_map: Dict[str, GraphRelation] = {}

    for chunk in chunks:
        content = (
            get_value(chunk, "content")
            or get_value(chunk, "text")
            or ""
        )

        if not content:
            continue

        chunk_id = get_value(chunk, "chunk_id", "")
        page_number = get_value(chunk, "page_number", None)

        extracted_entities = extract_entities_from_text(content)

        for item in extracted_entities:
            entity_id = item["entity_id"]

            if entity_id not in entity_map:
                entity_map[entity_id] = GraphEntity(
                    entity_id=entity_id,
                    name=item["name"],
                    entity_type=item["entity_type"],
                    mention_count=0
                )

            entity = entity_map[entity_id]
            entity.mention_count += content.lower().count(item["name"].lower())

            add_unique(entity.chunk_ids, chunk_id)
            add_unique(entity.pages, page_number)

            if len(entity.evidence) < 5:
                entity.evidence.append(
                    {
                        "chunk_id": chunk_id,
                        "page_number": page_number,
                        "text_preview": content[:250]
                    }
                )

        extracted_relations = extract_relations_from_text(
            text=content,
            entities=extracted_entities
        )

        for item in extracted_relations:
            rel_id = item["relation_id"]

            if rel_id not in relation_map:
                relation_map[rel_id] = GraphRelation(
                    relation_id=rel_id,
                    source_entity_id=item["source_entity_id"],
                    target_entity_id=item["target_entity_id"],
                    source_name=item["source_name"],
                    target_name=item["target_name"],
                    relation_type=item["relation_type"],
                    weight=0
                )

            relation = relation_map[rel_id]
            relation.weight += 1

            add_unique(relation.chunk_ids, chunk_id)
            add_unique(relation.pages, page_number)

            if len(relation.evidence) < 5:
                relation.evidence.append(
                    {
                        "chunk_id": chunk_id,
                        "page_number": page_number,
                        "sentence": item["evidence_sentence"]
                    }
                )

    entities = sorted(
        entity_map.values(),
        key=lambda entity: entity.mention_count,
        reverse=True
    )

    relations = sorted(
        relation_map.values(),
        key=lambda relation: relation.weight,
        reverse=True
    )

    graph = DocumentGraph(
        document_id=document_id,
        source_file_name=source_file_name,
        total_entities=len(entities),
        total_relations=len(relations),
        entities=entities,
        relations=relations,
        build_metadata={
            "builder": "rule_based_entity_relation_extractor",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunk_count": len(chunks),
            "note": "This is the graph foundation layer before adding a dedicated graph database."
        }
    )

    save_document_graph(graph)

    return {
        "status": "success",
        "message": "Document graph built successfully.",
        "document_id": document_id,
        "total_entities": graph.total_entities,
        "total_relations": graph.total_relations,
        "top_entities": [
            {
                "entity_id": entity.entity_id,
                "name": entity.name,
                "type": entity.entity_type,
                "mention_count": entity.mention_count
            }
            for entity in entities[:15]
        ],
        "top_relations": [
            {
                "source": relation.source_name,
                "relation": relation.relation_type,
                "target": relation.target_name,
                "weight": relation.weight
            }
            for relation in relations[:15]
        ]
    }
