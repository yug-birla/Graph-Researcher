
import re
from typing import List, Dict, Any

from app.graph.graph_quality import is_noisy_entity_name


STOP_ENTITIES = {
    "The", "This", "That", "These", "Those", "It", "They", "We", "You",
    "Page", "Chapter", "Figure", "Table", "Example", "Answer", "Question",
    "Introduction", "Conclusion", "Summary", "Overview", "Paragraph",
    "What", "Why", "When", "Where", "Who", "How", "Is", "Are", "IS"
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

    if is_noisy_entity_name(name):
        return False

    if len(name) < 2:
        return False

    if len(name) > 90:
        return False

    return True


def extract_entities_from_text(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    candidates = []

    # Acronyms like RAG, LLM, API, OCR, BM25
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
