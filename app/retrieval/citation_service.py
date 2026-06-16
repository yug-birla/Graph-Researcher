from typing import List, Dict, Any


def build_citation_text(payload: Dict[str, Any], source_id: str) -> str:
    source_file_name = payload.get("source_file_name", "Unknown file")
    page_number = payload.get("page_number")
    section_title = payload.get("section_title")

    parts = [source_id, source_file_name]

    if page_number:
        parts.append(f"page {page_number}")

    if section_title:
        parts.append(f"section: {section_title}")

    return "[" + " | ".join(parts) + "]"


def attach_source_ids(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    updated_results = []

    for index, result in enumerate(results, start=1):
        source_id = f"S{index}"

        payload = {
            "source_file_name": result.get("source_file_name"),
            "page_number": result.get("page_number"),
            "section_title": result.get("section_title")
        }

        result = dict(result)
        result["source_id"] = source_id
        result["citation"] = build_citation_text(payload, source_id)

        updated_results.append(result)

    return updated_results


def create_context_from_sources(
    results: List[Dict[str, Any]],
    max_context_chars: int
) -> str:
    context_parts = []
    used_chars = 0

    for result in results:
        source_id = result.get("source_id", "S?")
        citation = result.get("citation", "")
        content = result.get("content", "")

        context_piece = (
            f"{source_id}\n"
            f"Citation: {citation}\n"
            f"Content:\n{content}\n"
        )

        if used_chars + len(context_piece) > max_context_chars:
            remaining_chars = max_context_chars - used_chars

            if remaining_chars <= 0:
                break

            context_piece = context_piece[:remaining_chars]

        context_parts.append(context_piece)
        used_chars += len(context_piece)

    return "\n---\n".join(context_parts)


def create_citation_objects(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citations = []

    for result in results:
        content = result.get("content", "")

        citations.append(
            {
                "source_id": result.get("source_id"),
                "chunk_id": result.get("chunk_id"),
                "document_id": result.get("document_id"),
                "source_file_name": result.get("source_file_name"),
                "page_number": result.get("page_number"),
                "section_title": result.get("section_title"),
                "content_type": result.get("content_type"),
                "score": result.get("score"),
                "citation_text": result.get("citation"),
                "content_preview": content[:500],
                "metadata": result.get("metadata", {})
            }
        )

    return citations
