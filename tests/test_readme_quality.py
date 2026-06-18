"""Tests for README quality and required content."""

from pathlib import Path

README = Path(__file__).parent.parent / "README.md"


def read_readme() -> str:
    assert README.exists(), "README.md not found"
    return README.read_text(encoding="utf-8")


def test_readme_exists():
    assert README.exists()


def test_readme_has_eval_markers():
    """README must contain eval results placeholder markers."""
    content = read_readme()
    assert "EVAL_RESULTS_START" in content, "Missing <!-- EVAL_RESULTS_START --> marker"
    assert "EVAL_RESULTS_END" in content, "Missing <!-- EVAL_RESULTS_END --> marker"


def test_readme_mentions_ablation():
    """README must mention RAG vs RAG + Graph comparison."""
    content = read_readme().lower()
    assert "rag" in content
    assert "graph" in content
    # Should mention ablation or comparison
    assert any(term in content for term in ["ablation", "rag + graph", "rag+graph", "rag only", "graph-guided"]), \
        "README should mention RAG vs Graph ablation/comparison"


def test_readme_has_limitations():
    """README must have an honest limitations section."""
    content = read_readme().lower()
    assert "limitation" in content, "README should have a limitations section"


def test_readme_no_fake_metrics():
    """README should not contain suspicious hardcoded metric claims."""
    content = read_readme()
    # Check for suspicious patterns like "95% accuracy" or "Recall@5: 0.92"
    import re
    suspicious = re.findall(r'(?:accuracy|recall|precision|f1)[:\s]+(?:0\.\d{2,}|\d{2,}%)', content, re.IGNORECASE)
    # Filter out legitimate eval table placeholders
    for match in suspicious:
        assert "actual" in match.lower() or "pending" in match.lower() or "n/a" in match.lower(), \
            f"Suspicious hardcoded metric found: {match}. Metrics should come from real evaluation runs."


def test_readme_has_project_title():
    """README should have a project title."""
    content = read_readme()
    assert "GraphResearcher" in content


def test_readme_has_setup_section():
    """README should have setup instructions."""
    content = read_readme().lower()
    assert any(term in content for term in ["setup", "install", "pip install", "requirements"]), \
        "README should have setup/installation instructions"


def test_readme_not_too_long():
    """README should be reasonable length (not bloated)."""
    content = read_readme()
    lines = content.strip().split("\n")
    assert len(lines) < 400, f"README is {len(lines)} lines — should be concise and professional"
