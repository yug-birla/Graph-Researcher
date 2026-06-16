from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")

# =====================================================
# 1. Minimal product_db fallback if missing
# =====================================================

product_db_path = Path("app/product/product_db.py")

if not product_db_path.exists():
    product_db_path.write_text(r'''
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.core.config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_database_path() -> Path:
    env_path = os.getenv("APP_DATABASE_PATH")

    if env_path:
        db_path = Path(env_path)
    else:
        db_path = Path(settings.PROCESSED_DIR).parent / "product_app.sqlite3"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection():
    conn = sqlite3.connect(str(get_database_path()))
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def init_product_database() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        auth_provider TEXT DEFAULT 'local',
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        last_login_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_documents (
        document_id TEXT PRIMARY KEY,
        owner_user_id TEXT,
        source_file_name TEXT,
        upload_status TEXT DEFAULT 'uploaded',
        index_status TEXT DEFAULT 'not_indexed',
        graph_status TEXT DEFAULT 'not_built',
        chunk_count INTEGER DEFAULT 0,
        entity_count INTEGER DEFAULT 0,
        relation_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        owner_user_id TEXT,
        document_id TEXT,
        title TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT NOT NULL,
        metadata_json TEXT
    )
    """)

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "database_path": str(get_database_path())
    }


def get_database_status() -> Dict[str, Any]:
    init_product_database()

    conn = get_connection()
    cur = conn.cursor()

    tables = ["users", "user_documents", "conversations", "messages"]
    counts = {}

    for table in tables:
        cur.execute(f"SELECT COUNT(*) AS count FROM {table}")
        counts[table] = int(cur.fetchone()["count"])

    conn.close()

    return {
        "status": "healthy",
        "database_path": str(get_database_path()),
        "table_counts": counts
    }


def upsert_user(
    user_id: str,
    email: str,
    name: Optional[str] = None,
    role: str = "user",
    auth_provider: str = "local",
    avatar_url: Optional[str] = None
):
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (user_id, email, name, role, auth_provider, is_active, created_at, last_login_at)
    VALUES (?, ?, ?, ?, ?, 1, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
        name = excluded.name,
        role = excluded.role,
        auth_provider = excluded.auth_provider,
        last_login_at = excluded.last_login_at
    """, (user_id, email, name, role, auth_provider, now, now))

    conn.commit()

    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = dict(cur.fetchone())

    conn.close()
    return user


def list_users(limit: int = 100):
    init_product_database()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT user_id, email, name, role, auth_provider, is_active, created_at, last_login_at
    FROM users
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    rows = rows_to_dicts(cur.fetchall())
    conn.close()
    return rows


def list_documents(limit: int = 100):
    init_product_database()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM user_documents
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    rows = rows_to_dicts(cur.fetchall())
    conn.close()
    return rows


def list_conversations(limit: int = 100):
    init_product_database()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM conversations
    ORDER BY updated_at DESC
    LIMIT ?
    """, (limit,))

    rows = rows_to_dicts(cur.fetchall())
    conn.close()
    return rows
''', encoding="utf-8")
    print("Created fallback product_db.py")
else:
    print("product_db.py already exists")


# =====================================================
# 2. Auth service
# =====================================================

Path("app/product/auth_service.py").write_text(r'''
import os
from typing import Dict, Any, Optional

from fastapi import Request, HTTPException

from app.product.product_db import upsert_user


DEFAULT_ADMIN_EMAILS = {
    "2006yugb@gmail.com"
}


def get_admin_emails():
    raw = os.getenv("ADMIN_EMAILS", "")

    emails = {
        email.strip().lower()
        for email in raw.split(",")
        if email.strip()
    }

    return emails | DEFAULT_ADMIN_EMAILS


def normalize_email(email: Optional[str]) -> str:
    return str(email or "").strip().lower()


def make_user_id(email: str) -> str:
    return "user_" + email.replace("@", "_").replace(".", "_")


def infer_role(email: str) -> str:
    if normalize_email(email) in get_admin_emails():
        return "admin"

    return "user"


def get_current_user_from_request(request: Request) -> Dict[str, Any]:
    email = normalize_email(request.headers.get("x-user-email"))
    name = request.headers.get("x-user-name")

    if not email:
        return {
            "authenticated": False,
            "user_id": None,
            "email": None,
            "name": "Guest",
            "role": "guest",
            "auth_provider": "none"
        }

    role = infer_role(email)
    user_id = make_user_id(email)

    user = upsert_user(
        user_id=user_id,
        email=email,
        name=name or email.split("@")[0],
        role=role,
        auth_provider="header_dev"
    )

    user["authenticated"] = True
    return user


def require_authenticated_user(request: Request) -> Dict[str, Any]:
    user = get_current_user_from_request(request)

    if not user.get("authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    return user


def require_admin_user(request: Request) -> Dict[str, Any]:
    user = require_authenticated_user(request)

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return user


def dev_login_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    email = normalize_email(email)

    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    role = infer_role(email)
    user_id = make_user_id(email)

    user = upsert_user(
        user_id=user_id,
        email=email,
        name=name or email.split("@")[0],
        role=role,
        auth_provider="dev_login"
    )

    user["authenticated"] = True
    user["dev_header_hint"] = {
        "X-User-Email": email,
        "X-User-Name": name or email.split("@")[0]
    }

    return user
''', encoding="utf-8")


