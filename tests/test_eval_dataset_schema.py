"""Tests for QA evaluation dataset schema validity."""

import json
import os
import pytest
from pathlib import Path

EVAL_DIR = Path(__file__).parent.parent / "eval"
REQUIRED_FIELDS = {"id", "question", "gold_answer", "relevant_chunk_ids", "expected_terms", "difficulty"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def iter_jsonl(path: Path):
    """Yield parsed rows from a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            yield line_no, json.loads(line)


def get_eval_files():
    """Find all .jsonl files in eval/ directory."""
    if not EVAL_DIR.exists():
        return []
    return list(EVAL_DIR.glob("*.jsonl"))


@pytest.fixture(params=get_eval_files(), ids=lambda p: p.name)
def eval_file(request):
    return request.param


def test_eval_files_exist():
    """At least one eval JSONL file should exist."""
    files = get_eval_files()
    assert len(files) > 0, "No eval JSONL files found in eval/ directory"


def test_eval_file_has_required_fields(eval_file):
    """Every row in every eval file must have all required fields."""
    for line_no, row in iter_jsonl(eval_file):
        missing = REQUIRED_FIELDS - set(row.keys())
        assert not missing, f"{eval_file.name}:{line_no} missing fields: {missing}"


def test_eval_file_has_valid_types(eval_file):
    """Field types must be correct."""
    for line_no, row in iter_jsonl(eval_file):
        assert isinstance(row["id"], str), f"{eval_file.name}:{line_no} id must be string"
        assert isinstance(row["question"], str), f"{eval_file.name}:{line_no} question must be string"
        assert isinstance(row["gold_answer"], str), f"{eval_file.name}:{line_no} gold_answer must be string"
        assert isinstance(row["relevant_chunk_ids"], list), f"{eval_file.name}:{line_no} relevant_chunk_ids must be list"
        assert isinstance(row["expected_terms"], list), f"{eval_file.name}:{line_no} expected_terms must be list"
        assert isinstance(row["difficulty"], str), f"{eval_file.name}:{line_no} difficulty must be string"


def test_eval_file_has_valid_difficulty(eval_file):
    """Difficulty must be easy, medium, or hard."""
    for line_no, row in iter_jsonl(eval_file):
        assert row["difficulty"] in VALID_DIFFICULTIES, (
            f"{eval_file.name}:{line_no} invalid difficulty: {row['difficulty']}"
        )


def test_eval_file_has_unique_ids(eval_file):
    """All question IDs within a file must be unique."""
    ids = []
    for _, row in iter_jsonl(eval_file):
        ids.append(row["id"])
    assert len(ids) == len(set(ids)), f"{eval_file.name} has duplicate IDs"


def test_eval_file_questions_not_empty(eval_file):
    """Questions must not be empty."""
    for line_no, row in iter_jsonl(eval_file):
        assert len(row["question"].strip()) > 5, (
            f"{eval_file.name}:{line_no} question too short: {row['question']}"
        )


def test_starter_file_has_15_questions():
    """The 15-question starter file must have exactly 15 rows."""
    starter = EVAL_DIR / "qa_15_starter.jsonl"
    if not starter.exists():
        pytest.skip("qa_15_starter.jsonl not found")
    rows = list(iter_jsonl(starter))
    assert len(rows) == 15, f"Expected 15 questions, got {len(rows)}"


def test_full_file_has_50_questions():
    """The 50-question file must have exactly 50 rows."""
    full = EVAL_DIR / "qa_50_graphresearcher.jsonl"
    if not full.exists():
        pytest.skip("qa_50_graphresearcher.jsonl not found")
    rows = list(iter_jsonl(full))
    assert len(rows) == 50, f"Expected 50 questions, got {len(rows)}"
