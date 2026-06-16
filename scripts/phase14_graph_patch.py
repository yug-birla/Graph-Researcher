from pathlib import Path

# =====================================================
# Graph schemas
# =====================================================

Path("app/schemas/graph_schema.py").write_text(r'''
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class GraphEntity(BaseModel):
    entity_id: str
    name: str
    entity_type: str = "CONCEPT"

    mention_count: int = 0
    pages: List[int] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)

    aliases: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class GraphRelation(BaseModel):
    relation_id: str
    source_entity_id: str
    target_entity_id: str

    source_name: str
    target_name: str

    relation_type: str = "RELATED_TO"
    weight: int = 1

    pages: List[int] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class DocumentGraph(BaseModel):
    document_id: str
    source_file_name: Optional[str] = None

    total_entities: int = 0
    total_relations: int = 0

    entities: List[GraphEntity] = Field(default_factory=list)
    relations: List[GraphRelation] = Field(default_factory=list)

    build_metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
''', encoding="utf-8")


# =====================================================
# Entity extractor
# =====================================================

Path("app/graph/entity_extractor.py").write_text(r'''
import re
from typing import List, Dict, Any


STOP_ENTITIES = {
    "The", "This", "That", "These", "Those", "It", "They", "We", "You",
    "Page", "Chapter", "Figure", "Table", "Example", "Answer", "Question",
    "Introduction", "Conclusion", "Summary", "Overview"
}


def normalize_entity_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name or "").strip()
    name = name.strip(".,;:()[]{}")
    return name


def make_entity_id(name: str) -> str:
    cleaned = name.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned[:80] or "unknown_entity"


def classify_entity(name: str) -> str:
    if re.fullmatch(r"[A-Z][A-Z0-9]{1,9}", name):
        return "ACRONYM"

    org_markers = [
        "University", "Institute", "Corporation", "Corp", "Inc", "Ltd",
        "Company", "OpenAI", "Microsoft", "Google", "Amazon"
    ]

    if any(marker.lower() in name.lower() for marker in org_markers):
        return "ORGANIZATION"

    if any(char.isdigit() for char in name):
        return "TECHNICAL_TERM"

    if "-" in name or "/" in name:
        return "TECHNICAL_TERM"

    return "CONCEPT"


def is_valid_entity(name: str) -> bool:
    if not name:
        return False

    if name in STOP_ENTITIES:
        return False

    if len(name) < 2:
        return False

    if len(name) > 80:
        return False

    if name.lower() in {"and", "or", "but", "with", "from", "into"}:
        return False

    return True


def extract_entities_from_text(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    candidates = []

    # Acronyms like RAG, LLM, API, OCR
    for match in re.finditer(r"\b[A-Z][A-Z0-9]{1,9}\b", text):
        candidates.append(match.group(0))

    # Capitalized technical phrases like Retrieval-Augmented Generation
    capitalized_phrase_pattern = (
        r"\b[A-Z][a-zA-Z0-9]*(?:[-/][A-Z]?[a-zA-Z0-9]+)?"
        r"(?:\s+[A-Z][a-zA-Z0-9]*(?:[-/][A-Z]?[a-zA-Z0-9]+)?){0,5}\b"
    )

    for match in re.finditer(capitalized_phrase_pattern, text):
        candidates.append(match.group(0))

    cleaned_entities = []

    seen = set()

    for candidate in candidates:
        name = normalize_entity_name(candidate)

        if not is_valid_entity(name):
            continue

        entity_id = make_entity_id(name)

        if entity_id in seen:
            continue

        seen.add(entity_id)

        cleaned_entities.append(
            {
                "entity_id": entity_id,
                "name": name,
                "entity_type": classify_entity(name)
            }
        )

    return cleaned_entities


def split_sentences(text: str) -> List[str]:
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if len(part.strip()) > 20]
''', encoding="utf-8")


# =====================================================
# Relation extractor
# =====================================================

