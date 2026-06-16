import re
from typing import List, Dict, Any


NOISE_PATTERNS = [
    r"Vectorless RAG Master Guide\s+Vectorless Enterprise Knowledge Intelligence Platform",
    r"Page\s+\d+\s+of\s+\d+",
    r"Chapter\s+\d+\s*[:\-].*?(?=\s{2,}|$)",
    r"Q\d+\s*:\s*",
    r"Ideal Answer",
    r"Practice saying these out loud.*?(?=\s{2,}|$)",
]


def clean_chunk_text(text: str) -> str:
    """
    Cleans noisy PDF/chunk text before answer generation.
    """

    if not text:
        return ""

    cleaned = text

    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(
            pattern,
            " ",
            cleaned,
            flags=re.IGNORECASE
        )

    cleaned = cleaned.replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" .", ".")
    cleaned = cleaned.replace(" ,", ",")
    cleaned = cleaned.strip()

    return cleaned


def clean_sentence_text(sentence: str) -> str:
    """
    Cleans one evidence sentence.
    """

    if not sentence:
        return ""

    cleaned = sentence

    cleaned = re.sub(r"^Q\d+\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^Ideal Answer\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)

    cleaned = cleaned.replace(" .", ".")
    cleaned = cleaned.replace(" ,", ",")
    cleaned = cleaned.strip()

    return cleaned


def clean_retrieved_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned_results = []

    for result in results:
        result = dict(result)
        result["raw_content"] = result.get("content", "")
        result["content"] = clean_chunk_text(result.get("content", ""))
        cleaned_results.append(result)

    return cleaned_results
