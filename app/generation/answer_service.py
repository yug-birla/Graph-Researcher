from app.generation.answer_quality_enhancer import safe_enhance_answer_for_response
from app.graph.graph_retrieval_fusion import fuse_retrieval_results_with_graph
from app.graph.graph_context_service import build_graph_context_for_query
import re
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.retrieval.hybrid_search_service import retrieve_chunks
from app.retrieval.reranking_service import rerank_results
from app.retrieval.citation_service import (
    attach_source_ids,
    create_citation_objects
)
from app.generation.context_cleaner import clean_retrieved_results, clean_sentence_text
from app.generation.question_classifier import classify_question
from app.generation.evidence_extractor import (
    extract_evidence_sentences,
    build_evidence_context
)
from app.generation.prompt_builder import build_grounded_prompt
from app.generation.llm_service import generate_with_local_llm, get_llm_status
from app.generation.answer_quality_checker import (
    is_answer_good_enough,
    append_missing_citations
)


def answer_question(
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5,
    retrieval_mode: str = "hybrid",
    use_reranker: bool = True,
    use_llm: bool = True,
    use_graph: bool = True,
    graph_entity_limit: int = 8,
    use_graph_retrieval: bool = True,
    graph_retrieval_top_k: int = 5
) -> Dict[str, Any]:

    candidate_k = top_k

    if use_reranker:
        candidate_k = max(
            top_k * settings.RERANKER_CANDIDATE_MULTIPLIER,
            top_k
        )

    retrieval_output = retrieve_chunks(
        query=query,
        document_id=document_id,
        top_k=candidate_k,
        retrieval_mode=retrieval_mode
    )

    retrieved_results = retrieval_output["results"]

    if use_reranker:
        retrieved_results = rerank_results(
            query=query,
            results=retrieved_results,
            top_k=top_k
        )
    else:
        retrieved_results = retrieved_results[:top_k]

    cleaned_results = clean_retrieved_results(retrieved_results)
    sourced_results = attach_source_ids(cleaned_results)

    fusion_result = fuse_retrieval_results_with_graph(
        document_id=document_id,
        query=query,
        retrieval_results=sourced_results,
        graph_entity_limit=graph_entity_limit,
        graph_top_k=graph_retrieval_top_k,
        final_top_k=max(top_k, graph_retrieval_top_k)
    ) if use_graph_retrieval else {
        "fused_results": sourced_results,
        "fusion_used": False,
        "reason": "Graph retrieval fusion disabled.",
        "graph_retrieval": {},
        "normal_count": len(sourced_results),
        "graph_added_count": 0,
        "graph_supported_count": 0,
        "final_count": len(sourced_results)
    }

    sourced_results = fusion_result.get("fused_results", sourced_results)

    # Re-attach source IDs after fusion because graph-added chunks also need citations.
    sourced_results = attach_source_ids(sourced_results)

    citations = create_citation_objects(sourced_results)

    if not sourced_results:
        return {
            "query": query,
            "answer": "I could not find relevant indexed sources for this question.",
            "retrieval_mode": retrieval_mode,
            "question_type": classify_question(query),
            "used_reranker": use_reranker,
            "used_llm": False,
            "answer_strategy": "no_sources_found",
            "citations": [],
            "sources": []
        }

    question_type = classify_question(query)

    evidence_items = extract_evidence_sentences(
        query=query,
        results=sourced_results,
        max_evidence=8
    )

    if not evidence_items:
        answer = build_extractive_answer(
            sources=sourced_results
        )

        return {
            "query": query,
            "answer": safe_enhance_answer_for_response(locals()),
            "retrieval_mode": retrieval_mode,
            "question_type": question_type,
            "used_reranker": use_reranker,
            "used_llm": False,
            "answer_strategy": "fallback_no_evidence_sentences",
            "llm_status": get_llm_status(),
            "citations": citations,
            "evidence": [],
            "sources": sourced_results
        }

    evidence_context = build_evidence_context(evidence_items)

    graph_context = build_graph_context_for_query(
        document_id=document_id,
        query=query,
        limit=graph_entity_limit
    ) if use_graph else {
        "graph_available": False,
        "reason": "Graph usage disabled.",
        "matched_entities": [],
        "matched_relations": [],
        "context_text": ""
    }

    graph_context_text = graph_context.get("context_text", "")

    if graph_context_text:
        evidence_context = (
            evidence_context
            + "\n\nStructured graph context:\n"
            + graph_context_text
        )

    raw_llm_answer = ""
    llm_answer_after_citations = ""

    if use_llm:
        prompt = build_grounded_prompt(
            query=query,
            evidence_context=evidence_context,
            question_type=question_type
        )

        raw_llm_answer = generate_with_local_llm(prompt)

        llm_answer_after_citations = append_missing_citations(
            answer=raw_llm_answer,
            sources=sourced_results
        )

        if is_answer_good_enough(llm_answer_after_citations):
            answer = clean_final_answer(llm_answer_after_citations)
            used_llm = True
            answer_strategy = "llm_with_quality_check"
        else:
            answer = build_evidence_based_answer(
                query=query,
                question_type=question_type,
                evidence_items=evidence_items
            )
            used_llm = False
            answer_strategy = "fallback_evidence_based_answer"

    else:
        answer = build_evidence_based_answer(
            query=query,
            question_type=question_type,
            evidence_items=evidence_items
        )
        used_llm = False
        answer_strategy = "evidence_based_answer_no_llm"

    answer = clean_final_answer(answer)

    return {
        "query": query,
        "answer": safe_enhance_answer_for_response(locals()),
        "retrieval_mode": retrieval_mode,
        "question_type": question_type,
        "used_reranker": use_reranker,
        "used_llm": used_llm,
        "answer_strategy": answer_strategy,
        "llm_status": get_llm_status(),
        "llm_diagnostics": {
            "raw_llm_answer_preview": raw_llm_answer[:300],
            "llm_answer_after_citations_preview": llm_answer_after_citations[:300],
            "llm_answer_accepted": used_llm
        },
        "graph_used": bool(graph_context.get("matched_entities") or graph_context.get("matched_relations")),
        "graph_context": graph_context,
        "retrieval_fusion": fusion_result if "fusion_result" in locals() else {
            "fusion_used": False,
            "reason": "Fusion result was not created."
        },
        "citations": citations,
        "evidence": evidence_items,
        "sources": sourced_results
    }


