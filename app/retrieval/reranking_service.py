from functools import lru_cache
from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

from app.core.config import settings


@lru_cache(maxsize=1)
def get_reranker_model():
    return CrossEncoder(settings.RERANKER_MODEL_NAME, device="cpu")


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int
) -> List[Dict[str, Any]]:

    if not results:
        return []

    if not settings.ENABLE_RERANKER:
        return results[:top_k]

    try:
        model = get_reranker_model()

        pairs = [
            [query, result.get("content", "")]
            for result in results
        ]

        rerank_scores = model.predict(pairs)

        reranked_results = []

        for result, rerank_score in zip(results, rerank_scores):
            result = dict(result)
            result["original_score"] = result.get("score")
            result["rerank_score"] = float(rerank_score)
            result["score"] = float(rerank_score)
            reranked_results.append(result)

        reranked_results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return reranked_results[:top_k]

    except Exception as error:
        fallback_results = []

        for result in results[:top_k]:
            result = dict(result)
            result["rerank_error"] = str(error)
            fallback_results.append(result)

        return fallback_results