# =====================================================
# 3. Admin service
# =====================================================

Path("app/product/admin_service.py").write_text(r'''
from typing import Dict, Any

from app.product.product_db import (
    get_database_status,
    list_users,
    list_documents,
    list_conversations
)


def get_admin_status(current_admin: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "ok",
        "message": "Admin backend is available.",
        "admin": {
            "email": current_admin.get("email"),
            "role": current_admin.get("role")
        },
        "database": get_database_status()
    }


def get_admin_users(limit: int = 100) -> Dict[str, Any]:
    users = list_users(limit=limit)

    return {
        "count": len(users),
        "users": users
    }


def get_admin_documents(limit: int = 100) -> Dict[str, Any]:
    documents = list_documents(limit=limit)

    return {
        "count": len(documents),
        "documents": documents
    }


def get_admin_conversations(limit: int = 100) -> Dict[str, Any]:
    conversations = list_conversations(limit=limit)

    return {
        "count": len(conversations),
        "conversations": conversations
    }


def get_admin_system_summary() -> Dict[str, Any]:
    db = get_database_status()

    return {
        "status": "ok",
        "database": db,
        "notes": [
            "Admin tools are separated from the normal user app.",
            "Normal users should not see API docs or GraphRAG console links.",
            "Admin APIs are protected by backend role checks."
        ]
    }
''', encoding="utf-8")


# =====================================================
# 4. Admin UI
# =====================================================

