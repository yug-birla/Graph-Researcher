import uuid
from functools import lru_cache
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from app.core.config import settings


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(path=str(settings.QDRANT_LOCAL_PATH))


def ensure_collection() -> None:
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    try:
        exists = client.collection_exists(collection_name)
    except Exception:
        exists = False

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )


def make_point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def upsert_chunk_vectors(points: List[Dict[str, Any]]) -> int:
    ensure_collection()
    client = get_qdrant_client()

    qdrant_points = []

    for point in points:
        qdrant_points.append(
            PointStruct(
                id=make_point_id(point["chunk_id"]),
                vector=point["vector"],
                payload=point["payload"]
            )
        )

    if not qdrant_points:
        return 0

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=qdrant_points
    )

    return len(qdrant_points)


def search_vectors(
    query_vector: List[float],
    top_k: int,
    document_id: Optional[str] = None
):
    ensure_collection()
    client = get_qdrant_client()

    query_filter = None

    if document_id:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )

    try:
        result = client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        return result.points

    except Exception:
        return client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )


def delete_vectors_for_document(document_id: str) -> None:
    ensure_collection()
    client = get_qdrant_client()

    client.delete(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )
