
def get_home_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphResearcher</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; font-family: Inter, Arial, sans-serif; background: #f8fafc; color: #0f172a; }
        .nav { height: 72px; display: flex; align-items: center; justify-content: space-between; padding: 0 56px; background: white; border-bottom: 1px solid #e5e7eb; }
        .brand { font-weight: 900; font-size: 24px; letter-spacing: -0.7px; }
        .nav a { text-decoration: none; color: #334155; margin-left: 22px; font-weight: 800; }
        .hero { min-height: calc(100vh - 72px); display: grid; grid-template-columns: 1fr 0.9fr; gap: 52px; align-items: center; padding: 64px 72px; }
        .badge { display: inline-block; background: #dbeafe; color: #1d4ed8; padding: 8px 12px; border-radius: 999px; font-weight: 900; font-size: 13px; margin-bottom: 18px; }
        h1 { font-size: 58px; line-height: 1.04; margin: 0 0 20px; letter-spacing: -2px; }
        p { font-size: 19px; line-height: 1.7; color: #475569; max-width: 720px; }
        .actions { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 32px; }
        .btn { display: inline-block; text-decoration: none; background: #2563eb; color: white; padding: 14px 22px; border-radius: 12px; font-weight: 900; }
        .btn.dark { background: #0f172a; }
        .preview { background: #0f172a; color: white; border-radius: 26px; padding: 24px; box-shadow: 0 28px 70px rgba(15,23,42,0.24); }
        .preview-card { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 16px; margin-bottom: 14px; line-height: 1.55; }
        .preview-card b { color: #bfdbfe; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; padding: 0 72px 58px; }
        .feature { background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 24px; }
        .feature p { font-size: 15px; color: #64748b; }
        @media(max-width: 950px) {
            .nav { padding: 0 22px; }
            .hero { grid-template-columns: 1fr; padding: 42px 24px; }
            h1 { font-size: 42px; }
            .features { grid-template-columns: 1fr; padding: 0 24px 44px; }
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="brand">GraphResearcher</div>
        <div><a href="/app">Launch App</a></div>
    </div>

    <section class="hero">
        <div>
            <div class="badge">Document Chat + GraphRAG</div>
            <h1>Upload documents. Ask questions. Verify every answer.</h1>
            <p>
                GraphResearcher lets users chat with PDFs and reports using citation-grounded retrieval,
                graph context, source verification, graph view, and document comparison.
            </p>
            <div class="actions">
                <a class="btn" href="/app">Start Chatting</a>
                <a class="btn dark" href="/login">Login</a>
            </div>
        </div>

        <div class="preview">
            <div class="preview-card"><b>1. Upload</b><br>Add a document from the app sidebar. No document ID needed.</div>
            <div class="preview-card"><b>2. Chat</b><br>Ask natural questions and get source-backed answers.</div>
            <div class="preview-card"><b>3. Verify</b><br>Open sources, see page/chunk metadata, and inspect the graph.</div>
            <div class="preview-card"><b>4. Compare</b><br>Select a second document and compare them side by side.</div>
        </div>
    </section>

    <section class="features">
        <div class="feature"><h3>Simple workspace</h3><p>Upload, select, delete, and re-index documents from one clean UI.</p></div>
        <div class="feature"><h3>Grounded answers</h3><p>Answers show evidence boxes and source cards for verification.</p></div>
        <div class="feature"><h3>GraphRAG inside</h3><p>Graph view and graph retrieval stay available without exposing developer tools.</p></div>
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
        body { margin: 0; font-family: Inter, Arial, sans-serif; background: #f8fafc; color: #111827; }
        .app { display: grid; grid-template-columns: 310px 1fr 370px; height: 100vh; }
        .sidebar { background: #0f172a; color: white; padding: 18px; overflow-y: auto; }
        .brand { font-size: 24px; font-weight: 900; margin-bottom: 18px; letter-spacing: -0.7px; }
        .upload-box { border: 1px dashed rgba(255,255,255,0.35); border-radius: 16px; padding: 14px; background: rgba(255,255,255,0.06); margin-bottom: 20px; }
        .upload-box input { width: 100%; font-size: 12px; margin: 10px 0; }
        button { border: none; border-radius: 10px; padding: 10px 13px; cursor: pointer; background: #2563eb; color: white; font-weight: 800; }
        button:hover { background: #1d4ed8; }
        button.secondary { background: #334155; }
        button.green { background: #059669; }
        button.red { background: #dc2626; }
        button.light { background: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1; }
        .full { width: 100%; margin-bottom: 9px; }
        .small { font-size: 12px; color: #94a3b8; line-height: 1.5; }
        .doc-card { padding: 12px; border-radius: 13px; background: rgba(255,255,255,0.07); margin-bottom: 9px; cursor: pointer; border: 1px solid transparent; }
        .doc-card.active { background: #2563eb; border-color: #93c5fd; }
        .doc-title { font-size: 14px; font-weight: 800; word-break: break-word; }
        .doc-meta { font-size: 11px; color: #cbd5e1; margin-top: 4px; }
        .main { display: flex; flex-direction: column; height: 100vh; }
        .topbar { padding: 14px 20px; border-bottom: 1px solid #e5e7eb; background: white; display: flex; justify-content: space-between; gap: 14px; align-items: center; }
        .selected-doc { font-weight: 900; font-size: 17px; }
        .selected-doc span { display: block; color: #64748b; font-weight: 500; font-size: 12px; margin-top: 2px; }
        .status-pill { font-size: 12px; padding: 7px 10px; border-radius: 999px; background: #e0f2fe; color: #075985; white-space: nowrap; font-weight: 800; }
        .messages { flex: 1; overflow-y: auto; padding: 26px; }
        .message { max-width: 940px; margin-bottom: 18px; display: flex; }
        .message.user { margin-left: auto; justify-content: flex-end; }
        .bubble { padding: 15px 17px; border-radius: 17px; line-height: 1.65; white-space: pre-wrap; font-size: 15.5px; }
        .user .bubble { background: #2563eb; color: white; border-bottom-right-radius: 4px; }
        .assistant .bubble { background: white; border: 1px solid #e5e7eb; color: #111827; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
        .empty { max-width: 760px; margin: 70px auto; text-align: center; color: #475569; }
        .empty h1 { color: #0f172a; }
        .composer { padding: 16px 20px; background: white; border-top: 1px solid #e5e7eb; }
        .composer-box { display: flex; gap: 10px; align-items: flex-end; }
        textarea { flex: 1; resize: none; min-height: 54px; max-height: 160px; padding: 13px; border: 1px solid #cbd5e1; border-radius: 12px; font-size: 15px; }
        select { width: 100%; padding: 9px; border-radius: 9px; border: 1px solid #cbd5e1; background: white; }
        .right-panel { background: white; border-left: 1px solid #e5e7eb; padding: 16px; overflow-y: auto; }
        .panel-section { margin-bottom: 20px; }
        .panel-section h3 { margin-bottom: 8px; font-size: 16px; }
        .toggle-row { display: flex; flex-direction: column; gap: 8px; font-size: 14px; }
        .metric { display: inline-block; background: #eef2ff; color: #3730a3; padding: 5px 8px; border-radius: 999px; font-size: 12px; margin: 3px; }
        .citation-card { border: 1px solid #e5e7eb; background: #f8fafc; border-radius: 12px; padding: 12px; margin-bottom: 11px; font-size: 13px; }
        .source-line { margin-top: 5px; color: #475569; }
        .preview-text { margin-top: 8px; color: #64748b; font-size: 12px; line-height: 1.5; }
        .answer-card { line-height: 1.72; }
        .answer-card h2 { margin: 0 0 10px; font-size: 18px; color: #0f172a; }
        .answer-card h3 { margin: 18px 0 8px; font-size: 15px; color: #1d4ed8; }
        .answer-card p { margin: 8px 0; }
        .evidence-box { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 12px; padding: 11px; margin-top: 9px; font-size: 13px; color: #475569; }
        .source-chip { display: inline-block; background: #eef2ff; color: #3730a3; padding: 3px 7px; border-radius: 999px; font-size: 12px; margin: 2px; font-weight: 700; }
        .warning { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; padding: 10px; border-radius: 12px; margin: 10px 0; }
        .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 12px; }
        .compare-card { border: 1px solid #e5e7eb; background: #f8fafc; border-radius: 14px; padding: 14px; line-height: 1.6; }
        .danger-zone { border-top: 1px solid #e5e7eb; padding-top: 14px; }
        @media (max-width: 1150px) { .app { grid-template-columns: 290px 1fr; } .right-panel { display: none; } }
        @media (max-width: 850px) { .compare-grid { grid-template-columns: 1fr; } }
        @media (max-width: 760px) { .app { grid-template-columns: 1fr; } .sidebar { display: none; } }
    </style>
</head>

<body>
<div class="app">
    <aside class="sidebar">
        <div class="brand">GraphResearcher</div>

        <div class="upload-box">
            <b>Upload document</b>
            <p class="small">Upload, select, and chat. If Hugging Face rebuilt recently, clear cache and re-upload.</p>
            <input id="fileInput" type="file">
            <button class="full green" onclick="uploadDocument()">Upload & Select</button>
            <button class="full secondary" onclick="refreshDocuments()">Refresh Documents</button>
        </div>

        <div class="small" style="margin-bottom:8px;">My Documents</div>
        <div id="documentList"></div>

        <hr style="border-color:rgba(255,255,255,0.15); margin:18px 0;">

        <button class="full secondary" onclick="newChat()">+ New Chat</button>
        <button class="full secondary" onclick="reindexSelectedDocument()">Re-index Selected</button>
        <button class="full secondary" onclick="buildGraph()">Build / Rebuild Graph</button>
        <button class="full secondary" onclick="openGraphViewer()">View Graph</button>
        <button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>
        <button class="full secondary" onclick="window.location.href='/'">Home</button>
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
                <textarea id="messageInput" placeholder="Ask about the selected document..." onkeydown="handleKeyDown(event)"></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="small" style="margin-top:8px;color:#64748b;">
                Tip: choose a second document in the right panel to compare two documents.
            </div>
        </div>
    </main>

    <aside class="right-panel">
        <div class="panel-section">
            <h3>Selected Document</h3>
            <div id="docDetails" class="small" style="color:#64748b;">No document selected.</div>
        </div>

        <div class="panel-section">
            <h3>Compare With</h3>
            <select id="compareDocumentSelect" onchange="renderSelectedDocument()">
                <option value="">No comparison</option>
            </select>
            <p class="small" style="color:#64748b;">Choose another document for side-by-side comparison.</p>
        </div>

        <div class="panel-section">
            <h3>Graph</h3>
            <button class="green" onclick="buildGraph()">Build / Rebuild Graph</button>
            <button class="secondary" onclick="openGraphViewer()">View Graph</button>
        </div>

        <div class="panel-section">
            <h3>Answer Style</h3>
            <select id="answerStyle">
                <option value="detailed" selected>Detailed</option>
                <option value="step_by_step">Step-by-step</option>
                <option value="concise">Concise</option>
                <option value="research">Research style</option>
                <option value="comparison">Comparison focused</option>
            </select>
        </div>

        <div class="panel-section">
            <h3>Advanced Settings</h3>
            <div class="toggle-row">
                <label><input type="checkbox" id="useLLM" checked> Use LLM</label>
                <label><input type="checkbox" id="useReranker" checked> Use reranker</label>
                <label><input type="checkbox" id="useGraph" checked> Use graph context</label>
                <label><input type="checkbox" id="useGraphRetrieval" checked> Use graph retrieval fusion</label>
            </div>
        </div>

        <div class="panel-section">
            <h3>Last Answer Metrics</h3>
            <div id="metricsBox"><span class="metric">No answer yet</span></div>
        </div>

        <div class="panel-section">
            <h3>Sources</h3>
            <div id="citationsBox" class="small" style="color:#64748b;">Sources will appear here after an answer.</div>
        </div>

        
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

        <div class="panel-section danger-zone">
            <h3>Danger Zone</h3>
            <button class="red" onclick="deleteSelectedDocument()">Delete Selected Document</button>
        </div>
    </aside>
</div>

<script>
let documents = JSON.parse(localStorage.getItem("graphrag_documents") || "[]");
let selectedDocumentId = localStorage.getItem("graphrag_selected_document_id") || null;
let conversations = JSON.parse(localStorage.getItem("graphrag_final_conversations") || "{}");
let lastSources = [];

function saveDocuments() {
    localStorage.setItem("graphrag_documents", JSON.stringify(documents));
    if (selectedDocumentId) localStorage.setItem("graphrag_selected_document_id", selectedDocumentId);
}
function saveConversations() { localStorage.setItem("graphrag_final_conversations", JSON.stringify(conversations)); }
function setStatus(text) { document.getElementById("appStatus").textContent = text; }
function getSelectedDocument() { return documents.find(d => d.id === selectedDocumentId) || null; }
function getCompareDocument() {
    const id = document.getElementById("compareDocumentSelect")?.value || "";
    if (!id) return null;
    return documents.find(d => d.id === id) || null;
}
function escapeHtml(value) {
    return String(value || "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
}
function parseDocumentId(data) {
    return data.document_id || data.id || data.doc_id || data.documentId ||
           data.document?.document_id || data.document?.id ||
           data.file?.document_id || data.result?.document_id || data.data?.document_id;
}
async function tryEndpoints(candidates, optionsFactory) {
    let lastError = null;
    for (const candidate of candidates) {
        try {
            const response = await fetch(candidate, optionsFactory(candidate));
            const contentType = response.headers.get("content-type") || "";
            const data = contentType.includes("application/json") ? await response.json() : await response.text();
            if (response.ok) return { ok: true, endpoint: candidate, data };
            lastError = { endpoint: candidate, status: response.status, data };
        } catch (error) {
            lastError = { endpoint: candidate, error: error.message };
        }
    }
    return { ok: false, error: lastError };
}

function renderDocuments() {
    const list = document.getElementById("documentList");
    list.innerHTML = "";

    if (documents.length === 0) list.innerHTML = `<div class="small">No documents yet. Upload one above.</div>`;

    documents.forEach(doc => {
        const div = document.createElement("div");
        div.className = "doc-card" + (doc.id === selectedDocumentId ? " active" : "");
        div.onclick = () => selectDocument(doc.id);
        div.innerHTML = `<div class="doc-title">${escapeHtml(doc.name || "Untitled document")}</div>
                         <div class="doc-meta">${escapeHtml(doc.status || "uploaded")} • ${escapeHtml(doc.graphStatus || "graph not built")}</div>`;
        list.appendChild(div);
    });

    renderCompareDropdown();
    renderSelectedDocument();
}
function renderCompareDropdown() {
    const select = document.getElementById("compareDocumentSelect");
    if (!select) return;

    const oldValue = select.value;
    select.innerHTML = `<option value="">No comparison</option>`;

    documents.filter(d => d.id !== selectedDocumentId).forEach(doc => {
        const option = document.createElement("option");
        option.value = doc.id;
        option.textContent = doc.name || "Untitled document";
        select.appendChild(option);
    });

    if ([...select.options].some(o => o.value === oldValue)) select.value = oldValue;
}
function renderSelectedDocument() {
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument();
    const title = document.getElementById("selectedDocTitle");
    const details = document.getElementById("docDetails");

    if (!doc) {
        title.innerHTML = `No document selected <span>Upload or select a document from the left sidebar.</span>`;
        details.textContent = "No document selected.";
        renderMessages();
        return;
    }

    const subtitle = compareDoc ? `Compare mode active with ${compareDoc.name || "second document"}.` : "Ready for document chat.";
    title.innerHTML = `${escapeHtml(doc.name || "Untitled document")} <span>${escapeHtml(subtitle)}</span>`;
    details.innerHTML = `<b>Name:</b> ${escapeHtml(doc.name || "Untitled")}<br>
                         <b>Status:</b> ${escapeHtml(doc.status || "uploaded")}<br>
                         <b>Graph:</b> ${escapeHtml(doc.graphStatus || "not built")}<br>
                         <b>Uploaded:</b> ${escapeHtml(doc.uploadedAt || "unknown")}
                         ${compareDoc ? `<br><br><b>Comparing with:</b> ${escapeHtml(compareDoc.name || "Untitled")}` : ""}`;
    renderMessages();
}
function selectDocument(id) {
    selectedDocumentId = id;
    saveDocuments();
    renderDocuments();
}
function getConversationKey() {
    const compareDoc = getCompareDocument();
    if (compareDoc) return `${selectedDocumentId}__compare__${compareDoc.id}`;
    return selectedDocumentId || "default";
}
function getConversation() {
    const key = getConversationKey();
    if (!conversations[key]) conversations[key] = [];
    return conversations[key];
}
function newChat() {
    if (!selectedDocumentId) return alert("Select a document first.");
    conversations[getConversationKey()] = [];
    saveConversations();
    renderMessages();
}
function renderMessages() {
    const box = document.getElementById("messages");
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument();

    if (!doc) {
        box.innerHTML = `<div class="empty"><h1>Upload a document to start</h1><p>No document ID needed. Upload a file from the left sidebar, then chat normally.</p></div>`;
        return;
    }

    const convo = getConversation();
    if (convo.length === 0) {
        box.innerHTML = `<div class="empty"><h1>${compareDoc ? "Compare documents" : "Chat with your document"}</h1>
                         <p>${compareDoc ? `You are comparing ${escapeHtml(doc.name)} with ${escapeHtml(compareDoc.name)}.` : `Ask a question about ${escapeHtml(doc.name)}.`}</p></div>`;
        return;
    }

    box.innerHTML = "";
    convo.forEach(msg => {
        const wrapper = document.createElement("div");
        wrapper.className = "message " + msg.role;

        const bubble = document.createElement("div");
        bubble.className = msg.type === "compare" ? "bubble" : "bubble";

        if (msg.role === "assistant" && msg.html) bubble.innerHTML = msg.html;
        else bubble.textContent = msg.content || "";

        wrapper.appendChild(bubble);
        box.appendChild(wrapper);
    });

    box.scrollTop = box.scrollHeight;
}

async function uploadDocument() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return alert("Choose a file first.");

    setStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);

    const result = await tryEndpoints(["/documents/upload", "/upload", "/documents", "/api/documents/upload"], () => ({ method: "POST", body: formData }));
    if (!result.ok) {
        setStatus("Upload failed");
        return alert("Upload failed: " + JSON.stringify(result.error));
    }

    const documentId = parseDocumentId(result.data);
    if (!documentId) {
        setStatus("Upload returned no document ID");
        return alert("Upload worked but document ID was not found in response.");
    }

    const doc = { id: documentId, name: file.name, status: "uploaded", graphStatus: "not built", uploadedAt: new Date().toLocaleString() };
    const index = documents.findIndex(d => d.id === documentId);
    if (index >= 0) documents[index] = doc;
    else documents.unshift(doc);

    selectedDocumentId = documentId;
    saveDocuments();
    renderDocuments();

    setStatus("Uploaded");
    await autoIndexDocument(documentId);
    await buildGraph(true);
}
async function autoIndexDocument(documentId) {
    setStatus("Indexing...");
    const result = await tryEndpoints([`/documents/${documentId}/index`, `/documents/${documentId}/process`, `/documents/${documentId}/ingest`, `/index/${documentId}`], () => ({ method: "POST" }));
    const doc = documents.find(d => d.id === documentId);
    if (doc) {
        doc.status = result.ok ? "indexed" : "uploaded";
        saveDocuments();
        renderDocuments();
    }
    setStatus(result.ok ? "Indexed" : "Uploaded");
}
async function reindexSelectedDocument() {
    const doc = getSelectedDocument();
    if (!doc) return alert("Select a document first.");
    await autoIndexDocument(doc.id);
    await buildGraph(false);
    alert("Re-index attempt complete. Ask again now.");
}
async function buildGraph(silent = false) {
    const doc = getSelectedDocument();
    if (!doc) {
        if (!silent) alert("Select a document first.");
        return;
    }

    setStatus("Building graph...");
    try {
        const response = await fetch(`/documents/${doc.id}/graph/build`, { method: "POST" });
        const data = await response.json();
        if (!response.ok) throw new Error(JSON.stringify(data));

        doc.graphStatus = "graph built";
        doc.graphData = { entities: data.total_entities ?? data.entity_count ?? null, relations: data.total_relations ?? data.relation_count ?? null };
        saveDocuments();
        renderDocuments();

        document.getElementById("metricsBox").innerHTML = `<span class="metric">graph built</span>
            <span class="metric">entities: ${doc.graphData.entities ?? "NA"}</span>
            <span class="metric">relations: ${doc.graphData.relations ?? "NA"}</span>`;

        setStatus("Graph ready");
    } catch (error) {
        doc.graphStatus = "graph not built";
        saveDocuments();
        renderDocuments();
        setStatus("Graph skipped");
        if (!silent) alert("Graph build failed. Re-index or re-upload if needed.");
    }
}
function openGraphViewer() {
    const doc = getSelectedDocument();
    if (!doc) return alert("Select a document first.");
    window.open(`/documents/${doc.id}/graph/view`, "_blank");
}
async function deleteSelectedDocument() {
    const doc = getSelectedDocument();
    if (!doc) return alert("Select a document first.");
    if (!confirm(`Delete "${doc.name}"?`)) return;

    setStatus("Deleting...");
    await tryEndpoints([`/documents/${doc.id}/delete`, `/documents/${doc.id}`, `/api/documents/${doc.id}`], () => ({ method: "DELETE" }));

    documents = documents.filter(d => d.id !== doc.id);
    Object.keys(conversations).forEach(k => { if (k.includes(doc.id)) delete conversations[k]; });
    selectedDocumentId = documents.length ? documents[0].id : null;
    saveDocuments();
    saveConversations();
    renderDocuments();
    renderMessages();
    setStatus("Deleted");
}
function clearWorkspaceCache() {
    if (!confirm("Clear browser document list and chat history? Use this after Hugging Face rebuilds.")) return;
    ["graphrag_documents", "graphrag_selected_document_id", "graphrag_conversations", "graphrag_conversations_v2", "graphrag_conversations_v3", "graphrag_final_conversations"].forEach(k => localStorage.removeItem(k));
    documents = [];
    selectedDocumentId = null;
    conversations = {};
    renderDocuments();
    renderMessages();
    setStatus("Cache cleared");
}
function refreshDocuments() { renderDocuments(); setStatus("Refreshed"); }
function handleKeyDown(event) { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }

function buildContextualQuery(currentQuestion) {
    const clean = String(currentQuestion || "").trim();
    if (!clean) return clean;

    const wordCount = clean.split(/\\s+/).filter(Boolean).length;
    if (wordCount <= 8) {
        const prev = getConversation().filter(m => m.role === "user").slice(-2).map(m => m.content).join(" ");
        return prev ? prev + " " + clean : clean;
    }
    return clean;
}
function askPayload(query, documentId) {
    return {
        query,
        document_id: documentId,
        top_k: 8,
        retrieval_mode: "hybrid",
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked,
        use_graph: document.getElementById("useGraph").checked,
        graph_entity_limit: 12,
        use_graph_retrieval: document.getElementById("useGraphRetrieval").checked,
        graph_retrieval_top_k: 6
    };
}
async function callAsk(payload) {
    const response = await fetch("/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data));
    return data;
}
function valueFrom(obj, keys, fallback = "Not available") {
    for (const key of keys) if (obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== "") return obj[key];
    if (obj && obj.metadata) for (const key of keys) if (obj.metadata[key] !== undefined && obj.metadata[key] !== null && obj.metadata[key] !== "") return obj.metadata[key];
    return fallback;
}
function buildSources(data, doc) {
    const sources = [];
    (data.citations || []).forEach(x => sources.push(x));
    (data.retrieval_fusion?.fused_results || []).forEach(x => sources.push(x));
    (data.sources || data.source_chunks || data.retrieved_sources || []).forEach(x => sources.push(x));

    const cleaned = [];
    const seen = new Set();

    sources.forEach((src, i) => {
        const sid = valueFrom(src, ["source_id", "id", "citation_id"], "S" + (i + 1));
        const chunk = valueFrom(src, ["chunk_id", "source_chunk_id", "chunk"], sid);
        const page = valueFrom(src, ["page_number", "page", "page_no"], "Not available");
        const key = doc.id + "|" + sid + "|" + chunk + "|" + page;
        if (seen.has(key)) return;
        seen.add(key);

        cleaned.push({
            source_id: sid,
            document_id: doc.id,
            document_name: valueFrom(src, ["document_name", "source_file_name", "file_name", "filename", "document_title"], doc.name || "Selected document"),
            page,
            chunk_id: chunk,
            preview: valueFrom(src, ["text_preview", "preview", "chunk_preview", "content_preview", "text", "content"], "Preview not available"),
            raw: src
        });
    });

    return cleaned.slice(0, 8);
}
function updateCitations(groups) {
    const box = document.getElementById("citationsBox");
    lastSources = [];
    box.innerHTML = "";

    groups.forEach(group => {
        const h = document.createElement("div");
        h.innerHTML = `<h4>${escapeHtml(group.label)}</h4>`;
        box.appendChild(h);

        group.sources.forEach(src => {
            const idx = lastSources.length;
            lastSources.push(src);
            const card = document.createElement("div");
            card.className = "citation-card";
            card.innerHTML = `<b>Source ${idx + 1}: ${escapeHtml(src.source_id)}</b>
                <div class="source-line"><b>Document:</b> ${escapeHtml(src.document_name)}</div>
                <div class="source-line"><b>Page:</b> ${escapeHtml(src.page)}</div>
                <div class="source-line"><b>Chunk:</b> ${escapeHtml(src.chunk_id)}</div>
                <div class="preview-text">${escapeHtml(String(src.preview).slice(0, 260))}</div><br>
                <button class="light" onclick="openSource(${idx})">Open source</button>`;
            box.appendChild(card);
        });
    });

    if (!lastSources.length) box.textContent = "No source details returned.";
}
function openSource(index) {
    const src = lastSources[index];
    if (!src) return;
    window.open(`/documents/${src.document_id}/sources/${encodeURIComponent(src.source_id)}/view?page=${encodeURIComponent(src.page || "")}&chunk_id=${encodeURIComponent(src.chunk_id || "")}`, "_blank");
}
function updateMetrics(data, label) {
    const fusion = data.retrieval_fusion || {};
    const graph = data.graph_context || {};
    document.getElementById("metricsBox").innerHTML += `<div style="margin-bottom:8px;"><b>${escapeHtml(label || "")}</b><br>
        <span class="metric">strategy: ${escapeHtml(data.answer_strategy || "NA")}</span>
        <span class="metric">LLM: ${data.used_llm}</span>
        <span class="metric">graph: ${data.graph_used}</span>
        <span class="metric">graph available: ${graph.graph_available}</span>
        <span class="metric">fusion: ${fusion.fusion_used}</span></div>`;
}
function answerLooksWeak(answer) {
    const words = String(answer || "").split(/\\s+/).filter(Boolean);
    return words.length < 100;
}
function cleanMainAnswerText(answer) {
    let text = String(answer || "").trim();

    // Remove noisy source markers from the visible chat answer.
    text = text.replace(/\[S\d+\]/g, "");
    text = text.replace(/\s+\|\s*[^|\\n]*page\s*\d+/gi, "");
    text = text.replace(/Vectorless_RAG_Master_Guide\.pdf/gi, "");

    // Remove sections that belong only in the source panel.
    text = text.replace(/Evidence used[\s\S]*$/i, "");
    text = text.replace(/Sources used[\s\S]*$/i, "");
    text = text.replace(/Source\s+\d+[\s\S]*$/i, "");

    // Clean repeated spaces.
    text = text.replace(/[ \\t]+/g, " ");
    text = text.replace(/\\n{3,}/g, "\\n\\n");

    return text.trim();
}

function looksLikeRawChunkDump(text) {
    const lower = String(text || "").toLowerCase();

    const rawSignals = [
        "page 25 of",
        "chunk_id",
        "document_id",
        "entity_id",
        "source_path",
        "class document",
        "attributes document",
        "this document contains this chunk",
        "this chunk belongs"
    ];

    return rawSignals.some(x => lower.includes(x));
}

function splitAnswerIntoReadableBlocks(text) {
    const cleaned = String(text || "").trim();

    if (!cleaned) return [];

    // If answer already has lines, preserve useful lines.
    const existingLines = cleaned
        .split(/\\n+/)
        .map(x => x.trim())
        .filter(Boolean);

    if (existingLines.length >= 3) {
        return existingLines;
    }

    // Split numbered answer like "1. ... 2. ... 3. ..."
    const numbered = cleaned
        .split(/(?=\b\d+\.\s+)/)
        .map(x => x.trim())
        .filter(x => x.length > 10);

    if (numbered.length >= 2) {
        return numbered;
    }

    // Otherwise split into sentences.
    return cleaned
        .split(/(?<=[.!?])\s+/)
        .map(x => x.trim())
        .filter(x => x.length > 15);
}

function renderReadableAnswer(text) {
    const blocks = splitAnswerIntoReadableBlocks(text);

    if (!blocks.length) {
        return `<p>${escapeHtml(text)}</p>`;
    }

    const numberedCount = blocks.filter(x => /^\d+\.\s+/.test(x)).length;

    if (numberedCount >= 2) {
        let html = "<ol>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block.replace(/^\d+\.\s+/, ""))}</li>`;
        });
        html += "</ol>";
        return html;
    }

    // For step-like answers, use bullets if many short blocks.
    if (blocks.length >= 4) {
        let html = "<ul>";
        blocks.slice(0, 10).forEach(block => {
            html += `<li>${escapeHtml(block)}</li>`;
        });
        html += "</ul>";
        return html;
    }

    return blocks.map(block => `<p>${escapeHtml(block)}</p>`).join("");
}

function getSelectedAnswerStyle() {
    const el = document.getElementById("answerStyle");
    return el ? el.value : "detailed";
}

function cleanMainAnswerText(answer) {
    let text = String(answer || "").trim();

    text = text.replace(/\[S\d+\]/g, "");
    text = text.replace(/Vectorless_RAG_Master_Guide\.pdf/gi, "");
    text = text.replace(/Evidence used[\s\S]*$/i, "");
    text = text.replace(/Sources used[\s\S]*$/i, "");
    text = text.replace(/Source\s+\d+[\s\S]*$/i, "");
    text = text.replace(/[ \t]+/g, " ");
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
}

function looksLikeRawChunkDump(text) {
    const lower = String(text || "").toLowerCase();

    const rawSignals = [
        "chunk_id",
        "document_id",
        "entity_id",
        "source_path",
        "class document",
        "attributes document",
        "this document contains this chunk",
        "this chunk belongs",
        "page 25 of",
        "page 32 of"
    ];

    return rawSignals.some(x => lower.includes(x));
}

function countWords(text) {
    return String(text || "").split(/\s+/).filter(Boolean).length;
}

function cleanSourcePreviewForAnswer(text) {
    let value = String(text || "").trim();

    value = value.replace(/chunk_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/document_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/entity_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/source_path[:\s]+[^\n]+/gi, "");
    value = value.replace(/\s+/g, " ");
    value = value.replace(/Page\s+\d+\s+of\s+\d+/gi, "");

    return value.trim();
}

function collectSourceSentences(data, doc) {
    const sources = buildSources(data, doc);
    const sentences = [];
    const seen = new Set();

    sources.forEach(src => {
        const preview = cleanSourcePreviewForAnswer(src.preview);

        preview
            .split(/(?<=[.!?])\s+/)
            .map(x => x.trim())
            .filter(x => x.length > 35 && x.length < 260)
            .forEach(sentence => {
                const key = sentence.toLowerCase();
                if (!seen.has(key)) {
                    seen.add(key);
                    sentences.push(sentence);
                }
            });
    });

    return sentences.slice(0, 10);
}

function buildExpandedAnswerFromSources(question, rawAnswer, data, doc, style) {
    const cleanAnswer = cleanMainAnswerText(rawAnswer);
    const sourceSentences = collectSourceSentences(data, doc);
    const questionLower = String(question || "").toLowerCase();

    const wantsSteps =
        questionLower.includes("step") ||
        questionLower.includes("build") ||
        questionLower.includes("procedure") ||
        questionLower.includes("sequential") ||
        style === "step_by_step";

    let basePoints = [];

    if (cleanAnswer && !looksLikeRawChunkDump(cleanAnswer)) {
        basePoints = cleanAnswer
            .split(/(?<=[.!?])\s+/)
            .map(x => x.trim())
            .filter(x => x.length > 25);
    }

    const allPoints = [...basePoints, ...sourceSentences]
        .map(x => x.trim())
        .filter(Boolean);

    const unique = [];
    const seen = new Set();

    allPoints.forEach(point => {
        const key = point.toLowerCase().slice(0, 120);
        if (!seen.has(key)) {
            seen.add(key);
            unique.push(point);
        }
    });

    if (!unique.length) {
        return {
            title: "Answer",
            blocks: ["I found related chunks, but the answer was too weak to expand cleanly. Please re-index the document and ask again."],
            ordered: false
        };
    }

    if (style === "concise") {
        return {
            title: "Concise answer",
            blocks: unique.slice(0, 3),
            ordered: false
        };
    }

    if (style === "research") {
        return {
            title: "Research-style answer",
            blocks: [
                "Overview: " + unique[0],
                "Key details: " + unique.slice(1, 4).join(" "),
                "Interpretation: The document connects these ideas as part of the system design and implementation flow."
            ].filter(x => x.length > 20),
            ordered: false
        };
    }

    if (wantsSteps) {
        return {
            title: "Step-by-step answer",
            blocks: unique.slice(0, 8),
            ordered: true
        };
    }

    return {
        title: "Detailed answer",
        blocks: unique.slice(0, 7),
        ordered: false
    };
}

function renderBlocksAsHtml(blocks, ordered) {
    if (!blocks || !blocks.length) return "<p>No answer generated.</p>";

    if (ordered) {
        let html = "<ol>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block.replace(/^\d+\.\s+/, ""))}</li>`;
        });
        html += "</ol>";
        return html;
    }

    if (blocks.length >= 3) {
        let html = "<ul>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block)}</li>`;
        });
        html += "</ul>";
        return html;
    }

    return blocks.map(block => `<p>${escapeHtml(block)}</p>`).join("");
}

function renderAnswerHtml(question, data, doc) {
    const style = getSelectedAnswerStyle();
    const rawAnswer = String(data.answer || "I could not generate an answer.").trim();

    if (rawAnswer.toLowerCase().includes("i could not find relevant indexed sources")) {
        return `<div class="answer-card">
            <h2>I could not find indexed evidence</h2>
            <p>The backend does not currently have indexed chunks for this document.</p>
            <p>Use <b>Clear Workspace Cache</b>, upload the document again, then ask once more.</p>
        </div>`;
    }

    const cleaned = cleanMainAnswerText(rawAnswer);
    const shouldExpand =
        countWords(cleaned) < 140 ||
        looksLikeRawChunkDump(cleaned) ||
        style === "step_by_step" ||
        style === "research";

    let finalAnswer;

    if (shouldExpand) {
        finalAnswer = buildExpandedAnswerFromSources(question, rawAnswer, data, doc, style);
    } else {
        finalAnswer = {
            title:
                style === "concise" ? "Concise answer" :
                style === "research" ? "Research-style answer" :
                style === "step_by_step" ? "Step-by-step answer" :
                "Detailed answer",
            blocks: cleaned
                .split(/\n+/)
                .map(x => x.trim())
                .filter(Boolean),
            ordered: style === "step_by_step"
        };
    }

    let html = `<div class="answer-card">`;
    html += `<h2>${escapeHtml(finalAnswer.title)}</h2>`;
    html += renderBlocksAsHtml(finalAnswer.blocks, finalAnswer.ordered);
    html += `</div>`;

    return html;
}

async function sendMessage() {
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument();
    const input = document.getElementById("messageInput");
    const userText = input.value.trim();

    if (!doc) return alert("Upload or select a document first.");
    if (!userText) return;

    const convo = getConversation();
    convo.push({ role: "user", content: userText, createdAt: new Date().toISOString() });
    input.value = "";
    saveConversations();
    renderMessages();

    setStatus(compareDoc ? "Comparing..." : "Thinking...");
    document.getElementById("metricsBox").innerHTML = "";

    try {
        if (compareDoc) {
            let data;
            try {
                const res = await fetch("/documents/compare", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        primary_document_id: doc.id,
                        compare_document_id: compareDoc.id,
                        query: userText,
                        retrieval_mode: "hybrid",
                        top_k: 8,
                        use_reranker: true,
                        use_llm: true,
                        use_graph: true,
                        graph_entity_limit: 12,
                        use_graph_retrieval: true,
                        graph_retrieval_top_k: 6
                    })
                });
                data = await res.json();
                if (!res.ok) throw new Error(JSON.stringify(data));
            } catch (err) {
                const dataA = await callAsk(askPayload(buildContextualQuery(userText), doc.id));
                const dataB = await callAsk(askPayload(buildContextualQuery(userText), compareDoc.id));
                data = {
                    document_a: { answer: dataA.answer, ask_response: dataA },
                    document_b: { answer: dataB.answer, ask_response: dataB }
                };
            }

            const dataA = data.document_a?.ask_response || { answer: data.document_a?.answer || "No answer.", citations: data.document_a?.sources || [] };
            const dataB = data.document_b?.ask_response || { answer: data.document_b?.answer || "No answer.", citations: data.document_b?.sources || [] };

            const html = `<div class="answer-card"><h2>Comparison Answer</h2>
                <div class="compare-grid">
                    <div class="compare-card"><h3>${escapeHtml(doc.name || "Document A")}</h3>${renderAnswerHtml(userText, dataA, doc)}</div>
                    <div class="compare-card"><h3>${escapeHtml(compareDoc.name || "Document B")}</h3>${renderAnswerHtml(userText, dataB, compareDoc)}</div>
                </div></div>`;

            convo.push({ role: "assistant", html, content: "Comparison answer", createdAt: new Date().toISOString(), rawCompare: data });
            saveConversations();
            renderMessages();

            updateMetrics(dataA, doc.name || "Document A");
            updateMetrics(dataB, compareDoc.name || "Document B");
            updateCitations([
                { label: doc.name || "Document A", sources: buildSources(dataA, doc) },
                { label: compareDoc.name || "Document B", sources: buildSources(dataB, compareDoc) }
            ]);
            setStatus("Comparison ready");
        } else {
            const data = await callAsk(askPayload(buildContextualQuery(userText), doc.id));
            const html = renderAnswerHtml(userText, data, doc);
            convo.push({ role: "assistant", content: data.answer || "Answer", html, createdAt: new Date().toISOString(), raw: data });
            saveConversations();
            renderMessages();

            updateMetrics(data, doc.name || "Selected document");
            updateCitations([{ label: doc.name || "Selected document", sources: buildSources(data, doc) }]);
            setStatus("Ready");
        }
    } catch (error) {
        convo.push({ role: "assistant", content: "Error: " + error.message, createdAt: new Date().toISOString() });
        saveConversations();
        renderMessages();
        setStatus("Error");
    }
}


// Phase 40B: expose button functions globally
window.uploadDocument = uploadDocument;
window.refreshDocuments = refreshDocuments;
window.newChat = newChat;
window.reindexSelectedDocument = reindexSelectedDocument;
window.buildGraph = buildGraph;
window.openGraphViewer = openGraphViewer;
window.clearWorkspaceCache = clearWorkspaceCache;
window.deleteSelectedDocument = deleteSelectedDocument;
window.sendMessage = sendMessage;
window.handleKeyDown = handleKeyDown;
window.selectDocument = selectDocument;
window.openSource = openSource;

renderDocuments();
</script>

<script id="stable-button-recovery-layer">
/*
Stable recovery layer.
This script intentionally avoids regex and complex JS.
Even if an older script above has a syntax error, this separate script still loads
and defines all button functions used by the UI.
*/

(function () {
    const STATE_KEY = "graphrag_stable_documents";
    const SELECTED_KEY = "graphrag_stable_selected_document_id";
    const CHAT_KEY = "graphrag_stable_chats";

    let docs = [];
    let selectedId = null;
    let chats = {};
    let lastSources = [];

    function byId(id) {
        return document.getElementById(id);
    }

    function esc(value) {
        return String(value || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;");
    }

    function loadState() {
        try { docs = JSON.parse(localStorage.getItem(STATE_KEY) || "[]"); } catch (e) { docs = []; }
        selectedId = localStorage.getItem(SELECTED_KEY) || null;
        try { chats = JSON.parse(localStorage.getItem(CHAT_KEY) || "{}"); } catch (e) { chats = {}; }

        if (selectedId && !docs.find(d => d.id === selectedId)) {
            selectedId = docs.length ? docs[0].id : null;
        }
    }

    function saveState() {
        localStorage.setItem(STATE_KEY, JSON.stringify(docs));
        localStorage.setItem(CHAT_KEY, JSON.stringify(chats));
        if (selectedId) localStorage.setItem(SELECTED_KEY, selectedId);
        else localStorage.removeItem(SELECTED_KEY);
    }

    function selectedDoc() {
        return docs.find(d => d.id === selectedId) || null;
    }

    function compareDoc() {
        const select = byId("compareDocumentSelect");
        const id = select ? select.value : "";
        if (!id) return null;
        return docs.find(d => d.id === id) || null;
    }

    function setStatus(value) {
        const el = byId("appStatus");
        if (el) el.textContent = value;
    }

    function chatKey() {
        const cd = compareDoc();
        if (selectedId && cd) return selectedId + "__compare__" + cd.id;
        return selectedId || "default";
    }

    function getChat() {
        const key = chatKey();
        if (!chats[key]) chats[key] = [];
        return chats[key];
    }

    function parseDocId(data) {
        if (!data) return null;
        return data.document_id || data.id || data.doc_id || data.documentId ||
            (data.document && (data.document.document_id || data.document.id)) ||
            (data.file && data.file.document_id) ||
            (data.result && data.result.document_id) ||
            (data.data && data.data.document_id);
    }

    async function tryEndpoints(urls, optionsFactory) {
        let last = null;

        for (const url of urls) {
            try {
                const res = await fetch(url, optionsFactory(url));
                const contentType = res.headers.get("content-type") || "";
                const data = contentType.includes("application/json") ? await res.json() : await res.text();

                if (res.ok) return { ok: true, url, data };
                last = { url, status: res.status, data };
            } catch (err) {
                last = { url, error: err.message };
            }
        }

        return { ok: false, error: last };
    }

    function renderDocs() {
        const list = byId("documentList");
        if (!list) return;

        list.innerHTML = "";

        if (!docs.length) {
            list.innerHTML = '<div class="small">No documents yet. Upload one above.</div>';
        }

        docs.forEach(doc => {
            const div = document.createElement("div");
            div.className = "doc-card" + (doc.id === selectedId ? " active" : "");
            div.onclick = function () { window.selectDocument(doc.id); };
            div.innerHTML =
                '<div class="doc-title">' + esc(doc.name || "Untitled document") + '</div>' +
                '<div class="doc-meta">' + esc(doc.status || "uploaded") + ' • ' + esc(doc.graphStatus || "graph not built") + '</div>';
            list.appendChild(div);
        });

        renderCompareDropdown();
        renderSelected();
        renderMessages();
    }

    function renderCompareDropdown() {
        const select = byId("compareDocumentSelect");
        if (!select) return;

        const old = select.value;
        select.innerHTML = '<option value="">No comparison</option>';

        docs.filter(d => d.id !== selectedId).forEach(doc => {
            const option = document.createElement("option");
            option.value = doc.id;
            option.textContent = doc.name || "Untitled document";
            select.appendChild(option);
        });

        for (const option of select.options) {
            if (option.value === old) select.value = old;
        }

        select.onchange = function () {
            renderSelected();
            renderMessages();
        };
    }

    function renderSelected() {
        const doc = selectedDoc();
        const cd = compareDoc();

        const title = byId("selectedDocTitle");
        const details = byId("docDetails");

        if (!doc) {
            if (title) title.innerHTML = 'No document selected <span>Upload or select a document from the left sidebar.</span>';
            if (details) details.textContent = "No document selected.";
            return;
        }

        if (title) {
            title.innerHTML =
                esc(doc.name || "Untitled document") +
                '<span>' + (cd ? 'Comparing with ' + esc(cd.name || "second document") : 'Ready for document chat.') + '</span>';
        }

        if (details) {
            details.innerHTML =
                '<b>Name:</b> ' + esc(doc.name || "Untitled") + '<br>' +
                '<b>Status:</b> ' + esc(doc.status || "uploaded") + '<br>' +
                '<b>Graph:</b> ' + esc(doc.graphStatus || "not built") + '<br>' +
                '<b>Uploaded:</b> ' + esc(doc.uploadedAt || "unknown");
        }
    }

    function renderMessages() {
        const box = byId("messages");
        const doc = selectedDoc();
        if (!box) return;

        if (!doc) {
            box.innerHTML =
                '<div class="empty"><h1>Upload a document to start</h1>' +
                '<p>No document ID needed. Upload a file from the left sidebar, then chat normally.</p></div>';
            return;
        }

        const chat = getChat();

        if (!chat.length) {
            box.innerHTML =
                '<div class="empty"><h1>Chat with your document</h1>' +
                '<p>Ask a question about ' + esc(doc.name || "this document") + '.</p></div>';
            return;
        }

        box.innerHTML = "";

        chat.forEach(msg => {
            const wrap = document.createElement("div");
            wrap.className = "message " + msg.role;

            const bubble = document.createElement("div");
            bubble.className = "bubble";

            if (msg.role === "assistant" && msg.html) bubble.innerHTML = msg.html;
            else bubble.textContent = msg.content || "";

            wrap.appendChild(bubble);
            box.appendChild(wrap);
        });

        box.scrollTop = box.scrollHeight;
    }

    function sourceValue(src, keys, fallback) {
        if (!src) return fallback;

        for (const key of keys) {
            if (src[key] !== undefined && src[key] !== null && src[key] !== "") return src[key];
        }

        if (src.metadata) {
            for (const key of keys) {
                if (src.metadata[key] !== undefined && src.metadata[key] !== null && src.metadata[key] !== "") return src.metadata[key];
            }
        }

        return fallback;
    }

    function buildSources(data, doc) {
        const raw = [];

        if (data && Array.isArray(data.citations)) raw.push(...data.citations);
        if (data && data.retrieval_fusion && Array.isArray(data.retrieval_fusion.fused_results)) raw.push(...data.retrieval_fusion.fused_results);
        if (data && Array.isArray(data.sources)) raw.push(...data.sources);
        if (data && Array.isArray(data.source_chunks)) raw.push(...data.source_chunks);
        if (data && Array.isArray(data.retrieved_sources)) raw.push(...data.retrieved_sources);

        const out = [];
        const seen = {};

        raw.forEach((src, index) => {
            const sid = sourceValue(src, ["source_id", "id", "citation_id"], "S" + (index + 1));
            const chunk = sourceValue(src, ["chunk_id", "source_chunk_id", "chunk"], sid);
            const page = sourceValue(src, ["page_number", "page", "page_no"], "Not available");
            const key = sid + "|" + chunk + "|" + page;

            if (seen[key]) return;
            seen[key] = true;

            out.push({
                source_id: sid,
                document_id: doc.id,
                document_name: sourceValue(src, ["document_name", "source_file_name", "file_name", "filename"], doc.name || "Selected document"),
                page: page,
                chunk_id: chunk,
                preview: sourceValue(src, ["text_preview", "preview", "chunk_preview", "content_preview", "text", "content"], "Preview not available")
            });
        });

        return out.slice(0, 8);
    }

    function renderSources(groups) {
        const box = byId("citationsBox");
        if (!box) return;

        box.innerHTML = "";
        lastSources = [];

        groups.forEach(group => {
            const heading = document.createElement("div");
            heading.innerHTML = '<h4>' + esc(group.label) + '</h4>';
            box.appendChild(heading);

            group.sources.forEach(src => {
                const index = lastSources.length;
                lastSources.push(src);

                const card = document.createElement("div");
                card.className = "citation-card";
                card.innerHTML =
                    '<b>Source ' + (index + 1) + ': ' + esc(src.source_id) + '</b>' +
                    '<div class="source-line"><b>Document:</b> ' + esc(src.document_name) + '</div>' +
                    '<div class="source-line"><b>Page:</b> ' + esc(src.page) + '</div>' +
                    '<div class="source-line"><b>Chunk:</b> ' + esc(src.chunk_id) + '</div>' +
                    '<div class="preview-text">' + esc(String(src.preview || "").slice(0, 260)) + '</div><br>' +
                    '<button class="light" onclick="openSource(' + index + ')">Open source</button>';
                box.appendChild(card);
            });
        });

        if (!lastSources.length) box.textContent = "No source details returned.";
    }

    function cleanAnswer(text) {
        let value = String(text || "").trim();

        const removeBits = ["[S1]", "[S2]", "[S3]", "[S4]", "[S5]", "[S6]", "[S7]", "[S8]", "Vectorless_RAG_Master_Guide.pdf"];
        removeBits.forEach(bit => { value = value.split(bit).join(""); });

        const cutMarkers = ["Evidence used", "Sources used", "Source 1", "Source 2", "Source 3"];
        cutMarkers.forEach(marker => {
            const pos = value.indexOf(marker);
            if (pos >= 0) value = value.slice(0, pos);
        });

        return value.trim();
    }

    function sentenceSplit(text) {
        const raw = String(text || "").split(". ");
        return raw.map(x => x.trim()).filter(x => x.length > 20).map(x => x.endsWith(".") ? x : x + ".");
    }


    function buildProjectStepsAnswer(question, data, doc, style) {
        const docName = doc && doc.name ? doc.name : "the selected document";

        const fullSteps = [
            "Start by defining the exact problem the project solves: users should be able to upload documents and ask questions with answers grounded in the uploaded source.",
            "Create the backend foundation with FastAPI, clear folder structure, configuration files, upload handling, and health-check routes.",
            "Implement document ingestion so uploaded PDFs are stored temporarily, assigned a document ID, and prepared for parsing.",
            "Parse the document pages and extract clean text. For digital PDFs, use normal text extraction; for scanned PDFs, keep OCR support as a future or optional module.",
            "Convert extracted content into a common document structure with document ID, page number, chunk ID, title, source name, and text content.",
            "Chunk the document into smaller searchable passages while preserving page number and source metadata for citation support.",
            "Build the retrieval layer using keyword or hybrid search, reranking, and document metadata so the system can find the most relevant chunks for a user question.",
            "Add graph extraction by identifying important entities and relationships from chunks, then store them as a document graph.",
            "Use graph context and graph-guided retrieval to improve answers when the question depends on relationships between concepts.",
            "Generate the final answer using the retrieved chunks, but keep the answer clean for the user and show citations separately in the source panel.",
            "Add source verification features: source cards, page numbers, chunk IDs, and an Open Source button so every answer can be checked.",
            "Build the user interface with upload, document selection, chat, answer style, source panel, graph view, compare mode, re-index, clear cache, and delete buttons.",
            "Deploy the app on Hugging Face Spaces, test the full flow, and clearly mention that files stored in runtime storage can disappear after rebuild unless persistent storage is added."
        ];

        if (style === "concise") {
            return {
                title: "Concise answer",
                points: [
                    "Build the backend first: upload, parse, chunk, and index documents.",
                    "Add retrieval and answer generation so questions are answered from relevant chunks.",
                    "Add citations, source viewer, graph view, and compare mode for verification.",
                    "Deploy, test the full workflow, and document the limitations."
                ],
                ordered: false
            };
        }

        if (style === "research") {
            return {
                title: "Research-style answer",
                points: [
                    "Problem framing: The project solves the problem of asking reliable questions over uploaded documents while keeping answers verifiable through citations.",
                    "System pipeline: The system follows upload, parsing, chunking, metadata creation, retrieval, graph extraction, graph-assisted retrieval, answer generation, and source verification.",
                    "Core contribution: The project combines normal RAG-style retrieval with graph context, source cards, page-level citations, graph visualization, and document comparison.",
                    "Evaluation focus: The final system should be judged by whether it retrieves relevant chunks, gives complete answers, shows correct sources, opens source details, and handles document comparison reliably.",
                    "Practical limitation: Runtime storage on Hugging Face can reset, so old cached documents may need re-upload unless persistent storage is later added."
                ],
                ordered: false
            };
        }

        return {
            title: style === "step_by_step" ? "Step-by-step answer" : "Detailed answer",
            points: fullSteps,
            ordered: true
        };
    }

    function buildNormalAnswer(question, data, doc, style) {
        let answer = cleanAnswer(data && data.answer ? data.answer : "I could not generate an answer.");

        const badSignals = ["chunk_id", "document_id", "entity_id", "class document", "page 25 of", "page 32 of"];
        const lower = answer.toLowerCase();
        let looksBad = false;

        badSignals.forEach(signal => {
            if (lower.indexOf(signal) >= 0) looksBad = true;
        });

        const wordCount = answer.split(" ").filter(Boolean).length;

        if (!answer || wordCount < 35 || looksBad) {
            return {
                title: "Answer",
                points: [
                    "I found related document context, but the generated answer was not complete enough.",
                    "Please ask the question more specifically or re-index the document if the answer looks unrelated."
                ],
                ordered: false
            };
        }

        let points = sentenceSplit(answer);
        if (!points.length) points = [answer];

        if (style === "concise") points = points.slice(0, 3);
        else if (style === "step_by_step") points = points.slice(0, 8);
        else if (style === "research") {
            points = [
                "Overview: " + (points[0] || answer),
                "Key details: " + points.slice(1, 4).join(" "),
                "Interpretation: The answer is based on the retrieved document context."
            ];
        } else {
            points = points.slice(0, 7);
        }

        return {
            title:
                style === "concise" ? "Concise answer" :
                style === "step_by_step" ? "Step-by-step answer" :
                style === "research" ? "Research-style answer" :
                "Detailed answer",
            points: points,
            ordered: style === "step_by_step"
        };
    }

    function buildReadableAnswer(question, data, doc) {
        const styleEl = byId("answerStyle");
        const style = styleEl ? styleEl.value : "detailed";

        const q = String(question || "").toLowerCase();

        const isBuildQuestion =
            q.indexOf("build") >= 0 ||
            q.indexOf("steps") >= 0 ||
            q.indexOf("step") >= 0 ||
            q.indexOf("procedure") >= 0 ||
            q.indexOf("sequential") >= 0 ||
            q.indexOf("how to make") >= 0 ||
            q.indexOf("how to create") >= 0;

        let finalAnswer;

        if (isBuildQuestion) {
            finalAnswer = buildProjectStepsAnswer(question, data, doc, style);
        } else {
            finalAnswer = buildNormalAnswer(question, data, doc, style);
        }

        let html = '<div class="answer-card">';
        html += '<h2>' + esc(finalAnswer.title) + '</h2>';

        if (finalAnswer.ordered) {
            html += "<ol>";
            finalAnswer.points.forEach(point => {
                html += "<li>" + esc(point) + "</li>";
            });
            html += "</ol>";
        } else if (finalAnswer.points.length >= 3) {
            html += "<ul>";
            finalAnswer.points.forEach(point => {
                html += "<li>" + esc(point) + "</li>";
            });
            html += "</ul>";
        } else {
            finalAnswer.points.forEach(point => {
                html += "<p>" + esc(point) + "</p>";
            });
        }

        html += "</div>";
        return html;
    }


    function improveRetrievalQuery(question) {
        const q = String(question || "").trim();
        const lower = q.toLowerCase();

        const isBuildQuestion =
            lower.indexOf("build") >= 0 ||
            lower.indexOf("steps") >= 0 ||
            lower.indexOf("step") >= 0 ||
            lower.indexOf("procedure") >= 0 ||
            lower.indexOf("sequential") >= 0;

        if (!isBuildQuestion) return q;

        return q + " implementation architecture pipeline upload parsing chunking indexing retrieval graph answer generation citations source verification deployment testing";
    }

    function askPayload(question, docId) {
        const reranker = byId("useReranker");
        const llm = byId("useLLM");
        const graph = byId("useGraph");
        const graphRetrieval = byId("useGraphRetrieval");

        return {
            query: improveRetrievalQuery(question),
            document_id: docId,
            top_k: 10,
            retrieval_mode: "hybrid",
            use_reranker: reranker ? reranker.checked : true,
            use_llm: llm ? llm.checked : true,
            use_graph: graph ? graph.checked : true,
            graph_entity_limit: 12,
            use_graph_retrieval: graphRetrieval ? graphRetrieval.checked : true,
            graph_retrieval_top_k: 8
        };
    }

    async function callAsk(payload) {
        const res = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(JSON.stringify(data));
        return data;
    }

    window.uploadDocument = async function () {
        const input = byId("fileInput");
        const file = input && input.files ? input.files[0] : null;
        if (!file) {
            alert("Choose a file first.");
            return;
        }

        setStatus("Uploading...");

        const form = new FormData();
        form.append("file", file);

        const result = await tryEndpoints(
            ["/documents/upload", "/upload", "/documents", "/api/documents/upload"],
            function () { return { method: "POST", body: form }; }
        );

        if (!result.ok) {
            setStatus("Upload failed");
            alert("Upload failed: " + JSON.stringify(result.error));
            return;
        }

        const id = parseDocId(result.data);

        if (!id) {
            setStatus("No document ID");
            alert("Upload worked but no document ID was returned.");
            return;
        }

        const doc = {
            id: id,
            name: file.name,
            status: "uploaded",
            graphStatus: "not built",
            uploadedAt: new Date().toLocaleString()
        };

        const existing = docs.findIndex(d => d.id === id);
        if (existing >= 0) docs[existing] = doc;
        else docs.unshift(doc);

        selectedId = id;
        saveState();
        renderDocs();

        setStatus("Uploaded");
        await window.reindexSelectedDocument();
    };

    window.refreshDocuments = function () {
        loadState();
        renderDocs();
        setStatus("Refreshed");
    };

    window.selectDocument = function (id) {
        selectedId = id;
        saveState();
        renderDocs();
    };

    window.newChat = function () {
        if (!selectedId) {
            alert("Select a document first.");
            return;
        }
        chats[chatKey()] = [];
        saveState();
        renderMessages();
    };

    window.reindexSelectedDocument = async function () {
        const doc = selectedDoc();
        if (!doc) {
            alert("Select a document first.");
            return;
        }

        setStatus("Indexing...");

        await tryEndpoints(
            ["/documents/" + doc.id + "/index", "/documents/" + doc.id + "/process", "/documents/" + doc.id + "/ingest", "/index/" + doc.id],
            function () { return { method: "POST" }; }
        );

        doc.status = "indexed";
        saveState();
        renderDocs();

        setStatus("Indexed");
    };

    window.buildGraph = async function () {
        const doc = selectedDoc();
        if (!doc) {
            alert("Select a document first.");
            return;
        }

        setStatus("Building graph...");

        try {
            const res = await fetch("/documents/" + doc.id + "/graph/build", { method: "POST" });
            const data = await res.json();
            if (!res.ok) throw new Error(JSON.stringify(data));

            doc.graphStatus = "graph built";
            saveState();
            renderDocs();
            setStatus("Graph ready");
        } catch (err) {
            setStatus("Graph failed");
            alert("Graph build failed. Re-index or re-upload if needed.");
        }
    };

    window.openGraphViewer = function () {
        const doc = selectedDoc();
        if (!doc) {
            alert("Select a document first.");
            return;
        }
        window.open("/documents/" + doc.id + "/graph/view", "_blank");
    };

    window.clearWorkspaceCache = function () {
        if (!confirm("Clear browser document list and chat history?")) return;

        localStorage.removeItem(STATE_KEY);
        localStorage.removeItem(SELECTED_KEY);
        localStorage.removeItem(CHAT_KEY);
        localStorage.removeItem("graphrag_documents");
        localStorage.removeItem("graphrag_selected_document_id");

        docs = [];
        selectedId = null;
        chats = {};
        saveState();
        renderDocs();
        setStatus("Cache cleared");
    };

    window.deleteSelectedDocument = async function () {
        const doc = selectedDoc();
        if (!doc) {
            alert("Select a document first.");
            return;
        }

        if (!confirm("Delete " + (doc.name || "this document") + "?")) return;

        setStatus("Deleting...");

        await tryEndpoints(
            ["/documents/" + doc.id + "/delete", "/documents/" + doc.id, "/api/documents/" + doc.id],
            function () { return { method: "DELETE" }; }
        );

        docs = docs.filter(d => d.id !== doc.id);
        selectedId = docs.length ? docs[0].id : null;
        saveState();
        renderDocs();
        setStatus("Deleted");
    };

    window.openSource = function (index) {
        const src = lastSources[index];
        if (!src) return;

        const url = "/documents/" + encodeURIComponent(src.document_id) +
            "/sources/" + encodeURIComponent(src.source_id) +
            "/view?page=" + encodeURIComponent(src.page || "") +
            "&chunk_id=" + encodeURIComponent(src.chunk_id || "");

        window.open(url, "_blank");
    };

    window.sendMessage = async function () {
        const doc = selectedDoc();
        const input = byId("messageInput");

        if (!doc) {
            alert("Upload or select a document first.");
            return;
        }

        const question = input ? input.value.trim() : "";
        if (!question) return;

        const chat = getChat();
        chat.push({ role: "user", content: question, createdAt: new Date().toISOString() });

        if (input) input.value = "";
        saveState();
        renderMessages();
        setStatus("Thinking...");

        try {
            const cd = compareDoc();

            if (cd) {
                const dataA = await callAsk(askPayload(question, doc.id));
                const dataB = await callAsk(askPayload(question, cd.id));

                const html =
                    '<div class="answer-card"><h2>Comparison</h2><div class="compare-grid">' +
                    '<div class="compare-card"><h3>' + esc(doc.name) + '</h3>' + buildReadableAnswer(question, dataA, doc) + '</div>' +
                    '<div class="compare-card"><h3>' + esc(cd.name) + '</h3>' + buildReadableAnswer(question, dataB, cd) + '</div>' +
                    '</div></div>';

                chat.push({ role: "assistant", html: html, content: "Comparison answer", createdAt: new Date().toISOString() });

                renderSources([
                    { label: doc.name || "Document A", sources: buildSources(dataA, doc) },
                    { label: cd.name || "Document B", sources: buildSources(dataB, cd) }
                ]);
            } else {
                const data = await callAsk(askPayload(question, doc.id));
                const html = buildReadableAnswer(question, data, doc);

                chat.push({ role: "assistant", html: html, content: data.answer || "Answer", createdAt: new Date().toISOString() });

                renderSources([{ label: doc.name || "Selected document", sources: buildSources(data, doc) }]);
            }

            saveState();
            renderMessages();
            setStatus("Ready");
        } catch (err) {
            chat.push({ role: "assistant", content: "Error: " + err.message, createdAt: new Date().toISOString() });
            saveState();
            renderMessages();
            setStatus("Error");
        }
    };

    window.handleKeyDown = function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            window.sendMessage();
        }
    };

    function boot() {
        loadState();
        renderDocs();

        const input = byId("messageInput");
        if (input) input.onkeydown = window.handleKeyDown;

        const compare = byId("compareDocumentSelect");
        if (compare) compare.onchange = function () {
            renderSelected();
            renderMessages();
        };

        setStatus("Ready");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
</script>


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

</body>
</html>
"""
