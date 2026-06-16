from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone


# =====================================================
# Retrieval evaluation schemas
# =====================================================

class RetrievalTestCaseCreate(BaseModel):
    question: str = Field(..., min_length=1)

    expected_document_id: Optional[str] = None
    expected_source_file_name: Optional[str] = None
    expected_page_numbers: List[int] = Field(default_factory=list)
    expected_chunk_ids: List[str] = Field(default_factory=list)

    search_document_id: Optional[str] = None

    top_k: int = Field(default=5, ge=1, le=50)
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class RetrievalTestCase(BaseModel):
    test_case_id: str
    question: str

    expected_document_id: Optional[str] = None
    expected_source_file_name: Optional[str] = None
    expected_page_numbers: List[int] = Field(default_factory=list)
    expected_chunk_ids: List[str] = Field(default_factory=list)

    search_document_id: Optional[str] = None

    top_k: int = 5
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RetrievalEvaluationRunRequest(BaseModel):
    test_case_ids: Optional[List[str]] = None
    top_k_override: Optional[int] = Field(default=None, ge=1, le=50)
    retrieval_mode_override: Optional[Literal["vector", "keyword", "hybrid"]] = None


class RetrievalSingleResult(BaseModel):
    test_case_id: str
    question: str

    passed: bool
    failure_reasons: List[str] = Field(default_factory=list)

    expected_document_id: Optional[str] = None
    expected_source_file_name: Optional[str] = None
    expected_page_numbers: List[int] = Field(default_factory=list)
    expected_chunk_ids: List[str] = Field(default_factory=list)

    top_k: int
    retrieval_mode: str

    retrieved_count: int

    expected_document_hit: Optional[bool] = None
    expected_source_file_hit: Optional[bool] = None
    expected_page_hit: Optional[bool] = None
    expected_chunk_hit: Optional[bool] = None

    best_match_rank: Optional[int] = None
    reciprocal_rank: float = 0.0

    top_result: Optional[Dict[str, Any]] = None
    retrieved_results_preview: List[Dict[str, Any]] = Field(default_factory=list)


class RetrievalEvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int

    pass_rate: float
    mean_reciprocal_rank: float

    document_hit_rate: Optional[float] = None
    source_file_hit_rate: Optional[float] = None
    page_hit_rate: Optional[float] = None
    chunk_hit_rate: Optional[float] = None


class RetrievalEvaluationReport(BaseModel):
    summary: RetrievalEvaluationSummary
    results: List[RetrievalSingleResult]


# =====================================================
# Answer evaluation schemas
# =====================================================

class AnswerTestCaseCreate(BaseModel):
    question: str = Field(..., min_length=1)

    document_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"
    use_reranker: bool = True
    use_llm: bool = True

    expected_answer_keywords: List[str] = Field(default_factory=list)
    forbidden_answer_keywords: List[str] = Field(default_factory=list)

    require_citations: bool = True
    require_sources: bool = True

    minimum_answer_words: int = Field(default=20, ge=1)
    minimum_keyword_match_ratio: float = Field(default=0.5, ge=0.0, le=1.0)
    minimum_groundedness_score: float = Field(default=0.12, ge=0.0, le=1.0)

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AnswerTestCase(BaseModel):
    test_case_id: str
    question: str

    document_id: Optional[str] = None
    top_k: int = 5
    retrieval_mode: Literal["vector", "keyword", "hybrid"] = "hybrid"
    use_reranker: bool = True
    use_llm: bool = True

    expected_answer_keywords: List[str] = Field(default_factory=list)
    forbidden_answer_keywords: List[str] = Field(default_factory=list)

    require_citations: bool = True
    require_sources: bool = True

    minimum_answer_words: int = 20
    minimum_keyword_match_ratio: float = 0.5
    minimum_groundedness_score: float = 0.12

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AnswerEvaluationRunRequest(BaseModel):
    test_case_ids: Optional[List[str]] = None
    use_llm_override: Optional[bool] = None
    retrieval_mode_override: Optional[Literal["vector", "keyword", "hybrid"]] = None


class AnswerSingleResult(BaseModel):
    test_case_id: str
    question: str

    passed: bool
    failure_reasons: List[str] = Field(default_factory=list)

    answer: str
    answer_strategy: Optional[str] = None
    used_llm: bool
    used_reranker: bool
    retrieval_mode: str

    answer_word_count: int
    citation_present: bool
    source_count: int

    keyword_match_ratio: Optional[float] = None
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    forbidden_keywords_found: List[str] = Field(default_factory=list)

    groundedness_score: float = 0.0
    groundedness_passed: bool = False

    citations_preview: List[Dict[str, Any]] = Field(default_factory=list)
    sources_preview: List[Dict[str, Any]] = Field(default_factory=list)


class AnswerEvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int

    pass_rate: float

    citation_pass_rate: Optional[float] = None
    source_presence_rate: Optional[float] = None
    keyword_pass_rate: Optional[float] = None
    groundedness_pass_rate: Optional[float] = None

    average_groundedness_score: float = 0.0
    average_answer_word_count: float = 0.0


class AnswerEvaluationReport(BaseModel):
    summary: AnswerEvaluationSummary
    results: List[AnswerSingleResult]
