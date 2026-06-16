import json
import uuid
from typing import List, Optional

from app.core.config import settings
from app.schemas.evaluation_schema import (
    AnswerTestCase,
    AnswerTestCaseCreate
)


ANSWER_TEST_CASES_PATH = settings.EVALUATION_DIR / "answer_test_cases.json"


def load_answer_test_cases() -> List[AnswerTestCase]:
    settings.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    if not ANSWER_TEST_CASES_PATH.exists():
        return []

    with open(ANSWER_TEST_CASES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [AnswerTestCase(**item) for item in data]


def save_answer_test_cases(test_cases: List[AnswerTestCase]) -> None:
    settings.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    with open(ANSWER_TEST_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            [test_case.model_dump() for test_case in test_cases],
            f,
            indent=2,
            ensure_ascii=False
        )


def add_answer_test_case(
    test_case_create: AnswerTestCaseCreate
) -> AnswerTestCase:

    test_cases = load_answer_test_cases()

    new_test_case = AnswerTestCase(
        test_case_id=str(uuid.uuid4()),
        question=test_case_create.question,
        document_id=test_case_create.document_id,
        top_k=test_case_create.top_k,
        retrieval_mode=test_case_create.retrieval_mode,
        use_reranker=test_case_create.use_reranker,
        use_llm=test_case_create.use_llm,
        expected_answer_keywords=test_case_create.expected_answer_keywords,
        forbidden_answer_keywords=test_case_create.forbidden_answer_keywords,
        require_citations=test_case_create.require_citations,
        require_sources=test_case_create.require_sources,
        minimum_answer_words=test_case_create.minimum_answer_words,
        minimum_keyword_match_ratio=test_case_create.minimum_keyword_match_ratio,
        minimum_groundedness_score=test_case_create.minimum_groundedness_score,
        notes=test_case_create.notes,
        tags=test_case_create.tags
    )

    test_cases.append(new_test_case)
    save_answer_test_cases(test_cases)

    return new_test_case


def delete_answer_test_case(test_case_id: str) -> bool:
    test_cases = load_answer_test_cases()

    remaining_cases = [
        test_case for test_case in test_cases
        if test_case.test_case_id != test_case_id
    ]

    if len(remaining_cases) == len(test_cases):
        return False

    save_answer_test_cases(remaining_cases)
    return True


def get_answer_test_case(test_case_id: str) -> Optional[AnswerTestCase]:
    test_cases = load_answer_test_cases()

    for test_case in test_cases:
        if test_case.test_case_id == test_case_id:
            return test_case

    return None
