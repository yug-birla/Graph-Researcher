
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
