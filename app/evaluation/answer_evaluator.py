import re
from typing import List, Optional, Dict, Any

from app.schemas.evaluation_schema import (
    AnswerTestCase,
    AnswerEvaluationRunRequest,
    AnswerSingleResult,
    AnswerEvaluationSummary,
    AnswerEvaluationReport
)
from app.evaluation.answer_eval_storage import load_answer_test_cases
from app.generation.answer_service import answer_question


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "by", "for",
    "with", "from", "is", "are", "was", "were", "be", "been", "it",
    "this", "that", "as", "at", "which", "what", "how", "why"
}


def run_answer_evaluation(
    request: AnswerEvaluationRunRequest
) -> AnswerEvaluationReport:

    all_test_cases = load_answer_test_cases()

    if request.test_case_ids:
        selected_ids = set(request.test_case_ids)
        test_cases = [
            test_case for test_case in all_test_cases
            if test_case.test_case_id in selected_ids
        ]
    else:
        test_cases = all_test_cases

    results = []

    for test_case in test_cases:
        result = evaluate_single_answer_test_case(
            test_case=test_case,
            use_llm_override=request.use_llm_override,
            retrieval_mode_override=request.retrieval_mode_override
        )
        results.append(result)

    summary = build_answer_evaluation_summary(results)

    return AnswerEvaluationReport(
        summary=summary,
        results=results
    )


def evaluate_single_answer_test_case(
    test_case: AnswerTestCase,
    use_llm_override: Optional[bool] = None,
    retrieval_mode_override: Optional[str] = None
) -> AnswerSingleResult:

    use_llm = (
        use_llm_override
        if use_llm_override is not None
        else test_case.use_llm
    )

    retrieval_mode = retrieval_mode_override or test_case.retrieval_mode

    answer_output = answer_question(
        query=test_case.question,
        document_id=test_case.document_id,
        top_k=test_case.top_k,
        retrieval_mode=retrieval_mode,
        use_reranker=test_case.use_reranker,
        use_llm=use_llm
    )

    answer = answer_output.get("answer", "")
    citations = answer_output.get("citations", [])
    sources = answer_output.get("sources", [])

    answer_word_count = count_words(answer)
    citation_present = has_citation(answer)
    source_count = len(sources)

    matched_keywords, missing_keywords, keyword_match_ratio = evaluate_keywords(
        answer=answer,
        expected_keywords=test_case.expected_answer_keywords
    )

    forbidden_keywords_found = find_forbidden_keywords(
        answer=answer,
        forbidden_keywords=test_case.forbidden_answer_keywords
    )

    groundedness_score = compute_groundedness_score(
        answer=answer,
        sources=sources
    )

    groundedness_passed = (
        groundedness_score >= test_case.minimum_groundedness_score
    )

    failure_reasons = []

    if answer_word_count < test_case.minimum_answer_words:
        failure_reasons.append(
            f"Answer is too short. Expected at least {test_case.minimum_answer_words} words."
        )

    if test_case.require_citations and not citation_present:
        failure_reasons.append("Answer does not contain required citations.")

    if test_case.require_sources and source_count == 0:
        failure_reasons.append("Answer does not include any retrieved sources.")

    if test_case.expected_answer_keywords:
        if keyword_match_ratio < test_case.minimum_keyword_match_ratio:
            failure_reasons.append(
                "Answer did not match enough expected keywords."
            )

    if forbidden_keywords_found:
        failure_reasons.append(
            "Answer contains forbidden keywords."
        )

    if not groundedness_passed:
        failure_reasons.append(
            "Answer does not appear grounded enough in retrieved sources."
        )

    passed = len(failure_reasons) == 0

    return AnswerSingleResult(
        test_case_id=test_case.test_case_id,
        question=test_case.question,
        passed=passed,
        failure_reasons=failure_reasons,
        answer=answer,
        answer_strategy=answer_output.get("answer_strategy"),
        used_llm=answer_output.get("used_llm", False),
        used_reranker=answer_output.get("used_reranker", False),
        retrieval_mode=answer_output.get("retrieval_mode", retrieval_mode),
        answer_word_count=answer_word_count,
        citation_present=citation_present,
        source_count=source_count,
        keyword_match_ratio=keyword_match_ratio,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        forbidden_keywords_found=forbidden_keywords_found,
        groundedness_score=groundedness_score,
        groundedness_passed=groundedness_passed,
        citations_preview=simplify_citations(citations),
        sources_preview=simplify_sources(sources)
    )


