import re
from typing import List, Dict, Any

from app.core.config import settings


BAD_ANSWER_MARKERS = [
    "local llm generation failed",
    "i don't know",
    "i do not know",
    "unknown",
    "not enough information",
    "could not find",
    "cannot answer",
    "as an ai",
    "i am unable",
    "the evidence does not"
]


def answer_has_citation(answer: str) -> bool:
    if not answer:
        return False

    return bool(re.search(r"\[S\d+\]", answer))


def answer_is_too_short(answer: str) -> bool:
    if not answer:
        return True

    return len(answer.strip().split()) < settings.MIN_LLM_ANSWER_WORDS


def answer_repeats_prompt(answer: str) -> bool:
    answer_lower = answer.lower()

    prompt_markers = [
        "you are a research assistant",
        "answer the question using",
        "sources:",
        "question:",
        "evidence:",
        "final answer:"
    ]

    return any(marker in answer_lower for marker in prompt_markers)


def answer_has_bad_marker(answer: str) -> bool:
    answer_lower = answer.lower()

    return any(marker in answer_lower for marker in BAD_ANSWER_MARKERS)


def answer_is_mostly_citation(answer: str) -> bool:
    without_citations = re.sub(r"\[S\d+\]", "", answer).strip()

    return len(without_citations.split()) < 8


def is_answer_good_enough(answer: str) -> bool:
    """
    Quality gate for accepting LLM answer.

    If answer fails this, we use evidence-based fallback.
    """

    if answer_is_too_short(answer):
        return False

    if answer_repeats_prompt(answer):
        return False

    if answer_has_bad_marker(answer):
        return False

    if answer_is_mostly_citation(answer):
        return False

    if not answer_has_citation(answer):
        return False

    return True


def append_missing_citations(answer: str, sources: List[Dict[str, Any]]) -> str:
    """
    If model gives a good explanation but forgets citations,
    append top citations. Quality checker still decides acceptance.
    """

    if not answer:
        return answer

    if answer_has_citation(answer):
        return answer

    citation_ids = []

    for source in sources[:2]:
        source_id = source.get("source_id")

        if source_id:
            citation_ids.append(f"[{source_id}]")

    if not citation_ids:
        return answer

    return answer.strip() + " " + " ".join(citation_ids)
