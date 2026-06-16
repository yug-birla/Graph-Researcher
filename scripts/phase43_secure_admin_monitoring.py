from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

Path("app/product").mkdir(parents=True, exist_ok=True)
Path("app/product/__init__.py").touch()

# =====================================================
# 1. Secure admin monitoring service
# =====================================================

Path("app/product/admin_monitoring_service.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# 2. Secure admin dashboard UI
# =====================================================

Path("app/product/secure_admin_ui.py").write_text(r'''
def get_secure_admin_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Admin - GraphResearcher</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
        }
        .layout {
            display: grid;
            grid-template-columns: 270px 1fr;
            min-height: 100vh;
        }
        .sidebar {
            background: #020617;
            padding: 22px;
            border-right: 1px solid #1e293b;
        }
        .brand {
            font-size: 23px;
            font-weight: 900;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.5;
            margin-bottom: 24px;
        }
        .nav button {
            width: 100%;
            margin-bottom: 10px;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: #1e293b;
            color: white;
            font-weight: 800;
            cursor: pointer;
            text-align: left;
        }
        .nav button:hover { background: #334155; }
        .nav button.primary { background: #2563eb; }
        .nav button.danger { background: #991b1b; }
        .main {
            padding: 26px;
            overflow-y: auto;
        }
        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
            margin-bottom: 22px;
        }
        h1 { margin: 0; font-size: 28px; }
        .pill {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #1e293b;
            color: #bfdbfe;
            font-size: 12px;
            font-weight: 800;
            margin: 3px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(160px, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }
        .card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.22);
        }
        .card h3 {
            margin: 0 0 10px;
            font-size: 15px;
            color: #93c5fd;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 900;
            color: white;
        }
        .small {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
        }
        pre {
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
            overflow-x: auto;
            color: #d1d5db;
            max-height: 430px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #1f2937;
            text-align: left;
            vertical-align: top;
        }
        th { color: #93c5fd; }
        input {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #334155;
            background: #020617;
            color: white;
            margin-bottom: 10px;
        }
        .warning {
            background: #451a03;
            border: 1px solid #92400e;
            color: #fed7aa;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 16px;
        }
        .ok {
            background: #052e16;
            border: 1px solid #166534;
            color: #bbf7d0;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 16px;
        }
        a { color: #93c5fd; }
        @media(max-width: 1050px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { position: static; }
            .grid { grid-template-columns: 1fr 1fr; }
        }
        @media(max-width: 650px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>

<body>
<div class="layout">
    <aside class="sidebar">
        <div class="brand">GraphResearcher Admin</div>
        <div class="subtitle">
            Secure monitoring dashboard for runtime health, storage, routes, and admin security.
        </div>

        <input id="adminKey" type="password" placeholder="Admin dashboard key">
        <button class="primary" onclick="saveKey()">Save Admin Key</button>

        <div class="nav" style="margin-top:18px;">
            <button onclick="loadOverview()">Overview</button>
            <button onclick="loadStorage()">Storage</button>
            <button onclick="loadSecurity()">Security</button>
            <button onclick="loadRoutes()">Routes</button>
            <button onclick="window.location.href='/app'">Open User App</button>
            <button onclick="window.location.href='/auth/logout'">Logout</button>
            <button class="danger" onclick="clearKey()">Clear Admin Key</button>
        </div>

        <p class="small">
            Access requires admin login plus the ADMIN_DASHBOARD_KEY secret.
        </p>
    </aside>

    <main class="main">
        <div class="top">
            <h1 id="pageTitle">Admin Overview</h1>
            <span id="status" class="pill">Ready</span>
        </div>

        <div id="notice"></div>
        <div id="content"></div>
    </main>
</div>

<script>
function byId(id) {
    return document.getElementById(id);
}

function escapeHtml(value) {
    return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}

function formatBytes(bytes) {
    bytes = Number(bytes || 0);

    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + " MB";

    return (bytes / 1024 / 1024 / 1024).toFixed(2) + " GB";
}

function saveKey() {
    const value = byId("adminKey").value.trim();

    if (!value) {
        alert("Enter admin dashboard key first.");
        return;
    }

    sessionStorage.setItem("admin_dashboard_key", value);
    byId("adminKey").value = "";
    loadOverview();
}

function clearKey() {
    sessionStorage.removeItem("admin_dashboard_key");
    byId("notice").innerHTML = '<div class="warning">Admin key cleared from this browser tab.</div>';
}

function getKey() {
    return sessionStorage.getItem("admin_dashboard_key") || "";
}

async function apiGet(url) {
    byId("status").textContent = "Loading...";

    const response = await fetch(url, {
        headers: {
            "X-Admin-Key": getKey()
        }
    });

    const data = await response.json();

    if (!response.ok) {
        byId("status").textContent = "Error";
        throw new Error(data.detail || JSON.stringify(data));
    }

    byId("status").textContent = "Ready";
    return data;
}

function showError(error) {
    byId("content").innerHTML = '<div class="warning"><b>Access or load failed:</b><br>' + escapeHtml(error.message) + '<br><br>Login as admin first, then enter the admin dashboard key.</div>';
}

function renderOverview(data) {
    const s = data.summary || {};
    const sec = data.security || {};

    let notice = "";

    if (!sec.admin_dashboard_key_configured) {
        notice += '<div class="warning"><b>Security warning:</b> ADMIN_DASHBOARD_KEY is not configured. Add it in Hugging Face secrets.</div>';
    } else {
        notice += '<div class="ok"><b>Admin key is configured.</b> Dashboard APIs require X-Admin-Key.</div>';
    }

    byId("notice").innerHTML = notice;

    let html = '';

    html += '<div class="grid">';
    html += '<div class="card"><h3>Uploaded runtime items</h3><div class="metric-value">' + escapeHtml(s.uploaded_runtime_items) + '</div></div>';
    html += '<div class="card"><h3>Processed document folders</h3><div class="metric-value">' + escapeHtml(s.processed_document_folders) + '</div></div>';
    html += '<div class="card"><h3>Routes</h3><div class="metric-value">' + escapeHtml(s.routes_count) + '</div></div>';
    html += '<div class="card"><h3>Product DB</h3><div class="metric-value">' + (s.product_db_exists ? 'Yes' : 'No') + '</div></div>';
    html += '</div>';

    html += '<div class="card"><h3>Current admin</h3>';
    html += '<span class="pill">' + escapeHtml(data.user.email) + '</span>';
    html += '<span class="pill">role: ' + escapeHtml(data.user.role) + '</span>';
    html += '<span class="pill">auth: ' + escapeHtml(data.user.auth_provider) + '</span>';
    html += '</div><br>';

    html += '<div class="card"><h3>Storage summary</h3>';
    html += renderStorageTable(data.storage || {});
    html += '</div><br>';

    html += '<div class="card"><h3>Database counts</h3><pre>' + escapeHtml(JSON.stringify(data.database, null, 2)) + '</pre></div><br>';

    html += '<div class="card"><h3>Recent admin events</h3>';
    html += renderAudit(data.recent_admin_events || []);
    html += '</div>';

    byId("content").innerHTML = html;
}

function renderStorageTable(storage) {
    let html = '<table><thead><tr><th>Name</th><th>Path</th><th>Exists</th><th>Files</th><th>Size</th></tr></thead><tbody>';

    Object.keys(storage).forEach(name => {
        const item = storage[name] || {};
        html += '<tr>';
        html += '<td>' + escapeHtml(name) + '</td>';
        html += '<td>' + escapeHtml(item.path) + '</td>';
        html += '<td>' + escapeHtml(item.exists) + '</td>';
        html += '<td>' + escapeHtml(item.file_count) + '</td>';
        html += '<td>' + escapeHtml(formatBytes(item.size_bytes)) + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

function renderAudit(events) {
    if (!events.length) return '<p class="small">No admin events yet.</p>';

    let html = '<table><thead><tr><th>Time</th><th>Email</th><th>Action</th><th>Client</th></tr></thead><tbody>';

    events.forEach(e => {
        html += '<tr>';
        html += '<td>' + escapeHtml(e.time) + '</td>';
        html += '<td>' + escapeHtml(e.email) + '</td>';
        html += '<td>' + escapeHtml(e.action) + '</td>';
        html += '<td>' + escapeHtml(e.client) + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

async function loadOverview() {
    byId("pageTitle").textContent = "Admin Overview";
    try {
        const data = await apiGet("/admin/api/monitor/overview");
        renderOverview(data);
    } catch (error) {
        showError(error);
    }
}

async function loadStorage() {
    byId("pageTitle").textContent = "Storage Monitoring";
    try {
        const data = await apiGet("/admin/api/monitor/storage");
        byId("notice").innerHTML = "";
        byId("content").innerHTML = '<div class="card"><h3>Runtime storage</h3>' + renderStorageTable(data) + '</div><br><div class="card"><h3>Raw storage JSON</h3><pre>' + escapeHtml(JSON.stringify(data, null, 2)) + '</pre></div>';
    } catch (error) {
        showError(error);
    }
}

async function loadSecurity() {
    byId("pageTitle").textContent = "Security Monitoring";
    try {
        const data = await apiGet("/admin/api/monitor/security");
        byId("notice").innerHTML = data.admin_dashboard_key_configured
            ? '<div class="ok">Admin dashboard key is configured.</div>'
            : '<div class="warning">ADMIN_DASHBOARD_KEY is missing. Add it as a Hugging Face secret.</div>';

        byId("content").innerHTML = '<div class="card"><h3>Security report</h3><pre>' + escapeHtml(JSON.stringify(data, null, 2)) + '</pre></div>';
    } catch (error) {
        showError(error);
    }
}

async function loadRoutes() {
    byId("pageTitle").textContent = "Route Monitoring";
    try {
        const data = await apiGet("/admin/api/monitor/routes");
        byId("notice").innerHTML = "";
        byId("content").innerHTML = '<div class="card"><h3>Routes: ' + escapeHtml(data.route_count) + '</h3><pre>' + escapeHtml(JSON.stringify(data.routes, null, 2)) + '</pre></div>';
    } catch (error) {
        showError(error);
    }
}

loadOverview();
</script>
</body>
</html>
"""
''', encoding="utf-8")


# =====================================================
# 3. Patch main.py routes
# =====================================================

main_path = Path("app/main.py")
main = main_path.read_text(encoding="utf-8-sig")
main = main.replace("\ufeff", "")

imports = """
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.product.secure_admin_ui import get_secure_admin_html
from app.product.auth_service import get_current_user_from_request
from app.product.admin_monitoring_service import (
    get_admin_overview,
    get_storage_only,
    get_security_only,
    get_routes_only,
)
"""

if "from app.product.secure_admin_ui import get_secure_admin_html" not in main:
    main = imports + "\n" + main

routes = r'''

# Secure admin monitoring dashboard

@app.get("/admin/secure", response_class=HTMLResponse)
def secure_admin_dashboard(request: Request):
    user = get_current_user_from_request(request)

    if not user.get("authenticated") or user.get("role") != "admin":
        return RedirectResponse(url="/login", status_code=302)

    return get_secure_admin_html()


@app.get("/admin/api/monitor/overview")
def admin_monitor_overview(request: Request):
    return get_admin_overview(request=request, app=app)


@app.get("/admin/api/monitor/storage")
def admin_monitor_storage(request: Request):
    return get_storage_only(request=request)


@app.get("/admin/api/monitor/security")
def admin_monitor_security(request: Request):
    return get_security_only(request=request)


@app.get("/admin/api/monitor/routes")
def admin_monitor_routes(request: Request):
    return get_routes_only(request=request, app=app)
'''

if "Secure admin monitoring dashboard" not in main:
    main += routes
else:
    print("Secure admin monitoring routes already exist.")

main_path.write_text(main, encoding="utf-8")

print("Phase 43 secure admin monitoring dashboard added.")
