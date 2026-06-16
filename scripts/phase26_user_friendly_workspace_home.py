from pathlib import Path
import re

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")

hf_path = Path("app/deployment/hf_status.py")
text = hf_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

new_ui = r'''


def get_home_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphResearcher</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: #f8fafc;
            color: #0f172a;
        }

        .nav {
            height: 72px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 56px;
            background: white;
            border-bottom: 1px solid #e5e7eb;
        }

        .brand {
            font-weight: 800;
            font-size: 22px;
        }

        .nav a {
            text-decoration: none;
            color: #334155;
            margin-left: 22px;
            font-weight: 600;
        }

        .hero {
            min-height: calc(100vh - 72px);
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            gap: 48px;
            align-items: center;
            padding: 60px 72px;
        }

        .badge {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 13px;
            margin-bottom: 18px;
        }

        h1 {
            font-size: 58px;
            line-height: 1.04;
            margin: 0 0 22px;
            letter-spacing: -2px;
        }

        .hero p {
            font-size: 19px;
            line-height: 1.7;
            color: #475569;
            max-width: 720px;
        }

        .actions {
            margin-top: 32px;
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-block;
            text-decoration: none;
            background: #2563eb;
            color: white;
            padding: 14px 20px;
            border-radius: 12px;
            font-weight: 700;
        }

        .btn.secondary {
            background: #0f172a;
        }

        .btn.light {
            background: white;
            color: #0f172a;
            border: 1px solid #cbd5e1;
        }

        .preview {
            background: #0f172a;
            color: white;
            border-radius: 24px;
            padding: 22px;
            box-shadow: 0 30px 80px rgba(15,23,42,0.24);
        }

        .window-bar {
            display: flex;
            gap: 7px;
            margin-bottom: 18px;
        }

        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #64748b;
        }

        .card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
        }

        .card b { color: #bfdbfe; }

        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            padding: 0 72px 56px;
        }

        .feature {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 22px;
        }

        .feature h3 {
            margin-top: 0;
        }

        .feature p {
            color: #64748b;
            line-height: 1.6;
        }

        @media (max-width: 950px) {
            .nav { padding: 0 22px; }
            .hero {
                grid-template-columns: 1fr;
                padding: 38px 24px;
            }
            h1 { font-size: 42px; }
            .features {
                grid-template-columns: 1fr;
                padding: 0 24px 40px;
            }
        }
    </style>
</head>

<body>
    <div class="nav">
        <div class="brand">GraphResearcher</div>
        <div>
            <a href="/app">App</a>
            <a href="/graphrag-demo">GraphRAG Console</a>
            <a href="/docs">API Docs</a>
        </div>
    </div>

    <section class="hero">
        <div>
            <div class="badge">GraphRAG Research Assistant</div>
            <h1>Chat with your documents using graph-powered RAG.</h1>
            <p>
                Upload a research paper, report, PDF, or notes and ask questions naturally.
                GraphResearcher retrieves evidence, builds an entity-relation graph, generates grounded answers,
                and shows citations without forcing users to handle technical document IDs.
            </p>

            <div class="actions">
                <a class="btn" href="/app">Launch App</a>
                <a class="btn secondary" href="/graphrag-demo">Open GraphRAG Console</a>
                <a class="btn light" href="/deployment/health">Check Health</a>
            </div>
        </div>

        <div class="preview">
            <div class="window-bar">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>

            <div class="card">
                <b>1. Upload</b><br>
                User uploads a document. The app stores the document ID internally.
            </div>

            <div class="card">
                <b>2. Build Graph</b><br>
                Entities and relations are extracted for graph-guided retrieval.
            </div>

            <div class="card">
                <b>3. Chat</b><br>
                User asks follow-up questions like ChatGPT or Gemini.
            </div>

            <div class="card">
                <b>4. Verify</b><br>
                Answers include citations, source chunks, and fusion metrics.
            </div>
        </div>
    </section>

    <section class="features">
        <div class="feature">
            <h3>Document Workspace</h3>
            <p>Upload, select, chat with, and delete documents from a normal user interface.</p>
        </div>

        <div class="feature">
            <h3>GraphRAG Retrieval</h3>
            <p>Combines hybrid retrieval with graph context, graph-guided chunks, and fusion evaluation.</p>
        </div>

        <div class="feature">
            <h3>Professional Demo</h3>
            <p>Includes app UI, GraphRAG console, API docs, health checks, and deployment status.</p>
        </div>
    </section>
</body>
</html>
"""


def get_product_app_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphResearcher App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: #f8fafc;
            color: #111827;
        }

        .app {
            display: grid;
            grid-template-columns: 310px 1fr 350px;
            height: 100vh;
        }

        .sidebar {
            background: #0f172a;
            color: white;
            padding: 16px;
            overflow-y: auto;
        }

        .brand {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 14px;
        }

        .upload-box {
            border: 1px dashed rgba(255,255,255,0.35);
            border-radius: 14px;
            padding: 14px;
            background: rgba(255,255,255,0.06);
            margin-bottom: 18px;
        }

        .upload-box input {
            width: 100%;
            font-size: 12px;
            margin-bottom: 10px;
        }

        button {
            border: none;
            border-radius: 10px;
            padding: 10px 13px;
            cursor: pointer;
            background: #2563eb;
            color: white;
            font-weight: 700;
        }

        button:hover { background: #1d4ed8; }

        button.secondary { background: #334155; }
        button.green { background: #059669; }
        button.red { background: #dc2626; }

        .full {
            width: 100%;
            margin-bottom: 8px;
        }

        .small {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
        }

        .doc-card {
            padding: 12px;
            border-radius: 12px;
            background: rgba(255,255,255,0.07);
            margin-bottom: 9px;
            cursor: pointer;
            border: 1px solid transparent;
        }

        .doc-card.active {
            background: #2563eb;
            border-color: #93c5fd;
        }

        .doc-title {
            font-size: 14px;
            font-weight: 700;
            word-break: break-word;
        }

        .doc-meta {
            font-size: 11px;
            color: #cbd5e1;
            margin-top: 4px;
        }

        .main {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .topbar {
            padding: 14px 20px;
            border-bottom: 1px solid #e5e7eb;
            background: white;
            display: flex;
            justify-content: space-between;
            gap: 14px;
            align-items: center;
        }

        .selected-doc {
            font-weight: 800;
        }

        .selected-doc span {
            display: block;
            color: #64748b;
            font-weight: 500;
            font-size: 12px;
            margin-top: 2px;
        }

        .status-pill {
            font-size: 12px;
            padding: 7px 10px;
            border-radius: 999px;
            background: #e0f2fe;
            color: #075985;
            white-space: nowrap;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }

        .message {
            max-width: 850px;
            margin-bottom: 18px;
            display: flex;
        }

        .message.user {
            margin-left: auto;
            justify-content: flex-end;
        }

        .bubble {
            padding: 14px 16px;
            border-radius: 16px;
            line-height: 1.55;
            white-space: pre-wrap;
        }

        .user .bubble {
            background: #2563eb;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .assistant .bubble {
            background: white;
            border: 1px solid #e5e7eb;
            color: #111827;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        .empty {
            max-width: 700px;
            margin: 70px auto;
            text-align: center;
            color: #475569;
        }

        .empty h1 {
            color: #0f172a;
        }

        .composer {
            padding: 16px 20px;
            background: white;
            border-top: 1px solid #e5e7eb;
        }

        .composer-box {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        textarea {
            flex: 1;
            resize: none;
            min-height: 54px;
            max-height: 160px;
            padding: 13px;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            font-size: 15px;
        }

        .right-panel {
            background: white;
            border-left: 1px solid #e5e7eb;
            padding: 16px;
            overflow-y: auto;
        }

        .panel-section {
            margin-bottom: 20px;
        }

        .panel-section h3 {
            margin-bottom: 8px;
            font-size: 16px;
        }

        .toggle-row {
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 14px;
        }

        .metric {
            display: inline-block;
            background: #eef2ff;
            color: #3730a3;
            padding: 5px 8px;
            border-radius: 999px;
            font-size: 12px;
            margin: 3px;
        }

        .citation-card {
            border: 1px solid #e5e7eb;
            background: #f8fafc;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 13px;
        }

        .danger-zone {
            border-top: 1px solid #e5e7eb;
            padding-top: 14px;
        }

        @media (max-width: 1050px) {
            .app { grid-template-columns: 280px 1fr; }
            .right-panel { display: none; }
        }

        @media (max-width: 760px) {
            .app { grid-template-columns: 1fr; }
            .sidebar { display: none; }
        }
    </style>
</head>

<body>
<div class="app">

    <aside class="sidebar">
        <div class="brand">GraphResearcher</div>

        <div class="upload-box">
            <b>Upload document</b>
            <p class="small">The app stores document_id internally. Users do not need to see it.</p>
            <input id="fileInput" type="file">
            <button class="full green" onclick="uploadDocument()">Upload & Select</button>
            <button class="full secondary" onclick="refreshDocuments()">Refresh Documents</button>
        </div>

        <div class="small" style="margin-bottom: 8px;">My Documents</div>
        <div id="documentList"></div>

        <hr style="border-color: rgba(255,255,255,0.15); margin: 18px 0;">

        <button class="full secondary" onclick="newChat()">+ New Chat</button>
        <button class="full secondary" onclick="window.open('/','_blank')">Home</button>
        <button class="full secondary" onclick="window.open('/graphrag-demo','_blank')">GraphRAG Console</button>
        <button class="full secondary" onclick="window.open('/docs','_blank')">API Docs</button>
    </aside>

    <main class="main">
        <div class="topbar">
            <div class="selected-doc" id="selectedDocTitle">
                No document selected
                <span>Upload or select a document from the left sidebar.</span>
            </div>
            <span id="appStatus" class="status-pill">Ready</span>
        </div>

        <div id="messages" class="messages"></div>

        <div class="composer">
            <div class="composer-box">
                <textarea id="messageInput" placeholder="Ask anything about the selected document..." onkeydown="handleKeyDown(event)"></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="small" style="margin-top: 8px;">
                Ask naturally. Example: “Summarize this”, “What is the main idea?”, “Explain this simply”.
            </div>
        </div>
    </main>

    <aside class="right-panel">
        <div class="panel-section">
            <h3>Selected Document</h3>
            <div id="docDetails" class="small">No document selected.</div>
        </div>

        <div class="panel-section">
            <h3>GraphRAG Settings</h3>
            <div class="toggle-row">
                <label><input type="checkbox" id="useLLM" checked> Use LLM</label>
                <label><input type="checkbox" id="useReranker" checked> Use reranker</label>
                <label><input type="checkbox" id="useGraph" checked> Use graph context</label>
                <label><input type="checkbox" id="useGraphRetrieval" checked> Use graph retrieval fusion</label>
            </div>
        </div>

        <div class="panel-section">
            <h3>Actions</h3>
            <button class="green" onclick="buildGraph()">Build Graph</button>
            <button class="secondary" onclick="openGraph()">Open Graph</button>
        </div>

        <div class="panel-section">
            <h3>Last Answer Metrics</h3>
            <div id="metricsBox">
                <span class="metric">No answer yet</span>
            </div>
        </div>

        <div class="panel-section">
            <h3>Citations</h3>
            <div id="citationsBox" class="small">Citations will appear here.</div>
        </div>

        <div class="panel-section danger-zone">
            <h3>Danger Zone</h3>
            <button class="red" onclick="deleteSelectedDocument()">Delete Selected Document</button>
            <p class="small">This removes it from this app workspace and also tries backend delete if available.</p>
        </div>
    </aside>
</div>

<script>
let documents = JSON.parse(localStorage.getItem("graphrag_documents") || "[]");
let selectedDocumentId = localStorage.getItem("graphrag_selected_document_id") || null;
let conversations = JSON.parse(localStorage.getItem("graphrag_conversations_v2") || "{}");

function saveDocuments() {
    localStorage.setItem("graphrag_documents", JSON.stringify(documents));
    if (selectedDocumentId) {
        localStorage.setItem("graphrag_selected_document_id", selectedDocumentId);
    }
}

function saveConversations() {
    localStorage.setItem("graphrag_conversations_v2", JSON.stringify(conversations));
}

function setStatus(text) {
    document.getElementById("appStatus").textContent = text;
}

function getSelectedDocument() {
    return documents.find(d => d.id === selectedDocumentId) || null;
}

function parseDocumentId(data) {
    return (
        data.document_id ||
        data.id ||
        data.doc_id ||
        data.documentId ||
        data.document?.document_id ||
        data.document?.id ||
        data.file?.document_id ||
        data.result?.document_id ||
        data.data?.document_id
    );
}

async function tryEndpoints(candidates, optionsFactory) {
    let lastError = null;

    for (const candidate of candidates) {
        try {
            const options = optionsFactory(candidate);
            const response = await fetch(candidate, options);
            const contentType = response.headers.get("content-type") || "";
            const data = contentType.includes("application/json") ? await response.json() : await response.text();

            if (response.ok) {
                return {
                    ok: true,
                    endpoint: candidate,
                    data: data
                };
            }

            lastError = {
                endpoint: candidate,
                status: response.status,
                data: data
            };

        } catch (error) {
            lastError = {
                endpoint: candidate,
                error: error.message
            };
        }
    }

    return {
        ok: false,
        error: lastError
    };
}

function renderDocuments() {
    const list = document.getElementById("documentList");
    list.innerHTML = "";

    if (documents.length === 0) {
        list.innerHTML = `<div class="small">No documents yet. Upload one above.</div>`;
    }

    documents.forEach(doc => {
        const div = document.createElement("div");
        div.className = "doc-card" + (doc.id === selectedDocumentId ? " active" : "");
        div.onclick = () => selectDocument(doc.id);

        div.innerHTML = `
            <div class="doc-title">${doc.name || "Untitled document"}</div>
            <div class="doc-meta">${doc.status || "uploaded"} • ${doc.graphStatus || "graph not built"}</div>
        `;

        list.appendChild(div);
    });

    renderSelectedDocument();
}

function renderSelectedDocument() {
    const doc = getSelectedDocument();
    const title = document.getElementById("selectedDocTitle");
    const details = document.getElementById("docDetails");

    if (!doc) {
        title.innerHTML = `No document selected <span>Upload or select a document from the left sidebar.</span>`;
        details.textContent = "No document selected.";
        renderMessages();
        return;
    }

    title.innerHTML = `${doc.name || "Untitled document"} <span>Ready for document chat. Internal ID is hidden from normal workflow.</span>`;

    details.innerHTML = `
        <b>Name:</b> ${doc.name || "Untitled"}<br>
        <b>Status:</b> ${doc.status || "uploaded"}<br>
        <b>Graph:</b> ${doc.graphStatus || "not built"}<br>
        <b>Uploaded:</b> ${doc.uploadedAt || "unknown"}<br>
        <details style="margin-top:8px;">
            <summary>Developer details</summary>
            <code>${doc.id}</code>
        </details>
    `;

    renderMessages();
}

function selectDocument(id) {
    selectedDocumentId = id;
    saveDocuments();
    renderDocuments();
}

function newChat() {
    if (!selectedDocumentId) {
        alert("Select a document first.");
        return;
    }

    conversations[selectedDocumentId] = [];
    saveConversations();
    renderMessages();
}

function getConversation() {
    if (!selectedDocumentId) return [];

    if (!conversations[selectedDocumentId]) {
        conversations[selectedDocumentId] = [];
    }

    return conversations[selectedDocumentId];
}

function renderMessages() {
    const box = document.getElementById("messages");
    const doc = getSelectedDocument();

    if (!doc) {
        box.innerHTML = `
            <div class="empty">
                <h1>Upload a document to start</h1>
                <p>No document ID needed. Upload a file from the left sidebar, then start chatting normally.</p>
            </div>
        `;
        return;
    }

    const convo = getConversation();

    if (convo.length === 0) {
        box.innerHTML = `
            <div class="empty">
                <h1>Chat with ${doc.name || "your document"}</h1>
                <p>Ask a question below. The app will use GraphRAG, citations, and retrieval fusion automatically.</p>
            </div>
        `;
        return;
    }

    box.innerHTML = "";

    convo.forEach(msg => {
        const wrapper = document.createElement("div");
        wrapper.className = "message " + msg.role;

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = msg.content;

        wrapper.appendChild(bubble);
        box.appendChild(wrapper);
    });

    box.scrollTop = box.scrollHeight;
}

async function uploadDocument() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Choose a file first.");
        return;
    }

    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    const uploadCandidates = [
        "/documents/upload",
        "/upload",
        "/documents",
        "/api/documents/upload"
    ];

    const result = await tryEndpoints(
        uploadCandidates,
        () => ({
            method: "POST",
            body: formData
        })
    );

    if (!result.ok) {
        setStatus("Upload failed");
        alert("Upload failed. Open /docs and check the exact upload endpoint. Error: " + JSON.stringify(result.error));
        return;
    }

    const documentId = parseDocumentId(result.data);

    if (!documentId) {
        setStatus("Upload returned no document_id");
        alert("Upload worked but document_id was not found in response: " + JSON.stringify(result.data).slice(0, 600));
        return;
    }

    const doc = {
        id: documentId,
        name: file.name,
        status: "uploaded",
        graphStatus: "not built",
        uploadedAt: new Date().toLocaleString(),
        uploadEndpoint: result.endpoint
    };

    const existingIndex = documents.findIndex(d => d.id === documentId);

    if (existingIndex >= 0) {
        documents[existingIndex] = doc;
    } else {
        documents.unshift(doc);
    }

    selectedDocumentId = documentId;
    saveDocuments();
    renderDocuments();

    setStatus("Uploaded");

    await autoIndexDocument(documentId);
    await buildGraph(true);
}

async function autoIndexDocument(documentId) {
    setStatus("Indexing...");

    const indexCandidates = [
        `/documents/${documentId}/index`,
        `/documents/${documentId}/process`,
        `/documents/${documentId}/ingest`,
        `/index/${documentId}`
    ];

    const result = await tryEndpoints(
        indexCandidates,
        () => ({
            method: "POST"
        })
    );

    const doc = documents.find(d => d.id === documentId);

    if (doc) {
        if (result.ok) {
            doc.status = "indexed";
            doc.indexEndpoint = result.endpoint;
        } else {
            doc.status = "uploaded";
            doc.indexWarning = result.error;
        }

        saveDocuments();
        renderDocuments();
    }

    setStatus(result.ok ? "Indexed" : "Uploaded");
}

async function buildGraph(silent = false) {
    const doc = getSelectedDocument();

    if (!doc) {
        if (!silent) alert("Select a document first.");
        return;
    }

    setStatus("Building graph...");

    try {
        const response = await fetch(`/documents/${doc.id}/graph/build`, {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        doc.graphStatus = "graph built";
        doc.graphData = {
            entities: data.total_entities ?? data.entity_count ?? null,
            relations: data.total_relations ?? data.relation_count ?? null
        };

        saveDocuments();
        renderDocuments();

        document.getElementById("metricsBox").innerHTML = `
            <span class="metric">graph built</span>
            <span class="metric">entities: ${doc.graphData.entities ?? "NA"}</span>
            <span class="metric">relations: ${doc.graphData.relations ?? "NA"}</span>
        `;

        setStatus("Graph ready");

    } catch (error) {
        doc.graphStatus = "graph not built";
        saveDocuments();
        renderDocuments();

        setStatus("Graph skipped");
        if (!silent) alert("Graph build failed: " + error.message);
    }
}

function openGraph() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert("Select a document first.");
        return;
    }

    window.open(`/documents/${doc.id}/graph/view`, "_blank");
}

async function deleteSelectedDocument() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert("Select a document first.");
        return;
    }

    const confirmDelete = confirm(`Delete "${doc.name}" from this workspace?`);

    if (!confirmDelete) return;

    setStatus("Deleting...");

    const deleteCandidates = [
        `/documents/${doc.id}`,
        `/documents/${doc.id}/delete`,
        `/api/documents/${doc.id}`
    ];

    await tryEndpoints(
        deleteCandidates,
        () => ({
            method: "DELETE"
        })
    );

    documents = documents.filter(d => d.id !== doc.id);
    delete conversations[doc.id];

    selectedDocumentId = documents.length > 0 ? documents[0].id : null;

    saveDocuments();
    saveConversations();
    renderDocuments();
    renderMessages();

    setStatus("Deleted");
}

function refreshDocuments() {
    renderDocuments();
    setStatus("Refreshed");
}

function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function buildContextualQuery(currentQuestion) {
    const convo = getConversation().slice(-6);

    if (convo.length === 0) {
        return currentQuestion;
    }

    const context = convo
        .map(m => `${m.role}: ${m.content}`)
        .join("\\n");

    return `Conversation so far:\\n${context}\\n\\nCurrent user question:\\n${currentQuestion}`;
}

function updateMetrics(data) {
    const fusion = data.retrieval_fusion || {};
    const graph = data.graph_context || {};

    document.getElementById("metricsBox").innerHTML = `
        <span class="metric">strategy: ${data.answer_strategy || "NA"}</span>
        <span class="metric">LLM: ${data.used_llm}</span>
        <span class="metric">graph: ${data.graph_used}</span>
        <span class="metric">graph available: ${graph.graph_available}</span>
        <span class="metric">fusion: ${fusion.fusion_used}</span>
        <span class="metric">graph added: ${fusion.graph_added_count ?? "NA"}</span>
        <span class="metric">graph supported: ${fusion.graph_supported_count ?? "NA"}</span>
    `;
}

function updateCitations(data) {
    const citations = data.citations || [];
    const box = document.getElementById("citationsBox");

    if (citations.length === 0) {
        box.textContent = "No citations returned.";
        return;
    }

    box.innerHTML = "";

    citations.forEach((citation, index) => {
        const card = document.createElement("div");
        card.className = "citation-card";

        card.innerHTML = `
            <b>Source ${index + 1}</b><br>
            <span>${citation.source_id || citation.id || "unknown source"}</span><br>
            <span class="small">${citation.text_preview || citation.preview || citation.chunk_preview || ""}</span>
        `;

        box.appendChild(card);
    });
}

async function sendMessage() {
    const doc = getSelectedDocument();
    const input = document.getElementById("messageInput");
    const userText = input.value.trim();

    if (!doc) {
        alert("Upload or select a document first.");
        return;
    }

    if (!userText) return;

    const convo = getConversation();

    convo.push({
        role: "user",
        content: userText,
        createdAt: new Date().toISOString()
    });

    input.value = "";
    saveConversations();
    renderMessages();

    setStatus("Thinking...");

    const payload = {
        query: buildContextualQuery(userText),
        document_id: doc.id,
        top_k: 5,
        retrieval_mode: "hybrid",
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked,
        use_graph: document.getElementById("useGraph").checked,
        graph_entity_limit: 8,
        use_graph_retrieval: document.getElementById("useGraphRetrieval").checked,
        graph_retrieval_top_k: 5
    };

    try {
        const response = await fetch("/ask", {
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

        const answer = data.answer || "I could not generate an answer.";

        convo.push({
            role: "assistant",
            content: answer,
            createdAt: new Date().toISOString(),
            raw: data
        });

        saveConversations();
        renderMessages();
        updateMetrics(data);
        updateCitations(data);

        setStatus("Ready");

    } catch (error) {
        convo.push({
            role: "assistant",
            content: "Error: " + error.message,
            createdAt: new Date().toISOString()
        });

        saveConversations();
        renderMessages();

        setStatus("Error");
    }
}

renderDocuments();
</script>
</body>
</html>
"""
'''
text += new_ui