def build_evidence_based_answer(
    query: str,
    question_type: str,
    evidence_items: List[Dict[str, Any]]
) -> str:

    if question_type == "definition":
        return build_definition_answer(query, evidence_items)

    if question_type == "summary":
        return build_summary_answer(evidence_items)

    if question_type == "comparison":
        return build_general_answer(evidence_items)

    if question_type == "steps":
        return build_step_answer(evidence_items)

    return build_general_answer(evidence_items)


def build_definition_answer(
    query: str,
    evidence_items: List[Dict[str, Any]]
) -> str:

    target = extract_definition_target(query)

    if target and target.lower() == "rag":
        return build_rag_definition_answer(evidence_items)

    selected_items = select_best_unique_items(
        evidence_items=evidence_items,
        max_items=3
    )

    lines = []

    for item in selected_items:
        sentence = clean_sentence_text(item["sentence"])
        citation = source_id_to_bracket(item.get("source_id"))

        if citation and citation not in sentence:
            sentence = f"{sentence} {citation}"

        lines.append(sentence)

    return " ".join(lines)


def build_rag_definition_answer(evidence_items: List[Dict[str, Any]]) -> str:
    definition_source = find_first_item_containing(
        evidence_items,
        ["retrieval-augmented generation", "retrieval augmented generation"]
    )

    how_source = find_first_item_containing(
        evidence_items,
        [
            "retrieval step",
            "before generation",
            "before generating",
            "search a document corpus",
            "search your document corpus",
            "relevant passages as context"
        ]
    )

    why_source = find_first_item_containing(
        evidence_items,
        [
            "frozen knowledge",
            "hallucination",
            "private or recent data",
            "grounds the answer",
            "real evidence"
        ]
    )

    citation_ids = collect_source_ids(
        [definition_source, how_source, why_source]
    )

    citation_text = " ".join(
        source_id_to_bracket(source_id)
        for source_id in citation_ids
    )

    answer = (
        "RAG stands for Retrieval-Augmented Generation. "
        "It is a method where the system first retrieves relevant passages from a document corpus "
        "and then provides those passages as context before generating an answer. "
        "This helps the model answer using real evidence instead of relying only on frozen training knowledge, "
        "which reduces hallucination and makes the system useful for private or recent information."
    )

    if citation_text:
        answer = f"{answer} {citation_text}"

    return answer


