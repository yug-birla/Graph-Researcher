
import os
import time
import json
import sqlite3
import platform
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import Request, HTTPException

from app.core.config import settings
from app.product.auth_service import get_current_user_from_request, get_admin_emails


APP_STARTED_AT = time.time()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_path(value, fallback: str) -> Path:
    try:
        if value:
            return Path(value)
    except Exception:
        pass
    return Path(fallback)


def get_runtime_paths() -> Dict[str, Path]:
    return {
        "upload_dir": safe_path(getattr(settings, "UPLOAD_DIR", None), "/tmp/graphrag/uploads"),
        "processed_dir": safe_path(getattr(settings, "PROCESSED_DIR", None), "/tmp/graphrag/processed"),
        "qdrant_dir": safe_path(getattr(settings, "QDRANT_LOCAL_PATH", None), "/tmp/graphrag/qdrant"),
        "evaluation_dir": safe_path(getattr(settings, "EVALUATION_DIR", None), "/tmp/graphrag/evaluation"),
    }


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0

    if path.is_file():
        try:
            return path.stat().st_size
        except Exception:
            return 0

    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except Exception:
                    pass
    except Exception:
        pass

    return total


def count_files(path: Path) -> int:
    if not path.exists():
        return 0

    if path.is_file():
        return 1

    count = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                count += 1
    except Exception:
        pass

    return count


def list_recent_items(path: Path, limit: int = 20) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    items = []

    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "size_bytes": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                    })
                except Exception:
                    pass
    except Exception:
        pass

    items.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
    return items[:limit]


def get_product_db_path() -> Path:
    candidates = [
        Path("data/product.db"),
        Path("product.db"),
        Path("/tmp/graphrag/product.db"),
        Path("/tmp/product.db"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def get_db_counts() -> Dict[str, Any]:
    result = {
        "db_path": str(get_product_db_path()),
        "exists": get_product_db_path().exists(),
        "tables": {}
    }

    db_path = get_product_db_path()

    if not db_path.exists():
        return result

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        for table in ["users", "user_documents", "conversations", "messages", "admin_logs", "app_settings"]:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                result["tables"][table] = cur.fetchone()[0]
            except Exception as exc:
                result["tables"][table] = f"unavailable: {exc}"

        conn.close()
    except Exception as exc:
        result["error"] = str(exc)

    return result


def admin_key_configured() -> bool:
    return bool(os.getenv("ADMIN_DASHBOARD_KEY", "").strip())


def require_secure_admin(request: Request) -> Dict[str, Any]:
    user = get_current_user_from_request(request)

    if not user.get("authenticated"):
        raise HTTPException(status_code=401, detail="Login required for admin dashboard.")

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required.")

    configured_key = os.getenv("ADMIN_DASHBOARD_KEY", "").strip()

    if configured_key:
        provided_key = request.headers.get("x-admin-key", "").strip()

        if provided_key != configured_key:
            log_admin_event(
                request=request,
                user=user,
                action="admin_key_failed",
                detail="Invalid or missing admin dashboard key."
            )
            raise HTTPException(status_code=403, detail="Valid admin dashboard key required.")

    return user


def audit_log_path() -> Path:
    paths = get_runtime_paths()
    audit_dir = paths["processed_dir"] / "_admin"
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir / "admin_audit.log"


def log_admin_event(request: Request, user: Dict[str, Any], action: str, detail: str = "") -> None:
    event = {
        "time": now_iso(),
        "action": action,
        "detail": detail,
        "email": user.get("email"),
        "role": user.get("role"),
        "path": str(request.url.path),
        "client": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent", "")
    }

    try:
        with audit_log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_admin_audit(limit: int = 30) -> List[Dict[str, Any]]:
    path = audit_log_path()

    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]

    events = []
    for line in reversed(lines):
        try:
            events.append(json.loads(line))
        except Exception:
            pass

    return events


def get_storage_report() -> Dict[str, Any]:
    paths = get_runtime_paths()
    report = {}

    for name, path in paths.items():
        report[name] = {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": size_bytes(path),
            "file_count": count_files(path),
            "recent_files": list_recent_items(path, limit=10)
        }

    return report


def get_security_report() -> Dict[str, Any]:
    return {
        "admin_emails": sorted(list(get_admin_emails())),
        "admin_dashboard_key_configured": admin_key_configured(),
        "allow_header_auth": os.getenv("ALLOW_HEADER_AUTH", "true"),
        "session_secret_configured": bool(os.getenv("SESSION_SECRET_KEY", "").strip()),
        "google_oauth_configured": bool(
            os.getenv("GOOGLE_CLIENT_ID", "").strip()
            and os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        ),
        "recommendations": [
            "Set ADMIN_DASHBOARD_KEY in Hugging Face secrets.",
            "Set SESSION_SECRET_KEY in Hugging Face secrets.",
            "Keep ADMIN_EMAILS restricted to your own email.",
            "Disable ALLOW_HEADER_AUTH for stronger production security after OAuth is working.",
            "Do not upload sensitive documents until persistent private storage and access control are complete."
        ]
    }


def get_route_report(app) -> Dict[str, Any]:
    routes = []

    for route in app.routes:
        path = getattr(route, "path", "")
        methods = sorted(list(getattr(route, "methods", []) or []))

        if not path:
            continue

        routes.append({
            "path": path,
            "methods": methods
        })

    routes.sort(key=lambda x: x["path"])

    return {
        "route_count": len(routes),
        "routes": routes
    }


def get_admin_overview(request: Request, app) -> Dict[str, Any]:
    user = require_secure_admin(request)

    log_admin_event(
        request=request,
        user=user,
        action="view_admin_overview",
        detail="Admin monitoring overview loaded."
    )

    storage = get_storage_report()
    db = get_db_counts()
    security = get_security_report()

    uploaded_docs = 0
    processed_docs = 0

    upload_dir = get_runtime_paths()["upload_dir"]
    processed_dir = get_runtime_paths()["processed_dir"]

    if upload_dir.exists():
        try:
            uploaded_docs = len([x for x in upload_dir.iterdir()])
        except Exception:
            uploaded_docs = 0

    if processed_dir.exists():
        try:
            processed_docs = len([x for x in processed_dir.iterdir() if x.is_dir() and not x.name.startswith("_")])
        except Exception:
            processed_docs = 0

    return {
        "status": "ok",
        "time": now_iso(),
        "user": {
            "email": user.get("email"),
            "role": user.get("role"),
            "auth_provider": user.get("auth_provider")
        },
        "server": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pid": os.getpid(),
            "uptime_seconds": int(time.time() - APP_STARTED_AT)
        },
        "summary": {
            "uploaded_runtime_items": uploaded_docs,
            "processed_document_folders": processed_docs,
            "admin_key_configured": security["admin_dashboard_key_configured"],
            "product_db_exists": db["exists"],
            "routes_count": len(app.routes)
        },
        "storage": storage,
        "database": db,
        "security": security,
        "recent_admin_events": read_admin_audit(limit=20)
    }


def get_storage_only(request: Request) -> Dict[str, Any]:
    user = require_secure_admin(request)
    log_admin_event(request, user, "view_storage", "Admin viewed storage report.")
    return get_storage_report()


def get_security_only(request: Request) -> Dict[str, Any]:
    user = require_secure_admin(request)
    log_admin_event(request, user, "view_security", "Admin viewed security report.")
    return get_security_report()


def get_routes_only(request: Request, app) -> Dict[str, Any]:
    user = require_secure_admin(request)
    log_admin_event(request, user, "view_routes", "Admin viewed route report.")
    return get_route_report(app)
