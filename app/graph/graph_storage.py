
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