Path("app/product/admin_ui.py").write_text(r'''
def get_admin_panel_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphResearcher Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: #f8fafc;
            color: #0f172a;
        }

        .layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }

        .sidebar {
            background: #0f172a;
            color: white;
            padding: 20px;
        }

        .brand {
            font-weight: 900;
            font-size: 24px;
            margin-bottom: 6px;
        }

        .sub {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 22px;
        }

        input {
            width: 100%;
            padding: 11px;
            border-radius: 9px;
            border: 1px solid #cbd5e1;
            margin-bottom: 10px;
        }

        button {
            border: none;
            background: #2563eb;
            color: white;
            border-radius: 10px;
            padding: 11px 13px;
            cursor: pointer;
            font-weight: 800;
            width: 100%;
            margin-bottom: 9px;
        }

        button:hover { background: #1d4ed8; }
        button.dark { background: #334155; }
        button.green { background: #059669; }
        button.red { background: #dc2626; }

        .main {
            padding: 26px;
        }

        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }

        .status-pill {
            display: inline-block;
            padding: 7px 11px;
            background: #e0f2fe;
            color: #075985;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 800;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 20px;
        }

        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        .card h3 {
            margin-top: 0;
        }

        .metric {
            font-size: 30px;
            font-weight: 900;
            color: #1d4ed8;
        }

        pre {
            white-space: pre-wrap;
            word-break: break-word;
            background: #0f172a;
            color: #e5e7eb;
            padding: 16px;
            border-radius: 14px;
            max-height: 560px;
            overflow: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }

        th, td {
            border-bottom: 1px solid #e5e7eb;
            text-align: left;
            padding: 10px;
            font-size: 13px;
        }

        th {
            background: #f1f5f9;
            font-weight: 900;
        }

        .warning {
            background: #fff7ed;
            border: 1px solid #fed7aa;
            color: #9a3412;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .hidden {
            display: none;
        }

        @media(max-width: 950px) {
            .layout {
                grid-template-columns: 1fr;
            }

            .sidebar {
                position: static;
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
<div class="layout">
    <aside class="sidebar">
        <div class="brand">Admin Panel</div>
        <div class="sub">GraphResearcher internal tools</div>

        <label>Admin email</label>
        <input id="adminEmail" value="2006yugb@gmail.com">

        <button onclick="saveAdmin()">Use Admin Email</button>
        <button onclick="loadStatus()" class="green">Dashboard</button>
        <button onclick="loadUsers()">Users</button>
        <button onclick="loadDocuments()">Documents</button>
        <button onclick="loadConversations()">Conversations</button>
        <button onclick="loadSystem()">System</button>
        <button onclick="loadHealth()" class="dark">Deployment Health</button>
        <button onclick="loadLLM()" class="dark">LLM Status</button>

        <hr style="border-color: rgba(255,255,255,0.18); margin: 18px 0;">

        <button onclick="window.open('/app','_blank')" class="dark">Open User App</button>
        <button onclick="window.open('/docs','_blank')" class="dark">Open API Docs</button>
        <button onclick="window.open('/graphrag-demo','_blank')" class="dark">Open GraphRAG Console</button>
        <button onclick="logout()" class="red">Clear Admin Session</button>
    </aside>

    <main class="main">
        <div class="top">
            <div>
                <h1>GraphResearcher Admin</h1>
                <p style="color:#64748b;margin-top:-8px;">Hidden admin workspace for monitoring users, documents, system health, and developer tools.</p>
            </div>
            <span id="statusPill" class="status-pill">Not checked</span>
        </div>

        <div class="warning">
            This page is hidden from the normal user app. The backend APIs still check admin role using the admin email.
            Later Google OAuth will replace this temporary email-header login.
        </div>

        <div id="dashboardCards" class="grid">
            <div class="card">
                <h3>Users</h3>
                <div id="usersMetric" class="metric">-</div>
            </div>
            <div class="card">
                <h3>Documents</h3>
                <div id="docsMetric" class="metric">-</div>
            </div>
            <div class="card">
                <h3>Conversations</h3>
                <div id="convMetric" class="metric">-</div>
            </div>
            <div class="card">
                <h3>Status</h3>
                <div id="systemMetric" class="metric">-</div>
            </div>
        </div>

        <div class="card">
            <h3 id="outputTitle">Output</h3>
            <div id="tableOutput"></div>
            <pre id="rawOutput">{}</pre>
        </div>
    </main>
</div>

<script>
function getAdminEmail() {
    return localStorage.getItem("graphrag_admin_email") || document.getElementById("adminEmail").value.trim();
}

function saveAdmin() {
    const email = document.getElementById("adminEmail").value.trim();
    localStorage.setItem("graphrag_admin_email", email);
    setStatus("Admin email saved");
    loadStatus();
}

function logout() {
    localStorage.removeItem("graphrag_admin_email");
    setStatus("Admin cleared");
    document.getElementById("rawOutput").textContent = "{}";
    document.getElementById("tableOutput").innerHTML = "";
}

function headers() {
    return {
        "X-User-Email": getAdminEmail(),
        "X-User-Name": "Admin"
    };
}

function setStatus(text) {
    document.getElementById("statusPill").textContent = text;
}

function showRaw(title, data) {
    document.getElementById("outputTitle").textContent = title;
    document.getElementById("rawOutput").textContent = JSON.stringify(data, null, 2);
}

async function fetchJson(url, useAdminHeaders = true) {
    const response = await fetch(url, {
        headers: useAdminHeaders ? headers() : {}
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(JSON.stringify(data));
    }

    return data;
}

function renderTable(rows) {
    const box = document.getElementById("tableOutput");

    if (!rows || rows.length === 0) {
        box.innerHTML = "<p>No rows.</p>";
        return;
    }

    const columns = Object.keys(rows[0]).slice(0, 8);

    let html = "<table><thead><tr>";

    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });

    html += "</tr></thead><tbody>";

    rows.forEach(row => {
        html += "<tr>";
        columns.forEach(col => {
            html += `<td>${String(row[col] ?? "").slice(0, 80)}</td>`;
        });
        html += "</tr>";
    });

    html += "</tbody></table>";
    box.innerHTML = html;
}

async function loadStatus() {
    try {
        setStatus("Loading...");
        const data = await fetchJson("/admin/status");

        showRaw("Admin Status", data);

        const counts = data.database?.table_counts || {};
        document.getElementById("usersMetric").textContent = counts.users ?? "-";
        document.getElementById("docsMetric").textContent = counts.user_documents ?? "-";
        document.getElementById("convMetric").textContent = counts.conversations ?? "-";
        document.getElementById("systemMetric").textContent = data.status || "ok";

        document.getElementById("tableOutput").innerHTML = "";
        setStatus("Admin verified");
    } catch (error) {
        setStatus("Access denied");
        showRaw("Error", { error: error.message });
    }
}

async function loadUsers() {
    try {
        setStatus("Loading users...");
        const data = await fetchJson("/admin/users");
        showRaw("Users", data);
        renderTable(data.users || []);
        setStatus("Users loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

async function loadDocuments() {
    try {
        setStatus("Loading documents...");
        const data = await fetchJson("/admin/documents");
        showRaw("Documents", data);
        renderTable(data.documents || []);
        setStatus("Documents loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

async function loadConversations() {
    try {
        setStatus("Loading conversations...");
        const data = await fetchJson("/admin/conversations");
        showRaw("Conversations", data);
        renderTable(data.conversations || []);
        setStatus("Conversations loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

async function loadSystem() {
    try {
        setStatus("Loading system...");
        const data = await fetchJson("/admin/system");
        showRaw("System", data);
        document.getElementById("tableOutput").innerHTML = "";
        setStatus("System loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

async function loadHealth() {
    try {
        setStatus("Loading health...");
        const data = await fetchJson("/deployment/health", false);
        showRaw("Deployment Health", data);
        document.getElementById("tableOutput").innerHTML = "";
        setStatus("Health loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

async function loadLLM() {
    try {
        setStatus("Loading LLM...");
        const data = await fetchJson("/llm/status", false);
        showRaw("LLM Status", data);
        document.getElementById("tableOutput").innerHTML = "";
        setStatus("LLM loaded");
    } catch (error) {
        setStatus("Error");
        showRaw("Error", { error: error.message });
    }
}

document.getElementById("adminEmail").value = getAdminEmail();
loadStatus();
</script>
</body>
</html>
"""
''', encoding="utf-8")