Path("app/graph/relation_extractor.py").write_text(r'''
import itertools
import re
from typing import List, Dict, Any

from app.graph.entity_extractor import make_entity_id, split_sentences


VERB_RELATION_MAP = {
    "stands for": "STANDS_FOR",
    "refers to": "REFERS_TO",
    "uses": "USES",
    "use": "USES",
    "retrieves": "RETRIEVES",
    "retrieve": "RETRIEVES",
    "generates": "GENERATES",
    "generate": "GENERATES",
    "provides": "PROVIDES",
    "provide": "PROVIDES",
    "reduces": "REDUCES",
    "reduce": "REDUCES",
    "improves": "IMPROVES",
    "improve": "IMPROVES",
    "contains": "CONTAINS",
    "include": "INCLUDES",
    "includes": "INCLUDES",
    "is": "IS_A",
    "are": "IS_A"
}


def relation_id(source_id: str, relation_type: str, target_id: str) -> str:
    return f"{source_id}__{relation_type.lower()}__{target_id}"[:160]


def entity_appears_in_sentence(entity_name: str, sentence: str) -> bool:
    pattern = r"\b" + re.escape(entity_name) + r"\b"
    return re.search(pattern, sentence, flags=re.IGNORECASE) is not None


def extract_relations_from_text(
    text: str,
    entities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if not text or len(entities) < 2:
        return []

    relations = []
    sentences = split_sentences(text)

    for sentence in sentences:
        present_entities = [
            entity for entity in entities
            if entity_appears_in_sentence(entity["name"], sentence)
        ]

        # Avoid relation explosion
        present_entities = present_entities[:6]

        if len(present_entities) < 2:
            continue

        relation_type = detect_relation_type(sentence)

        for source, target in itertools.combinations(present_entities, 2):
            if source["entity_id"] == target["entity_id"]:
                continue

            relations.append(
                {
                    "relation_id": relation_id(
                        source["entity_id"],
                        relation_type,
                        target["entity_id"]
                    ),
                    "source_entity_id": source["entity_id"],
                    "target_entity_id": target["entity_id"],
                    "source_name": source["name"],
                    "target_name": target["name"],
                    "relation_type": relation_type,
                    "evidence_sentence": sentence
                }
            )

    return relations


def detect_relation_type(sentence: str) -> str:
    sentence_lower = sentence.lower()

    for phrase, relation_type in VERB_RELATION_MAP.items():
        if phrase in sentence_lower:
            return relation_type

    return "RELATED_TO"
''', encoding="utf-8")


# =====================================================
# Graph storage
# =====================================================

Path("app/graph/graph_storage.py").write_text(r'''
import json
from typing import Optional

from app.core.config import settings
from app.schemas.graph_schema import DocumentGraph


def get_graph_path(document_id: str):
    document_dir = settings.PROCESSED_DIR / document_id
    document_dir.mkdir(parents=True, exist_ok=True)
    return document_dir / "graph.json"


def save_document_graph(graph: DocumentGraph) -> None:
    graph_path = get_graph_path(graph.document_id)

    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(
            graph.model_dump(),
            f,
            indent=2,
            ensure_ascii=False
        )


def read_document_graph(document_id: str) -> Optional[DocumentGraph]:
    graph_path = get_graph_path(document_id)

    if not graph_path.exists():
        return None

    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return DocumentGraph(**data)
''', encoding="utf-8")


# =====================================================
# Graph builder
# =====================================================

Path("app/graph/graph_builder.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# Graph query service
# =====================================================

Path("app/graph/graph_query_service.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# Patch main.py
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8")

graph_imports = '''from app.graph.graph_builder import build_document_graph
from app.graph.graph_storage import read_document_graph
from app.graph.graph_query_service import (
    list_entities,
    search_entities,
    get_entity_neighborhood
)
'''

if "from app.graph.graph_builder import build_document_graph" not in text:
    text = graph_imports + text

old_phases = [
    "Phase 13 - Deployment Demo Stabilization",
    "Phase 12 - Hugging Face Hosted LLM Provider Hardening",
    "Phase 11 - Hugging Face Deployment Readiness",
    "Phase 10 - LLM Provider Abstraction",
    "Phase 9 - Answer Evaluation System",
    "Phase 8 - Retrieval Evaluation System"
]

for old in old_phases:
    text = text.replace(old, "Phase 14 - Graph Foundation Entity Relation Extraction")

if "# Graph foundation endpoints" not in text:
    text += '''

# Graph foundation endpoints

@app.post("/documents/{document_id}/graph/build")
def build_graph_for_document(document_id: str):
    result = build_document_graph(document_id)

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Graph build failed.")
        )

    return result


@app.get("/documents/{document_id}/graph")
def get_document_graph(document_id: str):
    graph = read_document_graph(document_id)

    if graph is None:
        raise HTTPException(
            status_code=404,
            detail="Graph not found. Build the graph first."
        )

    return graph


@app.get("/documents/{document_id}/graph/entities")
def get_graph_entities(
    document_id: str,
    limit: int = Query(50, ge=1, le=500),
    entity_type: Optional[str] = None
):
    result = list_entities(
        document_id=document_id,
        limit=limit,
        entity_type=entity_type
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result


@app.get("/documents/{document_id}/graph/search")
def search_graph_entities(
    document_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    result = search_entities(
        document_id=document_id,
        query=query,
        limit=limit
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result


@app.get("/documents/{document_id}/graph/neighborhood")
def get_graph_neighborhood(
    document_id: str,
    entity: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200)
):
    result = get_entity_neighborhood(
        document_id=document_id,
        entity=entity,
        limit=limit
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result
'''

main_path.write_text(text, encoding="utf-8")

print("Phase 14 graph foundation files created successfully.")