def count_words(text: str) -> int:
    return len(re.findall(r"[a-zA-Z0-9_]+", text or ""))


def has_citation(text: str) -> bool:
    if not text:
        return False

    return bool(re.search(r"\[S\d+\]", text))


def evaluate_keywords(
    answer: str,
    expected_keywords: List[str]
):
    if not expected_keywords:
        return [], [], None

    answer_lower = answer.lower()

    matched_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        keyword_lower = keyword.lower().strip()

        if keyword_lower in answer_lower:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    keyword_match_ratio = round(
        len(matched_keywords) / len(expected_keywords),
        4
    )

    return matched_keywords, missing_keywords, keyword_match_ratio


def find_forbidden_keywords(
    answer: str,
    forbidden_keywords: List[str]
) -> List[str]:

    if not forbidden_keywords:
        return []

    answer_lower = answer.lower()
    found = []

    for keyword in forbidden_keywords:
        keyword_lower = keyword.lower().strip()

        if keyword_lower in answer_lower:
            found.append(keyword)

    return found


def tokenize_for_groundedness(text: str) -> set:
    words = re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())

    tokens = {
        word for word in words
        if word not in STOPWORDS and len(word) > 2
    }

    return tokens


def compute_groundedness_score(
    answer: str,
    sources: List[Dict[str, Any]]
) -> float:

    answer_tokens = tokenize_for_groundedness(answer)

    if not answer_tokens:
        return 0.0

    source_text = " ".join(
        source.get("content", "")
        for source in sources
    )

    source_tokens = tokenize_for_groundedness(source_text)

    if not source_tokens:
        return 0.0

    overlap = answer_tokens.intersection(source_tokens)

    score = len(overlap) / len(answer_tokens)

    return round(score, 4)


def simplify_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    simplified = []

    for citation in citations[:5]:
        simplified.append(
            {
                "source_id": citation.get("source_id"),
                "source_file_name": citation.get("source_file_name"),
                "page_number": citation.get("page_number"),
                "citation_text": citation.get("citation_text")
            }
        )

    return simplified


def simplify_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    simplified = []

    for source in sources[:5]:
        content = source.get("content", "")

        simplified.append(
            {
                "source_id": source.get("source_id"),
                "score": source.get("score"),
                "chunk_id": source.get("chunk_id"),
                "source_file_name": source.get("source_file_name"),
                "page_number": source.get("page_number"),
                "content_preview": content[:250]
            }
        )

    return simplified


def build_answer_evaluation_summary(
    results: List[AnswerSingleResult]
) -> AnswerEvaluationSummary:

    total_cases = len(results)

    if total_cases == 0:
        return AnswerEvaluationSummary(
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            pass_rate=0.0,
            average_groundedness_score=0.0,
            average_answer_word_count=0.0
        )

    passed_cases = sum(1 for result in results if result.passed)
    failed_cases = total_cases - passed_cases

    pass_rate = round(passed_cases / total_cases, 4)

    citation_pass_rate = round(
        sum(1 for result in results if result.citation_present) / total_cases,
        4
    )

    source_presence_rate = round(
        sum(1 for result in results if result.source_count > 0) / total_cases,
        4
    )

    keyword_results = [
        result for result in results
        if result.keyword_match_ratio is not None
    ]

    keyword_pass_rate = None

    if keyword_results:
        keyword_pass_rate = round(
            sum(
                1 for result in keyword_results
                if result.keyword_match_ratio is not None
                and result.keyword_match_ratio >= 0.5
            ) / len(keyword_results),
            4
        )

    groundedness_pass_rate = round(
        sum(1 for result in results if result.groundedness_passed) / total_cases,
        4
    )

    average_groundedness_score = round(
        sum(result.groundedness_score for result in results) / total_cases,
        4
    )

    average_answer_word_count = round(
        sum(result.answer_word_count for result in results) / total_cases,
        2
    )

    return AnswerEvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        citation_pass_rate=citation_pass_rate,
        source_presence_rate=source_presence_rate,
        keyword_pass_rate=keyword_pass_rate,
        groundedness_pass_rate=groundedness_pass_rate,
        average_groundedness_score=average_groundedness_score,
        average_answer_word_count=average_answer_word_count
    )