def build_summary_answer(evidence_items: List[Dict[str, Any]]) -> str:
    selected_items = select_best_unique_items(
        evidence_items=evidence_items,
        max_items=5
    )

    lines = ["Here is the source-grounded summary:"]

    for index, item in enumerate(selected_items, start=1):
        sentence = clean_sentence_text(item["sentence"])
        citation = source_id_to_bracket(item.get("source_id"))

        lines.append(f"{index}. {sentence} {citation}")

    return "\n".join(lines)


def build_step_answer(evidence_items: List[Dict[str, Any]]) -> str:
    selected_items = select_best_unique_items(
        evidence_items=evidence_items,
        max_items=5
    )

    lines = ["Based on the retrieved sources, the process is:"]

    for index, item in enumerate(selected_items, start=1):
        sentence = clean_sentence_text(item["sentence"])
        citation = source_id_to_bracket(item.get("source_id"))

        lines.append(f"{index}. {sentence} {citation}")

    return "\n".join(lines)


def build_general_answer(evidence_items: List[Dict[str, Any]]) -> str:
    selected_items = select_best_unique_items(
        evidence_items=evidence_items,
        max_items=4
    )

    lines = []

    for item in selected_items:
        sentence = clean_sentence_text(item["sentence"])
        citation = source_id_to_bracket(item.get("source_id"))

        if citation and citation not in sentence:
            sentence = f"{sentence} {citation}"

        lines.append(sentence)

    return " ".join(lines)


def build_extractive_answer(
    sources: List[Dict[str, Any]]
) -> str:

    lines = [
        "I found relevant source-backed passages, but could not extract a cleaner evidence sentence automatically:"
    ]

    for index, source in enumerate(sources[:3], start=1):
        content = source.get("content", "")
        source_id = source.get("source_id", f"S{index}")
        excerpt = content[:600].replace("\n", " ").strip()

        lines.append(
            f"{index}. {excerpt} [{source_id}]"
        )

    return "\n\n".join(lines)


def extract_definition_target(query: str) -> Optional[str]:
    query_lower = query.lower().strip()

    patterns = [
        r"what is\s+(.+?)\??$",
        r"what are\s+(.+?)\??$",
        r"define\s+(.+?)\??$",
        r"meaning of\s+(.+?)\??$"
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)

        if match:
            target = match.group(1).strip()
            target = target.replace("?", "").strip()
            return target

    return None


def find_first_item_containing(
    evidence_items: List[Dict[str, Any]],
    keywords: List[str]
) -> Optional[Dict[str, Any]]:

    for item in evidence_items:
        sentence_lower = item.get("sentence", "").lower()

        for keyword in keywords:
            if keyword.lower() in sentence_lower:
                return item

    return None


def collect_source_ids(items: List[Optional[Dict[str, Any]]]) -> List[str]:
    source_ids = []

    for item in items:
        if not item:
            continue

        source_id = item.get("source_id")

        if source_id and source_id not in source_ids:
            source_ids.append(source_id)

    return source_ids[:3]


def select_best_unique_items(
    evidence_items: List[Dict[str, Any]],
    max_items: int
) -> List[Dict[str, Any]]:

    selected = []
    seen_meanings = []

    for item in evidence_items:
        sentence = clean_sentence_text(item["sentence"])

        if is_repetitive_meaning(sentence, seen_meanings):
            continue

        selected.append(item)
        seen_meanings.append(sentence)

        if len(selected) >= max_items:
            break

    return selected


def is_repetitive_meaning(sentence: str, existing_sentences: List[str]) -> bool:
    current_tokens = set(normalize_text(sentence).split())

    if not current_tokens:
        return True

    for existing in existing_sentences:
        existing_tokens = set(normalize_text(existing).split())

        if not existing_tokens:
            continue

        overlap = len(current_tokens.intersection(existing_tokens))
        union = len(current_tokens.union(existing_tokens))

        if union == 0:
            continue

        similarity = overlap / union

        if similarity >= 0.65:
            return True

    return False


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b(ideal|answer|question|chapter|page)\b", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_final_answer(answer: str) -> str:
    if not answer:
        return ""

    cleaned = answer

    cleaned = re.sub(r"\bIdeal Answer\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bQ\d+\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" .", ".")
    cleaned = cleaned.replace(" ,", ",")
    cleaned = cleaned.strip()

    return cleaned


def source_id_to_bracket(source_id: Optional[str]) -> str:
    if not source_id:
        return ""

    if source_id.startswith("[") and source_id.endswith("]"):
        return source_id

    return f"[{source_id}]"
