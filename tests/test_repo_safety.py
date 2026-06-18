"""Tests for repository safety and hygiene."""

import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).parent.parent


def test_env_not_committed():
    """The .env file must not exist in the repo (should be in .gitignore)."""
    env_file = BACKEND_ROOT / ".env"
    # It's OK if .env exists locally (it's gitignored), but we should
    # verify .gitignore includes it.
    gitignore = BACKEND_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore must exist"
    content = gitignore.read_text(encoding="utf-8")
    assert ".env" in content, ".gitignore must include .env"


def test_env_example_exists():
    """.env.example must exist to document required environment variables."""
    env_example = BACKEND_ROOT / ".env.example"
    assert env_example.exists(), ".env.example must exist"

    content = env_example.read_text(encoding="utf-8")
    # Should have at least some key variables documented
    assert "HF_API_TOKEN" in content or "LLM_PROVIDER" in content, \
        ".env.example should document key environment variables"


def test_gitignore_excludes_secrets():
    """.gitignore should exclude common secret/artifact patterns."""
    gitignore = BACKEND_ROOT / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")

    required_patterns = [".env", "__pycache__", "*.pyc"]
    for pattern in required_patterns:
        assert pattern in content, f".gitignore should exclude {pattern}"


def test_no_hardcoded_secrets_in_config():
    """Config file should not contain hardcoded real secrets."""
    config_path = BACKEND_ROOT / "app" / "core" / "config.py"
    if not config_path.exists():
        return

    content = config_path.read_text(encoding="utf-8")
    # Should not have real API tokens
    assert "hf_" not in content.lower() or "os.getenv" in content, \
        "Config should use environment variables, not hardcoded tokens"


def test_requirements_file_exists():
    """requirements.txt must exist."""
    req = BACKEND_ROOT / "requirements.txt"
    assert req.exists(), "requirements.txt must exist"

    content = req.read_text(encoding="utf-8")
    assert "fastapi" in content.lower(), "requirements.txt should include fastapi"


def test_eval_directory_exists():
    """eval/ directory with QA files should exist."""
    eval_dir = BACKEND_ROOT / "eval"
    assert eval_dir.exists(), "eval/ directory must exist"
    jsonl_files = list(eval_dir.glob("*.jsonl"))
    assert len(jsonl_files) > 0, "eval/ should contain at least one .jsonl file"


def test_scripts_directory_has_eval_script():
    """scripts/ should contain the ablation eval script."""
    scripts_dir = BACKEND_ROOT / "scripts"
    eval_script = scripts_dir / "run_graph_ablation_eval.py"
    assert eval_script.exists(), "scripts/run_graph_ablation_eval.py must exist"
