import re
from typing import List, Dict, Any

from app.generation.context_cleaner import clean_sentence_text


STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "of", "to", "and", "or", "in",
    "for", "with", "on", "by", "from", "this", "that", "it", "does",
    "do", "why", "how", "explain", "define", "meaning"
}


def split_into_sentences(text: str) -> List[str]:
    if not text:
        return []

    sentence_candidates = re.split(r"(?<=[.!?])\s+", text)
    sentences = []

    for sentence in sentence_candidates:
        sentence = clean_sentence_text(sentence)

        if len(sentence) < 25:
            continue

        if is_noise_sentence(sentence):
            continue

        sentences.append(sentence)

    return sentences


def is_noise_sentence(sentence: str) -> bool:
    sentence_lower = sentence.lower().strip()

    noise_starts = [
        "chapter ",
        "page ",
        "this chapter prepares",
        "practice saying",
        "component what it does",
    ]

    for start in noise_starts:
        if sentence_lower.startswith(start):
            return True

    return False


def extract_query_terms(query: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", query.lower())

    terms = [
        word for word in words
        if word not in STOPWORDS and len(word) > 1
    ]

    return terms


def score_sentence(sentence: str, query_terms: List[str]) -> float:
    sentence_lower = sentence.lower()
    score = 0.0

    for term in query_terms:
        if term in sentence_lower:
            score += 2.0

    important_markers = [
        "stands for",
        "means",
        "refers to",
        "retrieval-augmented generation",
        "retrieval augmented generation",
        "adds a retrieval step",
        "adding a retrieval step",
        "before generation",
        "before generating",
        "search your document corpus",
        "search a document corpus",
        "provide the relevant passages",
        "relevant passages as context",
        "frozen knowledge",
        "reduces hallucination",
        "grounds the answer",
        "private or recent data"
    ]

    for marker in important_markers:
        if marker in sentence_lower:
            score += 1.5

    if 60 <= len(sentence) <= 350:
        score += 0.5

    return score


def normalize_for_dedup(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def token_set(text: str) -> set:
    return set(normalize_for_dedup(text).split())


def is_similar_to_existing(sentence: str, existing_sentences: List[str]) -> bool:
    current_tokens = token_set(sentence)

    if not current_tokens:
        return True

    for existing in existing_sentences:
        existing_tokens = token_set(existing)

        if not existing_tokens:
            continue

        overlap = len(current_tokens.intersection(existing_tokens))
        union = len(current_tokens.union(existing_tokens))

        if union == 0:
            continue

        similarity = overlap / union

        if similarity >= 0.72:
            return True

    return False


def extract_evidence_sentences(
    query: str,
    results: List[Dict[str, Any]],
    max_evidence: int = 8
) -> List[Dict[str, Any]]:

    query_terms = extract_query_terms(query)
    evidence_items = []

    for result in results:
        content = result.get("content", "")
        sentences = split_into_sentences(content)

        for sentence in sentences:
            score = score_sentence(sentence, query_terms)

            if score <= 0:
                continue

            evidence_items.append(
                {
                    "sentence": sentence,
                    "score": score,
                    "source_id": result.get("source_id"),
                    "citation": result.get("citation"),
                    "chunk_id": result.get("chunk_id"),
                    "document_id": result.get("document_id"),
                    "source_file_name": result.get("source_file_name"),
                    "page_number": result.get("page_number")
                }
            )

    evidence_items.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    deduplicated = []
    existing_sentences = []

    for item in evidence_items:
        sentence = item["sentence"]

        if is_similar_to_existing(sentence, existing_sentences):
            continue

        deduplicated.append(item)
        existing_sentences.append(sentence)

        if len(deduplicated) >= max_evidence:
            break

    return deduplicated


def build_evidence_context(evidence_items: List[Dict[str, Any]]) -> str:
    context_lines = []

    for item in evidence_items:
        source_id = item.get("source_id", "S?")
        citation = item.get("citation", "")
        sentence = item.get("sentence", "")

        context_lines.append(
            f"{source_id}: {sentence} {citation}"
        )

    return "\n".join(context_lines)
