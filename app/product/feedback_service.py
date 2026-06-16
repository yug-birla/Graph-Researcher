
import os
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import Request
from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_feedback_dir() -> Path:
    raw = os.getenv("FEEDBACK_STORAGE_DIR", "").strip()

    if raw:
        path = Path(raw)
    else:
        path = Path("/tmp/graphrag/feedback")

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_feedback_db_path() -> Path:
    raw = os.getenv("FEEDBACK_DB_PATH", "").strip()

    if raw:
        path = Path(raw)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    return get_feedback_dir() / "feedback.db"


def get_feedback_jsonl_path() -> Path:
    return get_feedback_dir() / "feedback.jsonl"


class FeedbackRequest(BaseModel):
    feedback_type: str = Field(default="general")
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    message: str = Field(..., min_length=2, max_length=5000)

    page_url: Optional[str] = None
    document_id: Optional[str] = None
    question: Optional[str] = None
    answer_preview: Optional[str] = None
    email: Optional[str] = None


def init_feedback_db() -> None:
    db_path = get_feedback_db_path()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        feedback_type TEXT,
        rating INTEGER,
        message TEXT NOT NULL,
        page_url TEXT,
        document_id TEXT,
        question TEXT,
        answer_preview TEXT,
        email TEXT,
        user_agent TEXT,
        client_host TEXT,
        saved_to_hf_dataset INTEGER DEFAULT 0,
        hf_dataset_error TEXT
    )
    """)

    conn.commit()
    conn.close()


def safe_trim(value: Optional[str], limit: int) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip()

    if len(value) > limit:
        return value[:limit]

    return value


def feedback_to_record(payload: FeedbackRequest, request: Request) -> Dict[str, Any]:
    client_host = None

    try:
        client_host = request.client.host if request.client else None
    except Exception:
        client_host = None

    return {
        "feedback_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "feedback_type": safe_trim(payload.feedback_type, 80) or "general",
        "rating": payload.rating,
        "message": safe_trim(payload.message, 5000) or "",
        "page_url": safe_trim(payload.page_url, 1000),
        "document_id": safe_trim(payload.document_id, 200),
        "question": safe_trim(payload.question, 1200),
        "answer_preview": safe_trim(payload.answer_preview, 2000),
        "email": safe_trim(payload.email, 320),
        "user_agent": safe_trim(request.headers.get("user-agent", ""), 800),
        "client_host": client_host,
        "saved_to_hf_dataset": 0,
        "hf_dataset_error": None
    }


def save_feedback_local(record: Dict[str, Any]) -> None:
    init_feedback_db()

    conn = sqlite3.connect(str(get_feedback_db_path()))
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO feedback (
        feedback_id,
        created_at,
        feedback_type,
        rating,
        message,
        page_url,
        document_id,
        question,
        answer_preview,
        email,
        user_agent,
        client_host,
        saved_to_hf_dataset,
        hf_dataset_error
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["feedback_id"],
        record["created_at"],
        record["feedback_type"],
        record["rating"],
        record["message"],
        record["page_url"],
        record["document_id"],
        record["question"],
        record["answer_preview"],
        record["email"],
        record["user_agent"],
        record["client_host"],
        record["saved_to_hf_dataset"],
        record["hf_dataset_error"]
    ))

    conn.commit()
    conn.close()

    with get_feedback_jsonl_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def update_feedback_hf_status(feedback_id: str, saved: bool, error: Optional[str]) -> None:
    try:
        conn = sqlite3.connect(str(get_feedback_db_path()))
        cur = conn.cursor()

        cur.execute(
            "UPDATE feedback SET saved_to_hf_dataset = ?, hf_dataset_error = ? WHERE feedback_id = ?",
            (1 if saved else 0, error, feedback_id)
        )

        conn.commit()
        conn.close()
    except Exception:
        pass


def get_hf_feedback_config() -> Dict[str, Optional[str]]:
    token = (
        os.getenv("HF_FEEDBACK_TOKEN", "").strip()
        or os.getenv("HF_TOKEN", "").strip()
        or os.getenv("HF_API_TOKEN", "").strip()
    )

    dataset = os.getenv("HF_FEEDBACK_DATASET", "").strip()

    return {
        "token": token or None,
        "dataset": dataset or None
    }


def save_feedback_to_hf_dataset(record: Dict[str, Any]) -> Dict[str, Any]:
    config = get_hf_feedback_config()

    if not config["dataset"] or not config["token"]:
        return {
            "attempted": False,
            "saved": False,
            "error": "HF_FEEDBACK_DATASET and HF_FEEDBACK_TOKEN/HF_API_TOKEN are not configured."
        }

    try:
        from huggingface_hub import HfApi, hf_hub_download

        api = HfApi(token=config["token"])
        repo_id = config["dataset"]

        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=True,
            exist_ok=True
        )

        existing_lines = []

        try:
            old_file = hf_hub_download(
                repo_id=repo_id,
                filename="feedback.jsonl",
                repo_type="dataset",
                token=config["token"]
            )

            existing_lines = Path(old_file).read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            existing_lines = []

        existing_lines.append(json.dumps(record, ensure_ascii=False))

        temp_path = get_feedback_dir() / "feedback_hf_upload.jsonl"
        temp_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")

        api.upload_file(
            path_or_fileobj=str(temp_path),
            path_in_repo="feedback.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            token=config["token"],
            commit_message=f"Add feedback {record['feedback_id']}"
        )

        return {
            "attempted": True,
            "saved": True,
            "error": None,
            "dataset": repo_id
        }

    except Exception as exc:
        return {
            "attempted": True,
            "saved": False,
            "error": str(exc),
            "dataset": config["dataset"]
        }


def submit_feedback(payload: FeedbackRequest, request: Request) -> Dict[str, Any]:
    record = feedback_to_record(payload, request)

    save_feedback_local(record)

    hf_result = save_feedback_to_hf_dataset(record)

    if hf_result.get("attempted"):
        update_feedback_hf_status(
            feedback_id=record["feedback_id"],
            saved=bool(hf_result.get("saved")),
            error=hf_result.get("error")
        )

        record["saved_to_hf_dataset"] = 1 if hf_result.get("saved") else 0
        record["hf_dataset_error"] = hf_result.get("error")

    return {
        "status": "success",
        "feedback_id": record["feedback_id"],
        "saved_local_sqlite": True,
        "saved_local_jsonl": True,
        "hf_dataset_backup": hf_result,
        "message": "Feedback saved. Configure HF_FEEDBACK_DATASET for permanent dataset backup."
    }


def list_feedback(limit: int = 100) -> Dict[str, Any]:
    init_feedback_db()

    limit = max(1, min(int(limit or 100), 500))

    conn = sqlite3.connect(str(get_feedback_db_path()))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return {
        "status": "success",
        "db_path": str(get_feedback_db_path()),
        "jsonl_path": str(get_feedback_jsonl_path()),
        "count": len(rows),
        "feedback": rows
    }


def export_feedback_jsonl() -> str:
    if get_feedback_jsonl_path().exists():
        return get_feedback_jsonl_path().read_text(encoding="utf-8", errors="ignore")

    data = list_feedback(limit=500)["feedback"]
    return "\n".join(json.dumps(row, ensure_ascii=False) for row in data) + "\n"


def feedback_status() -> Dict[str, Any]:
    config = get_hf_feedback_config()

    return {
        "local_sqlite_path": str(get_feedback_db_path()),
        "local_jsonl_path": str(get_feedback_jsonl_path()),
        "hf_feedback_dataset_configured": bool(config["dataset"]),
        "hf_feedback_token_configured": bool(config["token"]),
        "hf_feedback_dataset": config["dataset"],
        "note": (
            "Local feedback files are useful for local testing. "
            "For permanent Hugging Face backup, set HF_FEEDBACK_DATASET and HF_FEEDBACK_TOKEN or HF_API_TOKEN."
        )
    }
