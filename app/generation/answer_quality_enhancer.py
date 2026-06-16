
from typing import Any, Dict, List


SHORT_ANSWER_WORD_LIMIT = 70


def to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}

    if isinstance(obj, dict):
        return obj

    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass

    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass

    if hasattr(obj, "__dict__"):
        try:
            return dict(obj.__dict__)
        except Exception:
            pass

    return {}


def value_from(data: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if value not in [None, ""]:
            return str(value)

    metadata = data.get("metadata")

    if isinstance(metadata, dict):
        for key in keys:
            value = metadata.get(key)
            if value not in [None, ""]:
                return str(value)

    return default


def text_from_source(source: Dict[str, Any]) -> str:
    return value_from(
        source,
        [
            "text",
            "content",
            "chunk_text",
            "page_text",
            "cleaned_text",
            "raw_text",
            "text_preview",
            "preview",
            "chunk_preview",
            "body"
        ],
        ""
    )


def normalize_sources(raw_sources: Any, raw_citations: Any = None) -> List[Dict[str, Any]]:
    sources = []

    if isinstance(raw_sources, list):
        for item in raw_sources:
            sources.append(to_dict(item))

    if isinstance(raw_citations, list):
        for item in raw_citations:
            sources.append(to_dict(item))

    cleaned = []
    seen = set()

    for index, source in enumerate(sources):
        if not source:
            continue

        source_id = value_from(
            source,
            ["source_id", "citation_id", "id"],
            f"S{index + 1}"
        )

        chunk_id = value_from(
            source,
            ["chunk_id", "source_chunk_id", "chunk", "chunk_index", "id"],
            source_id
        )

        text = text_from_source(source)

        document_name = value_from(
            source,
            ["document_name", "source_file_name", "file_name", "filename", "document_title"],
            "Selected document"
        )

        page = value_from(
            source,
            ["page_number", "page", "page_no", "page_index"],
            "Not available"
        )

        key = f"{source_id}|{chunk_id}|{page}"

        if key in seen:
            continue

        seen.add(key)

        cleaned.append({
            "source_id": source_id,
            "chunk_id": chunk_id,
            "document_name": document_name,
            "page": page,
            "text": text,
            "raw": source
        })

    return cleaned[:6]


def is_answer_too_short(answer: str) -> bool:
    if not answer:
        return True

    word_count = len(answer.split())

    if word_count < SHORT_ANSWER_WORD_LIMIT:
        return True

    weak_phrases = [
        "i could not find",
        "not enough information",
        "maternity leave",
        "rag is retrieval-augmented generation",
        "the answer is"
    ]

    lower = answer.lower().strip()

    for phrase in weak_phrases:
        if lower == phrase or lower.startswith(phrase) and word_count < 90:
            return True

    return False


def source_label(index: int, source: Dict[str, Any]) -> str:
    sid = source.get("source_id") or f"S{index + 1}"

    if str(sid).upper().startswith("S"):
        return str(sid)

    return f"S{index + 1}"


def make_key_points_from_sources(query: str, sources: List[Dict[str, Any]]) -> List[str]:
    points = []

    for index, source in enumerate(sources[:4]):
        text = source.get("text", "").strip()
        label = source_label(index, source)

        if not text:
            continue

        cleaned = " ".join(text.split())

        if len(cleaned) > 290:
            cleaned = cleaned[:290].rsplit(" ", 1)[0] + "..."

        points.append(f"- {cleaned} [{label}]")

    return points


def build_detailed_evidence_answer(
    query: str,
    original_answer: str,
    sources: List[Dict[str, Any]]
) -> str:
    if not sources:
        return original_answer or "I could not find enough grounded evidence in the indexed document to answer this clearly."

    direct_answer = (original_answer or "").strip()

    if not direct_answer or is_answer_too_short(direct_answer):
        direct_answer = (
            "Based on the retrieved document evidence, the answer is connected to the points below. "
            "The indexed sources provide supporting context, but the final interpretation should be verified from the cited source chunks."
        )

    key_points = make_key_points_from_sources(query=query, sources=sources)

    evidence_lines = []

    for index, source in enumerate(sources[:5]):
        label = source_label(index, source)
        document_name = source.get("document_name", "Selected document")
        page = source.get("page", "Not available")
        chunk_id = source.get("chunk_id", label)

        evidence_lines.append(
            f"- [{label}] Document: {document_name}; Page: {page}; Chunk: {chunk_id}"
        )

    answer_parts = []

    answer_parts.append("Direct answer")
    answer_parts.append(direct_answer)

    if key_points:
        answer_parts.append("\nKey evidence from the document")
        answer_parts.extend(key_points)

    answer_parts.append("\nSources used")
    answer_parts.extend(evidence_lines)

    answer_parts.append(
        "\nNote\nThis answer is grounded in the retrieved chunks above. "
        "If a page number is unavailable, it means the parser did not expose page metadata for that source."
    )

    return "\n".join(answer_parts)


def safe_enhance_answer_for_response(local_vars: Dict[str, Any]) -> str:
    """
    Designed to be called from answer_service response dict using locals().
    It avoids crashing the /ask endpoint even if variable names differ.
    """

    try:
        answer = (
            local_vars.get("answer")
            or local_vars.get("final_answer")
            or local_vars.get("generated_answer")
            or local_vars.get("response_text")
            or ""
        )

        query = local_vars.get("query") or ""

        request_obj = local_vars.get("request")

        if not query and request_obj is not None:
            query = getattr(request_obj, "query", "")

        sources = (
            local_vars.get("sourced_results")
            or local_vars.get("cleaned_results")
            or local_vars.get("retrieved_results")
            or local_vars.get("results")
            or []
        )

        citations = local_vars.get("citations") or []

        normalized_sources = normalize_sources(sources, citations)

        if is_answer_too_short(answer):
            return build_detailed_evidence_answer(
                query=str(query),
                original_answer=str(answer),
                sources=normalized_sources
            )

        # If answer is okay but has no citation marker, add source summary.
        if normalized_sources and "[S" not in str(answer):
            source_refs = []

            for index, source in enumerate(normalized_sources[:3]):
                label = source_label(index, source)
                page = source.get("page", "Not available")
                source_refs.append(f"[{label}: page {page}]")

            return str(answer).strip() + "\n\nSources: " + ", ".join(source_refs)

        return str(answer)

    except Exception:
        return str(
            local_vars.get("answer")
            or local_vars.get("final_answer")
            or local_vars.get("generated_answer")
            or local_vars.get("response_text")
            or ""
        )
