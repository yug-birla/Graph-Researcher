import json
import uuid
from typing import List, Optional

from app.core.config import settings
from app.schemas.evaluation_schema import (
    RetrievalTestCase,
    RetrievalTestCaseCreate
)


TEST_CASES_PATH = settings.EVALUATION_DIR / "retrieval_test_cases.json"


def load_retrieval_test_cases() -> List[RetrievalTestCase]:
    settings.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    if not TEST_CASES_PATH.exists():
        return []

    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [RetrievalTestCase(**item) for item in data]


def save_retrieval_test_cases(test_cases: List[RetrievalTestCase]) -> None:
    settings.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    with open(TEST_CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            [test_case.model_dump() for test_case in test_cases],
            f,
            indent=2,
            ensure_ascii=False
        )


def add_retrieval_test_case(
    test_case_create: RetrievalTestCaseCreate
) -> RetrievalTestCase:

    test_cases = load_retrieval_test_cases()

    new_test_case = RetrievalTestCase(
        test_case_id=str(uuid.uuid4()),
        question=test_case_create.question,
        expected_document_id=test_case_create.expected_document_id,
        expected_source_file_name=test_case_create.expected_source_file_name,
        expected_page_numbers=test_case_create.expected_page_numbers,
        expected_chunk_ids=test_case_create.expected_chunk_ids,
        search_document_id=test_case_create.search_document_id,
        top_k=test_case_create.top_k,
        retrieval_mode=test_case_create.retrieval_mode,
        notes=test_case_create.notes,
        tags=test_case_create.tags
    )

    test_cases.append(new_test_case)
    save_retrieval_test_cases(test_cases)

    return new_test_case


def delete_retrieval_test_case(test_case_id: str) -> bool:
    test_cases = load_retrieval_test_cases()

    remaining_cases = [
        test_case for test_case in test_cases
        if test_case.test_case_id != test_case_id
    ]

    if len(remaining_cases) == len(test_cases):
        return False

    save_retrieval_test_cases(remaining_cases)
    return True


def get_retrieval_test_case(test_case_id: str) -> Optional[RetrievalTestCase]:
    test_cases = load_retrieval_test_cases()

    for test_case in test_cases:
        if test_case.test_case_id == test_case_id:
            return test_case

    return None
