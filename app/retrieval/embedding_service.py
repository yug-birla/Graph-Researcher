from functools import lru_cache
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device="cpu")


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()

    return embeddings


def embed_text(text: str) -> List[float]:
    return embed_texts([text])[0]
