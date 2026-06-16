from typing import List, Optional, Dict, Any

from app.schemas.evaluation_schema import (
    RetrievalTestCase,
    RetrievalEvaluationRunRequest,
    RetrievalSingleResult,
    RetrievalEvaluationSummary,
    RetrievalEvaluationReport
)
from app.evaluation.retrieval_eval_storage import load_retrieval_test_cases
from app.retrieval.hybrid_search_service import retrieve_chunks


def run_retrieval_evaluation(
    request: RetrievalEvaluationRunRequest
) -> RetrievalEvaluationReport:

    all_test_cases = load_retrieval_test_cases()

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
        result = evaluate_single_test_case(
            test_case=test_case,
            top_k_override=request.top_k_override,
            retrieval_mode_override=request.retrieval_mode_override
        )
        results.append(result)

    summary = build_evaluation_summary(results)

    return RetrievalEvaluationReport(
        summary=summary,
        results=results
    )


def evaluate_single_test_case(
    test_case: RetrievalTestCase,
    top_k_override: Optional[int] = None,
    retrieval_mode_override: Optional[str] = None
) -> RetrievalSingleResult:

    top_k = top_k_override or test_case.top_k
    retrieval_mode = retrieval_mode_override or test_case.retrieval_mode

    retrieval_output = retrieve_chunks(
        query=test_case.question,
        document_id=test_case.search_document_id,
        top_k=top_k,
        retrieval_mode=retrieval_mode
    )

    retrieved_results = retrieval_output.get("results", [])

    expected_document_hit = evaluate_expected_document_hit(
        retrieved_results,
        test_case.expected_document_id
    )

    expected_source_file_hit = evaluate_expected_source_file_hit(
        retrieved_results,
        test_case.expected_source_file_name
    )

    expected_page_hit = evaluate_expected_page_hit(
        retrieved_results,
        test_case.expected_page_numbers
    )

    expected_chunk_hit = evaluate_expected_chunk_hit(
        retrieved_results,
        test_case.expected_chunk_ids
    )

    best_match_rank = find_best_match_rank(
        retrieved_results=retrieved_results,
        test_case=test_case
    )

    reciprocal_rank = 0.0

    if best_match_rank is not None and best_match_rank > 0:
        reciprocal_rank = 1.0 / best_match_rank

    failure_reasons = build_failure_reasons(
        expected_document_hit=expected_document_hit,
        expected_source_file_hit=expected_source_file_hit,
        expected_page_hit=expected_page_hit,
        expected_chunk_hit=expected_chunk_hit
    )

    passed = len(failure_reasons) == 0

    top_result = None

    if retrieved_results:
        top_result = simplify_result(retrieved_results[0], rank=1)

    retrieved_results_preview = [
        simplify_result(result, rank=index + 1)
        for index, result in enumerate(retrieved_results[:10])
    ]

    return RetrievalSingleResult(
        test_case_id=test_case.test_case_id,
        question=test_case.question,
        passed=passed,
        failure_reasons=failure_reasons,
        expected_document_id=test_case.expected_document_id,
        expected_source_file_name=test_case.expected_source_file_name,
        expected_page_numbers=test_case.expected_page_numbers,
        expected_chunk_ids=test_case.expected_chunk_ids,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        retrieved_count=len(retrieved_results),
        expected_document_hit=expected_document_hit,
        expected_source_file_hit=expected_source_file_hit,
        expected_page_hit=expected_page_hit,
        expected_chunk_hit=expected_chunk_hit,
        best_match_rank=best_match_rank,
        reciprocal_rank=reciprocal_rank,
        top_result=top_result,
        retrieved_results_preview=retrieved_results_preview
    )


def evaluate_expected_document_hit(
    results: List[Dict[str, Any]],
    expected_document_id: Optional[str]
) -> Optional[bool]:

    if not expected_document_id:
        return None

    return any(
        result.get("document_id") == expected_document_id
        for result in results
    )


def evaluate_expected_source_file_hit(
    results: List[Dict[str, Any]],
    expected_source_file_name: Optional[str]
) -> Optional[bool]:

    if not expected_source_file_name:
        return None

    return any(
        result.get("source_file_name") == expected_source_file_name
        for result in results
    )


