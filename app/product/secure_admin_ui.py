
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
            <button onclick="loadFeedback()">Feedback</button>
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
