
import re
from typing import Any


BAD_ENTITY_NAMES = {
    "what", "why", "when", "where", "who", "how",
    "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "they", "them",
    "page", "chapter", "section", "paragraph", "figure", "table",
    "contents", "overview", "summary", "introduction", "conclusion",
    "question", "answer", "example", "note", "notes",
    "part", "step", "case", "item", "level", "scope"
}


BAD_SINGLE_WORDS = BAD_ENTITY_NAMES | {
    "one", "two", "three", "first", "second", "third",
    "good", "bad", "new", "old", "main", "basic", "advanced"
}


def get_value(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name or "")).strip()


def tokenize_name(name: str):
    return re.findall(r"[a-zA-Z0-9_]+", str(name or "").lower())


def is_noisy_entity_name(name: str) -> bool:
    name = normalize_name(name)

    if not name:
        return True

    name_lower = name.lower()
    tokens = tokenize_name(name)

    if name_lower in BAD_ENTITY_NAMES:
        return True

    if len(tokens) == 1 and tokens[0] in BAD_SINGLE_WORDS:
        return True

    if len(name) <= 1:
        return True

    # Very short uppercase words like IS, OR, TO are usually not entities.
    # Keep useful acronyms like RAG, LLM, API, OCR, SQL, NLP, BM25.
    useful_acronyms = {"rag", "llm", "api", "ocr", "sql", "nlp", "bm25", "gpt", "pdf", "mvp"}

    if name.isupper() and len(name) <= 3 and name_lower not in useful_acronyms:
        return True

    if name_lower.startswith("chapter ") and len(tokens) <= 4:
        return True

    if name_lower.startswith("page ") and len(tokens) <= 4:
        return True

    return False


def is_noisy_relation(relation: Any) -> bool:
    source = get_value(relation, "source_name") or get_value(relation, "source")
    target = get_value(relation, "target_name") or get_value(relation, "target")
    relation_type = str(get_value(relation, "relation_type", "")).upper()

    if is_noisy_entity_name(source):
        return True

    if is_noisy_entity_name(target):
        return True

    # IS_A from rule-based extraction is noisy unless both sides look meaningful.
    if relation_type == "IS_A":
        target_tokens = tokenize_name(target)

        if len(target_tokens) == 1 and target_tokens[0] in BAD_SINGLE_WORDS:
            return True

    return False


def is_low_quality_chunk_text(text: str) -> bool:
    text = str(text or "").strip()

    if not text:
        return True

    lower = text.lower()
    dot_leaders = len(re.findall(r"\.{5,}", text))
    words = re.findall(r"[a-zA-Z]{3,}", text)

    # Table-of-content pages often contain many dot leaders.
    if dot_leaders >= 3:
        return True

    if "table of contents" in lower and dot_leaders >= 1:
        return True

    # Mostly heading/index text, not answer evidence.
    heading_markers = [
        "chapter ",
        "page ",
        "................................................................"
    ]

    marker_count = sum(1 for marker in heading_markers if marker in lower)

    if marker_count >= 2 and len(words) < 90:
        return True

    return False



def is_meta_showcase_chunk_text(text: str) -> bool:
    """
    Filters chunks that are about project promotion, resume bullets,
    LinkedIn drafts, portfolio text, or deployment brag text.

    These chunks may contain good keywords, but they are usually not
    good answer evidence for conceptual questions like "What is RAG?"
    """

    lower = str(text or "").lower()

    bad_phrases = [
        "linkedin post",
        "linkedin post draft",
        "copy and customise",
        "copy and customize",
        "i just shipped",
        "resume bullet",
        "portfolio",
        "general software engineering",
        "built vectorless rag platform",
        "most ambitious project",
        "deployment framework",
        "zero external dependencies"
    ]

    return any(phrase in lower for phrase in bad_phrases)



def is_cover_or_marketing_chunk_text(text: str) -> bool:
    """
    Filters cover pages, marketing pages, career-pitch pages,
    and table-like project overview pages.

    These chunks often contain the query keyword but are weak evidence.
    """

    lower = str(text or "").lower()

    bad_phrases = [
        "master guide",
        "what you will build",
        "why it matters for your career",
        "from absolute beginner",
        "senior ai / ml / mlops engineer",
        "production-grade rag system",
        "no vector databases",
        "no gpu",
        "no paid apis",
        "demonstrates mastery",
        "proves you can ship",
        "shows you understand",
        "career",
        "portfolio-ready",
        "resume-worthy"
    ]

    hit_count = sum(1 for phrase in bad_phrases if phrase in lower)

    return hit_count >= 2