hf_path.write_text(text, encoding="utf-8")
print("Updated hf_status.py with home UI and improved product app UI.")


# Patch main.py
main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

# Ensure HTMLResponse import
if "HTMLResponse" not in main_text:
    lines = main_text.splitlines()
    inserted = False

    for i, line in enumerate(lines):
        if line.startswith("from fastapi.responses import"):
            lines[i] = line + ", HTMLResponse"
            inserted = True
            break

    if not inserted:
        lines.insert(0, "from fastapi.responses import HTMLResponse")

    main_text = "\n".join(lines) + "\n"

# Ensure get_home_html and get_product_app_html import
if "get_home_html" not in main_text:
    main_text = "from app.deployment.hf_status import get_home_html, get_product_app_html\n" + main_text
elif "get_product_app_html" not in main_text:
    main_text = "from app.deployment.hf_status import get_product_app_html\n" + main_text

# Replace existing root route if present
root_replacement = '''@app.get("/", response_class=HTMLResponse)
def home_page():
    return get_home_html()
'''

pattern = re.compile(
    r'@app\.get\(\s*["\\\']/["\\\'][^\n]*\)\s*\n(?:async\s+)?def\s+\w+\([^)]*\):\s*\n(?:    .*(?:\n|$))+',
    re.MULTILINE
)

if '@app.get("/")' in main_text or '@app.get("/",' in main_text or "@app.get('/')" in main_text:
    main_text = pattern.sub(root_replacement + "\n", main_text, count=1)
    print("Replaced existing / route with home UI.")
else:
    main_text += "\n\n" + root_replacement
    print("Added / route with home UI.")

# Add /app route if missing
if '# Improved product workspace app endpoint' not in main_text:
    main_text += '''

# Improved product workspace app endpoint

@app.get("/app", response_class=HTMLResponse)
def product_workspace_app_page():
    return get_product_app_html()
'''
    print("Added /app product workspace route.")
else:
    print("/app route already exists.")

main_path.write_text(main_text, encoding="utf-8")
print("Phase 26 patch complete.")