# =====================================================
# 5. Patch main.py
# =====================================================

main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

required_imports = '''
from fastapi import Request, Query
from fastapi.responses import HTMLResponse
from app.product.auth_service import get_current_user_from_request, require_admin_user, dev_login_user
from app.product.admin_service import get_admin_status, get_admin_users, get_admin_documents, get_admin_conversations, get_admin_system_summary
from app.product.admin_ui import get_admin_panel_html
'''

if "from app.product.admin_ui import get_admin_panel_html" not in main_text:
    main_text = required_imports + "\n" + main_text

if '@app.get("/auth/me")' not in main_text:
    main_text += '''

# Auth foundation endpoints

@app.get("/auth/me")
def auth_me(request: Request):
    return get_current_user_from_request(request)


@app.get("/auth/dev-login")
def auth_dev_login(
    email: str = Query(..., min_length=3),
    name: str = Query(None)
):
    return dev_login_user(email=email, name=name)
'''

if '@app.get("/admin",' not in main_text:
    main_text += '''

# Hidden admin panel UI

@app.get("/admin", response_class=HTMLResponse)
def admin_panel_page():
    return get_admin_panel_html()
'''

if '@app.get("/admin/status")' not in main_text:
    main_text += '''

# Admin API endpoints

@app.get("/admin/status")
def admin_status(request: Request):
    current_admin = require_admin_user(request)
    return get_admin_status(current_admin=current_admin)


@app.get("/admin/users")
def admin_users(
    request: Request,
    limit: int = Query(100, ge=1, le=500)
):
    require_admin_user(request)
    return get_admin_users(limit=limit)


@app.get("/admin/documents")
def admin_documents(
    request: Request,
    limit: int = Query(100, ge=1, le=500)
):
    require_admin_user(request)
    return get_admin_documents(limit=limit)


@app.get("/admin/conversations")
def admin_conversations(
    request: Request,
    limit: int = Query(100, ge=1, le=500)
):
    require_admin_user(request)
    return get_admin_conversations(limit=limit)


@app.get("/admin/system")
def admin_system(request: Request):
    require_admin_user(request)
    return get_admin_system_summary()
'''

main_path.write_text(main_text, encoding="utf-8")

print("Phase 31 hidden admin panel patch complete.")
