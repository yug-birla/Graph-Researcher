from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

Path("app/product").mkdir(parents=True, exist_ok=True)
Path("app/product/__init__.py").touch()

# =====================================================
# 1. requirements update
# =====================================================

req_path = Path("requirements.txt")
req = req_path.read_text(encoding="utf-8-sig") if req_path.exists() else ""

if "huggingface_hub" not in req:
    req += "\nhuggingface_hub>=0.23.0\n"

req_path.write_text(req.strip() + "\n", encoding="utf-8")


# =====================================================
# 2. Feedback service
# =====================================================

Path("app/product/feedback_service.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# 3. Patch main.py routes
# =====================================================

main_path = Path("app/main.py")
main = main_path.read_text(encoding="utf-8-sig")
main = main.replace("\ufeff", "")

imports = """
from fastapi import Request, Query
from fastapi.responses import PlainTextResponse
from app.product.feedback_service import (
    FeedbackRequest,
    submit_feedback,
    list_feedback,
    export_feedback_jsonl,
    feedback_status,
)
"""

if "from app.product.feedback_service import" not in main:
    main = imports + "\n" + main

routes = r'''

# Feedback endpoints

@app.post("/feedback")
def submit_user_feedback(payload: FeedbackRequest, request: Request):
    return submit_feedback(payload=payload, request=request)


@app.get("/feedback/status")
def get_feedback_status():
    return feedback_status()


@app.get("/admin/api/feedback")
def admin_list_feedback(request: Request, limit: int = Query(100, ge=1, le=500)):
    try:
        from app.product.admin_monitoring_service import require_secure_admin
        require_secure_admin(request)
    except Exception:
        try:
            from app.product.auth_service import require_admin_user
            require_admin_user(request)
        except Exception as exc:
            raise exc

    return list_feedback(limit=limit)


@app.get("/admin/api/feedback/export", response_class=PlainTextResponse)
def admin_export_feedback(request: Request):
    try:
        from app.product.admin_monitoring_service import require_secure_admin
        require_secure_admin(request)
    except Exception:
        try:
            from app.product.auth_service import require_admin_user
            require_admin_user(request)
        except Exception as exc:
            raise exc

    return export_feedback_jsonl()
'''

if "Feedback endpoints" not in main:
    main += routes
else:
    print("Feedback endpoints already exist.")

main_path.write_text(main, encoding="utf-8")


# =====================================================
# 4. Patch app UI feedback box
# =====================================================

ui_path = Path("app/product/final_product_ui.py")
ui = ui_path.read_text(encoding="utf-8-sig")
ui = ui.replace("\ufeff", "")

feedback_box = r'''
        <div class="panel-section" id="feedbackBox">
            <h3>Feedback</h3>
            <select id="feedbackType">
                <option value="general">General feedback</option>
                <option value="answer_quality">Answer quality issue</option>
                <option value="ui_bug">UI bug</option>
                <option value="source_issue">Source/citation issue</option>
                <option value="feature_request">Feature request</option>
            </select>

            <select id="feedbackRating" style="margin-top:8px;">
                <option value="">Rating optional</option>
                <option value="5">5 - Excellent</option>
                <option value="4">4 - Good</option>
                <option value="3">3 - Average</option>
                <option value="2">2 - Poor</option>
                <option value="1">1 - Bad</option>
            </select>

            <textarea id="feedbackMessage" placeholder="Write feedback..." style="width:100%;min-height:82px;margin-top:8px;"></textarea>
            <button class="full green" onclick="submitFeedback()">Submit Feedback</button>
            <div id="feedbackStatus" class="small" style="color:#64748b;">Feedback is saved to backend storage.</div>
        </div>
'''

if 'id="feedbackBox"' not in ui:
    target = '<div class="panel-section danger-zone">'
    if target in ui:
        ui = ui.replace(target, feedback_box + "\n        " + target, 1)
    else:
        ui = ui.replace("</aside>", feedback_box + "\n    </aside>", 1)

feedback_js = r'''
<script id="feedback-submit-layer">
(function () {
    function byId(id) {
        return document.getElementById(id);
    }

    function selectedDocumentIdForFeedback() {
        try {
            if (typeof selectedId !== "undefined" && selectedId) return selectedId;
        } catch (e) {}

        try {
            const raw = localStorage.getItem("graphrag_stable_selected_document_id");
            if (raw) return raw;
        } catch (e) {}

        try {
            const raw2 = localStorage.getItem("graphrag_selected_document_id");
            if (raw2) return raw2;
        } catch (e) {}

        return null;
    }

    function latestQuestionForFeedback() {
        try {
            const chats = JSON.parse(localStorage.getItem("graphrag_stable_chats") || "{}");
            const keys = Object.keys(chats);

            for (let i = keys.length - 1; i >= 0; i--) {
                const convo = chats[keys[i]] || [];
                for (let j = convo.length - 1; j >= 0; j--) {
                    if (convo[j].role === "user") return convo[j].content || "";
                }
            }
        } catch (e) {}

        return "";
    }

    function latestAnswerPreviewForFeedback() {
        try {
            const chats = JSON.parse(localStorage.getItem("graphrag_stable_chats") || "{}");
            const keys = Object.keys(chats);

            for (let i = keys.length - 1; i >= 0; i--) {
                const convo = chats[keys[i]] || [];
                for (let j = convo.length - 1; j >= 0; j--) {
                    if (convo[j].role === "assistant") {
                        return String(convo[j].content || convo[j].html || "").slice(0, 1000);
                    }
                }
            }
        } catch (e) {}

        return "";
    }

    window.submitFeedback = async function () {
        const typeEl = byId("feedbackType");
        const ratingEl = byId("feedbackRating");
        const msgEl = byId("feedbackMessage");
        const statusEl = byId("feedbackStatus");

        const message = msgEl ? msgEl.value.trim() : "";

        if (!message) {
            alert("Write feedback first.");
            return;
        }

        if (statusEl) statusEl.textContent = "Saving feedback...";

        const ratingValue = ratingEl && ratingEl.value ? Number(ratingEl.value) : null;

        const payload = {
            feedback_type: typeEl ? typeEl.value : "general",
            rating: ratingValue,
            message: message,
            page_url: window.location.href,
            document_id: selectedDocumentIdForFeedback(),
            question: latestQuestionForFeedback(),
            answer_preview: latestAnswerPreviewForFeedback()
        };

        try {
            const response = await fetch("/feedback", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(JSON.stringify(data));
            }

            if (msgEl) msgEl.value = "";

            if (statusEl) {
                statusEl.textContent = data.hf_dataset_backup && data.hf_dataset_backup.saved
                    ? "Feedback saved permanently to HF Dataset."
                    : "Feedback saved locally. Configure HF_FEEDBACK_DATASET for permanent backup.";
            }

            alert("Feedback submitted. Thank you.");

        } catch (error) {
            if (statusEl) statusEl.textContent = "Feedback save failed.";
            alert("Feedback failed: " + error.message);
        }
    };
})();
</script>
'''

if "feedback-submit-layer" not in ui:
    idx = ui.rfind("</body>")
    if idx != -1:
        ui = ui[:idx] + feedback_js + "\n" + ui[idx:]
    else:
        ui += feedback_js

ui_path.write_text(ui, encoding="utf-8")


# =====================================================
# 5. Patch secure admin UI with feedback view if present
# =====================================================

secure_ui_path = Path("app/product/secure_admin_ui.py")

if secure_ui_path.exists():
    secure = secure_ui_path.read_text(encoding="utf-8-sig")
    secure = secure.replace("\ufeff", "")

    if "loadFeedback()" not in secure:
        secure = secure.replace(
            '<button onclick="loadRoutes()">Routes</button>',
            '<button onclick="loadRoutes()">Routes</button>\n            <button onclick="loadFeedback()">Feedback</button>',
            1
        )

        feedback_admin_js = r'''
async function loadFeedback() {
    byId("pageTitle").textContent = "User Feedback";
    try {
        const data = await apiGet("/admin/api/feedback?limit=100");
        byId("notice").innerHTML = "";

        let html = '<div class="card"><h3>Feedback: ' + escapeHtml(data.count) + '</h3>';
        html += '<p><a href="/admin/api/feedback/export" target="_blank">Open JSONL export</a></p>';
        html += '<table><thead><tr><th>Time</th><th>Type</th><th>Rating</th><th>Message</th><th>Document</th></tr></thead><tbody>';

        (data.feedback || []).forEach(item => {
            html += '<tr>';
            html += '<td>' + escapeHtml(item.created_at) + '</td>';
            html += '<td>' + escapeHtml(item.feedback_type) + '</td>';
            html += '<td>' + escapeHtml(item.rating || "") + '</td>';
            html += '<td>' + escapeHtml(item.message || "") + '</td>';
            html += '<td>' + escapeHtml(item.document_id || "") + '</td>';
            html += '</tr>';
        });

        html += '</tbody></table></div>';
        byId("content").innerHTML = html;
    } catch (error) {
        showError(error);
    }
}
'''
        secure = secure.replace("loadOverview();", feedback_admin_js + "\nloadOverview();", 1)

    secure_ui_path.write_text(secure, encoding="utf-8")

print("Phase 44 feedback collection with optional permanent HF Dataset backup added.")