def evaluate_expected_page_hit(
    results: List[Dict[str, Any]],
    expected_page_numbers: List[int]
) -> Optional[bool]:

    if not expected_page_numbers:
        return None

    expected_pages = set(expected_page_numbers)

    return any(
        result.get("page_number") in expected_pages
        for result in results
    )


def evaluate_expected_chunk_hit(
    results: List[Dict[str, Any]],
    expected_chunk_ids: List[str]
) -> Optional[bool]:

    if not expected_chunk_ids:
        return None

    expected_chunks = set(expected_chunk_ids)

    return any(
        result.get("chunk_id") in expected_chunks
        for result in results
    )


def find_best_match_rank(
    retrieved_results: List[Dict[str, Any]],
    test_case: RetrievalTestCase
) -> Optional[int]:

    for index, result in enumerate(retrieved_results, start=1):
        if result_matches_any_expectation(result, test_case):
            return index

    return None


def result_matches_any_expectation(
    result: Dict[str, Any],
    test_case: RetrievalTestCase
) -> bool:

    if (
        test_case.expected_chunk_ids
        and result.get("chunk_id") in set(test_case.expected_chunk_ids)
    ):
        return True

    if (
        test_case.expected_page_numbers
        and result.get("page_number") in set(test_case.expected_page_numbers)
    ):
        return True

    if (
        test_case.expected_document_id
        and result.get("document_id") == test_case.expected_document_id
    ):
        return True

    if (
        test_case.expected_source_file_name
        and result.get("source_file_name") == test_case.expected_source_file_name
    ):
        return True

    return False


def build_failure_reasons(
    expected_document_hit: Optional[bool],
    expected_source_file_hit: Optional[bool],
    expected_page_hit: Optional[bool],
    expected_chunk_hit: Optional[bool]
) -> List[str]:

    failure_reasons = []

    if expected_document_hit is False:
        failure_reasons.append("Expected document was not retrieved.")

    if expected_source_file_hit is False:
        failure_reasons.append("Expected source file was not retrieved.")

    if expected_page_hit is False:
        failure_reasons.append("Expected page was not retrieved.")

    if expected_chunk_hit is False:
        failure_reasons.append("Expected chunk was not retrieved.")

    return failure_reasons


def simplify_result(result: Dict[str, Any], rank: int) -> Dict[str, Any]:
    content = result.get("content", "")

    return {
        "rank": rank,
        "score": result.get("score"),
        "chunk_id": result.get("chunk_id"),
        "document_id": result.get("document_id"),
        "source_file_name": result.get("source_file_name"),
        "page_number": result.get("page_number"),
        "content_type": result.get("content_type"),
        "content_preview": content[:300]
    }


def build_evaluation_summary(
    results: List[RetrievalSingleResult]
) -> RetrievalEvaluationSummary:

    total_cases = len(results)

    if total_cases == 0:
        return RetrievalEvaluationSummary(
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            pass_rate=0.0,
            mean_reciprocal_rank=0.0
        )

    passed_cases = sum(1 for result in results if result.passed)
    failed_cases = total_cases - passed_cases

    pass_rate = round(passed_cases / total_cases, 4)

    mean_reciprocal_rank = round(
        sum(result.reciprocal_rank for result in results) / total_cases,
        4
    )

    document_hit_rate = compute_optional_rate(
        [result.expected_document_hit for result in results]
    )

    source_file_hit_rate = compute_optional_rate(
        [result.expected_source_file_hit for result in results]
    )

    page_hit_rate = compute_optional_rate(
        [result.expected_page_hit for result in results]
    )

    chunk_hit_rate = compute_optional_rate(
        [result.expected_chunk_hit for result in results]
    )

    return RetrievalEvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        mean_reciprocal_rank=mean_reciprocal_rank,
        document_hit_rate=document_hit_rate,
        source_file_hit_rate=source_file_hit_rate,
        page_hit_rate=page_hit_rate,
        chunk_hit_rate=chunk_hit_rate
    )


def compute_optional_rate(values: List[Optional[bool]]) -> Optional[float]:
    actual_values = [
        value for value in values
        if value is not None
    ]

    if not actual_values:
        return None

    true_count = sum(1 for value in actual_values if value is True)

    return round(true_count / len(actual_values), 4)
