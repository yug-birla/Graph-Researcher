"""Tests for evaluation metric functions."""

import sys
import os

# Allow importing from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_recall_at_k_perfect():
    from run_graph_ablation_eval import recall_at_k
    retrieved = ["c1", "c2", "c3", "c4", "c5"]
    gold = ["c1", "c2"]
    assert recall_at_k(retrieved, gold, 3) == 1.0
    assert recall_at_k(retrieved, gold, 5) == 1.0


def test_recall_at_k_partial():
    from run_graph_ablation_eval import recall_at_k
    retrieved = ["c1", "c2", "c3", "c4", "c5"]
    gold = ["c1", "c5", "c99"]
    assert recall_at_k(retrieved, gold, 3) == 1 / 3  # only c1 in top 3
    assert recall_at_k(retrieved, gold, 5) == 2 / 3  # c1 and c5 in top 5


def test_recall_at_k_miss():
    from run_graph_ablation_eval import recall_at_k
    retrieved = ["c10", "c20", "c30"]
    gold = ["c1", "c2"]
    assert recall_at_k(retrieved, gold, 3) == 0.0


def test_recall_at_k_empty_gold():
    from run_graph_ablation_eval import recall_at_k
    assert recall_at_k(["c1", "c2"], [], 3) == 0.0


def test_recall_at_k_empty_retrieved():
    from run_graph_ablation_eval import recall_at_k
    assert recall_at_k([], ["c1", "c2"], 3) == 0.0


def test_answer_completeness_full():
    from run_graph_ablation_eval import answer_completeness
    answer = "Retrieval-Augmented Generation combines retrieval with generation."
    terms = ["retrieval", "generation"]
    assert answer_completeness(answer, terms) == 1.0


def test_answer_completeness_partial():
    from run_graph_ablation_eval import answer_completeness
    answer = "This is about retrieval systems."
    terms = ["retrieval", "generation", "embedding"]
    assert abs(answer_completeness(answer, terms) - 1 / 3) < 0.01


def test_answer_completeness_empty():
    from run_graph_ablation_eval import answer_completeness
    assert answer_completeness("some answer", []) == 0.0
    assert answer_completeness("", ["term"]) == 0.0


def test_faithfulness_heuristic_supported():
    from run_graph_ablation_eval import answer_faithfulness_heuristic
    answer = "RAG uses retrieval to find relevant documents before generating answers."
    sources = ["RAG retrieval finds relevant documents and generates contextual answers."]
    score = answer_faithfulness_heuristic(answer, sources)
    assert score > 0.5  # should have high overlap


def test_faithfulness_heuristic_unsupported():
    from run_graph_ablation_eval import answer_faithfulness_heuristic
    answer = "Quantum computing enables superposition of qubits for parallel processing."
    sources = ["RAG retrieval finds relevant documents."]
    score = answer_faithfulness_heuristic(answer, sources)
    assert score < 0.5  # low overlap with unrelated sources


def test_faithfulness_heuristic_empty():
    from run_graph_ablation_eval import answer_faithfulness_heuristic
    assert answer_faithfulness_heuristic("", ["source"]) == 0.0
    assert answer_faithfulness_heuristic("answer", []) == 0.0
