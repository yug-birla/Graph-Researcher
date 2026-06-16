from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

hf_path = Path("app/deployment/hf_status.py")
text = hf_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

compare_app = r'''


# =====================================================
# Phase 29 override: multi-document compare app UI
# =====================================================

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
            grid-template-columns: 310px 1fr 370px;
            height: 100vh;
        }

        .sidebar {
            background: #0f172a;
            color: white;
            padding: 18px;
            overflow-y: auto;
        }

        .brand {
            font-size: 24px;
            font-weight: 900;
            margin-bottom: 18px;
        }

        .upload-box {
            border: 1px dashed rgba(255,255,255,0.35);
            border-radius: 16px;
            padding: 14px;
            background: rgba(255,255,255,0.06);
            margin-bottom: 20px;
        }

        .upload-box input {
            width: 100%;
            font-size: 12px;
            margin: 10px 0;
        }

        button {
            border: none;
            border-radius: 10px;
            padding: 10px 13px;
            cursor: pointer;
            background: #2563eb;
            color: white;
            font-weight: 800;
        }

        button:hover { background: #1d4ed8; }
        button.secondary { background: #334155; }
        button.green { background: #059669; }
        button.red { background: #dc2626; }
        button.light {
            background: #f1f5f9;
            color: #0f172a;
            border: 1px solid #cbd5e1;
        }

        .full {
            width: 100%;
            margin-bottom: 9px;
        }

        .small {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
        }

        .doc-card {
            padding: 12px;
            border-radius: 13px;
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
            font-weight: 800;
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
            font-weight: 900;
            font-size: 17px;
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
            padding: 26px;
        }

        .message {
            max-width: 920px;
            margin-bottom: 18px;
            display: flex;
        }

        .message.user {
            margin-left: auto;
            justify-content: flex-end;
        }

        .bubble {
            padding: 15px 17px;
            border-radius: 17px;
            line-height: 1.65;
            white-space: pre-wrap;
            font-size: 15.5px;
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

        .compare-bubble {
            width: 100%;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        .compare-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-top: 12px;
        }

        .compare-card {
            border: 1px solid #e5e7eb;
            background: #f8fafc;
            border-radius: 14px;
            padding: 14px;
            white-space: pre-wrap;
            line-height: 1.6;
        }

        .compare-card h3 {
            margin-top: 0;
            color: #1d4ed8;
        }

        .empty {
            max-width: 760px;
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

        select {
            width: 100%;
            padding: 9px;
            border-radius: 9px;
            border: 1px solid #cbd5e1;
            background: white;
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
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 11px;
            font-size: 13px;
        }

        .citation-card b { color: #0f172a; }

        .source-line {
            margin-top: 5px;
            color: #475569;
        }

        .preview-text {
            margin-top: 8px;
            color: #64748b;
            font-size: 12px;
            line-height: 1.5;
        }

        .danger-zone {
            border-top: 1px solid #e5e7eb;
            padding-top: 14px;
        }

        @media (max-width: 1150px) {
            .app { grid-template-columns: 290px 1fr; }
            .right-panel { display: none; }
        }

        @media (max-width: 850px) {
            .compare-grid { grid-template-columns: 1fr; }
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
            <p class="small">Upload documents, select one, and chat. You can also compare two documents.</p>
            <input id="fileInput" type="file">
            <button class="full green" onclick="uploadDocument()">Upload & Select</button>
            <button class="full secondary" onclick="refreshDocuments()">Refresh Documents</button>
        </div>

        <div class="small" style="margin-bottom: 8px;">My Documents</div>
        <div id="documentList"></div>

        <hr style="border-color: rgba(255,255,255,0.15); margin: 18px 0;">

        <button class="full secondary" onclick="newChat()">+ New Chat</button>
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
                <textarea id="messageInput" placeholder="Ask about the selected document, or compare with another document..." onkeydown="handleKeyDown(event)"></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="small" style="margin-top: 8px;">
                For comparison: choose a second document in the right panel, then ask “Compare the main ideas” or “Which document explains better?”
            </div>
        </div>
    </main>

    <aside class="right-panel">
        <div class="panel-section">
            <h3>Selected Document</h3>
            <div id="docDetails" class="small">No document selected.</div>
        </div>

        <div class="panel-section">
            <h3>Compare With</h3>
            <select id="compareDocumentSelect" onchange="renderSelectedDocument()">
                <option value="">No comparison</option>
            </select>
            <p class="small">Choose another document to compare answers side-by-side.</p>
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
            <div id="metricsBox">
                <span class="metric">No answer yet</span>
            </div>
        </div>

        <div class="panel-section">
            <h3>Sources</h3>
            <div id="citationsBox" class="small">Sources will appear here after an answer.</div>
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
let conversations = JSON.parse(localStorage.getItem("graphrag_conversations_v3") || "{}");
let lastSources = [];

function saveDocuments() {
    localStorage.setItem("graphrag_documents", JSON.stringify(documents));
    if (selectedDocumentId) {
        localStorage.setItem("graphrag_selected_document_id", selectedDocumentId);
    }
}

function saveConversations() {
    localStorage.setItem("graphrag_conversations_v3", JSON.stringify(conversations));
}

function setStatus(text) {
    document.getElementById("appStatus").textContent = text;
}

function getSelectedDocument() {
    return documents.find(d => d.id === selectedDocumentId) || null;
}

function getCompareDocument() {
    const compareId = document.getElementById("compareDocumentSelect")?.value || "";
    if (!compareId) return null;
    return documents.find(d => d.id === compareId) || null;
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
            const response = await fetch(candidate, optionsFactory(candidate));
            const contentType = response.headers.get("content-type") || "";
            const data = contentType.includes("application/json") ? await response.json() : await response.text();

            if (response.ok) {
                return { ok: true, endpoint: candidate, data };
            }

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

    renderCompareDropdown();
    renderSelectedDocument();
}

function renderCompareDropdown() {
    const select = document.getElementById("compareDocumentSelect");
    if (!select) return;

    const oldValue = select.value;

    select.innerHTML = `<option value="">No comparison</option>`;

    documents
        .filter(doc => doc.id !== selectedDocumentId)
        .forEach(doc => {
            const option = document.createElement("option");
            option.value = doc.id;
            option.textContent = doc.name || "Untitled document";
            select.appendChild(option);
        });

    if ([...select.options].some(o => o.value === oldValue)) {
        select.value = oldValue;
    }
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

    let subtitle = "Ready for document chat.";

    if (compareDoc) {
        subtitle = `Compare mode active with ${compareDoc.name || "second document"}.`;
    }

    title.innerHTML = `${doc.name || "Untitled document"} <span>${subtitle}</span>`;

    details.innerHTML = `
        <b>Name:</b> ${doc.name || "Untitled"}<br>
        <b>Status:</b> ${doc.status || "uploaded"}<br>
        <b>Graph:</b> ${doc.graphStatus || "not built"}<br>
        <b>Uploaded:</b> ${doc.uploadedAt || "unknown"}<br>
        ${compareDoc ? `<br><b>Comparing with:</b> ${compareDoc.name || "Untitled"}` : ""}
    `;

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

function newChat() {
    if (!selectedDocumentId) {
        alert("Select a document first.");
        return;
    }

    conversations[getConversationKey()] = [];
    saveConversations();
    renderMessages();
}

function getConversation() {
    const key = getConversationKey();

    if (!conversations[key]) {
        conversations[key] = [];
    }

    return conversations[key];
}

function renderMessages() {
    const box = document.getElementById("messages");
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument();

    if (!doc) {
        box.innerHTML = `
            <div class="empty">
                <h1>Upload a document to start</h1>
                <p>No document ID needed. Upload a file from the left sidebar, then chat normally.</p>
            </div>
        `;
        return;
    }

    const convo = getConversation();

    if (convo.length === 0) {
        box.innerHTML = `
            <div class="empty">
                <h1>${compareDoc ? "Compare documents" : "Chat with your document"}</h1>
                <p>
                    ${compareDoc
                        ? `You are comparing ${doc.name} with ${compareDoc.name}. Ask a comparison question below.`
                        : `Ask a question about ${doc.name}. Answers will include citation-backed sources.`}
                </p>
            </div>
        `;
        return;
    }

    box.innerHTML = "";

    convo.forEach(msg => {
        const wrapper = document.createElement("div");
        wrapper.className = "message " + msg.role;

        if (msg.type === "compare") {
            const bubble = document.createElement("div");
            bubble.className = "compare-bubble";
            bubble.innerHTML = `
                <h2>Comparison Answer</h2>
                <p><b>Question:</b> ${escapeHtml(msg.question)}</p>
                <div class="compare-grid">
                    <div class="compare-card">
                        <h3>${escapeHtml(msg.docAName)}</h3>
                        ${escapeHtml(msg.answerA)}
                    </div>
                    <div class="compare-card">
                        <h3>${escapeHtml(msg.docBName)}</h3>
                        ${escapeHtml(msg.answerB)}
                    </div>
                </div>
                <p class="small" style="color:#64748b;margin-top:12px;">
                    This compare mode retrieves and answers from both documents independently, then shows both evidence-backed answers side by side.
                </p>
            `;
            wrapper.appendChild(bubble);
        } else {
            const bubble = document.createElement("div");
            bubble.className = "bubble";
            bubble.textContent = msg.content;
            wrapper.appendChild(bubble);
        }

        box.appendChild(wrapper);
    });

    box.scrollTop = box.scrollHeight;
}

function escapeHtml(text) {
    return String(text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
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

    const result = await tryEndpoints(
        ["/documents/upload", "/upload", "/documents", "/api/documents/upload"],
        () => ({ method: "POST", body: formData })
    );

    if (!result.ok) {
        setStatus("Upload failed");
        alert("Upload failed. Error: " + JSON.stringify(result.error));
        return;
    }

    const documentId = parseDocumentId(result.data);

    if (!documentId) {
        setStatus("Upload returned no document");
        alert("Upload worked but document ID was not found in response.");
        return;
    }

    const doc = {
        id: documentId,
        name: file.name,
        status: "uploaded",
        graphStatus: "not built",
        uploadedAt: new Date().toLocaleString()
    };

    const existingIndex = documents.findIndex(d => d.id === documentId);

    if (existingIndex >= 0) documents[existingIndex] = doc;
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

    const result = await tryEndpoints(
        [
            `/documents/${documentId}/index`,
            `/documents/${documentId}/process`,
            `/documents/${documentId}/ingest`,
            `/index/${documentId}`
        ],
        () => ({ method: "POST" })
    );

    const doc = documents.find(d => d.id === documentId);

    if (doc) {
        doc.status = result.ok ? "indexed" : "uploaded";
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
        const response = await fetch(`/documents/${doc.id}/graph/build`, { method: "POST" });
        const data = await response.json();

        if (!response.ok) throw new Error(JSON.stringify(data));

        doc.graphStatus = "graph built";
        doc.graphData = {
            entities: data.total_entities ?? data.entity_count ?? null,
            relations: data.total_relations ?? data.relation_count ?? null
        };

        saveDocuments();
        renderDocuments();

        setStatus("Graph ready");

    } catch (error) {
        doc.graphStatus = "graph not built";
        saveDocuments();
        renderDocuments();

        setStatus("Graph skipped");
        if (!silent) alert("Graph build failed: " + error.message);
    }
}

async function deleteSelectedDocument() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert("Select a document first.");
        return;
    }

    if (!confirm(`Delete "${doc.name}" from this workspace?`)) return;

    setStatus("Deleting...");

    await tryEndpoints(
        [`/documents/${doc.id}`, `/documents/${doc.id}/delete`, `/api/documents/${doc.id}`],
        () => ({ method: "DELETE" })
    );

    documents = documents.filter(d => d.id !== doc.id);

    Object.keys(conversations).forEach(key => {
        if (key.includes(doc.id)) delete conversations[key];
    });

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

function getAnswerStyleInstruction() {
    const style = document.getElementById("answerStyle").value;

    if (style === "concise") {
        return "Answer concisely, but include citations after important claims.";
    }

    if (style === "step_by_step") {
        return "Answer step by step with numbered points. Include citations after key points.";
    }

    if (style === "research") {
        return "Answer in research style: direct answer, evidence, interpretation, limitations. Include citations after key claims.";
    }

    if (style === "comparison") {
        return "Focus on comparison. Explain similarities, differences, and evidence clearly. Include citations after key claims.";
    }

    return "Answer in a detailed but readable format. Start with a direct answer, then explain important points with evidence. Include citations after key claims.";
}

function buildContextualQuery(currentQuestion, compareMode = false) {
    const convo = getConversation().slice(-6);
    const instruction = getAnswerStyleInstruction();

    let context = "";

    if (convo.length > 0) {
        context = convo
            .filter(m => m.type !== "compare")
            .map(m => `${m.role}: ${m.content}`)
            .join("\\n");
    }

    const compareInstruction = compareMode
        ? "This is part of a two-document comparison. Answer only using this document's evidence. Make your answer detailed enough to compare with another document."
        : "";

    return `${instruction}\\n${compareInstruction}\\n\\nConversation so far:\\n${context}\\n\\nCurrent user question:\\n${currentQuestion}`;
}

function askPayload(query, documentId) {
    return {
        query: query,
        document_id: documentId,
        top_k: 7,
        retrieval_mode: "hybrid",
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked,
        use_graph: document.getElementById("useGraph").checked,
        graph_entity_limit: 10,
        use_graph_retrieval: document.getElementById("useGraphRetrieval").checked,
        graph_retrieval_top_k: 6
    };
}

async function callAsk(payload) {
    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(JSON.stringify(data));
    }

    return data;
}

function updateMetrics(data, label = "") {
    const fusion = data.retrieval_fusion || {};
    const graph = data.graph_context || {};

    document.getElementById("metricsBox").innerHTML += `
        <div style="margin-bottom:8px;">
            <b>${label}</b><br>
            <span class="metric">strategy: ${data.answer_strategy || "NA"}</span>
            <span class="metric">LLM: ${data.used_llm}</span>
            <span class="metric">graph: ${data.graph_used}</span>
            <span class="metric">graph available: ${graph.graph_available}</span>
            <span class="metric">fusion: ${fusion.fusion_used}</span>
            <span class="metric">graph added: ${fusion.graph_added_count ?? "NA"}</span>
        </div>
    `;
}

function valueFrom(obj, keys, fallback = "Not available") {
    for (const key of keys) {
        if (obj && obj[key] !== undefined && obj[key] !== null && obj[key] !== "") {
            return obj[key];
        }
    }

    if (obj && obj.metadata) {
        for (const key of keys) {
            if (obj.metadata[key] !== undefined && obj.metadata[key] !== null && obj.metadata[key] !== "") {
                return obj.metadata[key];
            }
        }
    }

    return fallback;
}

function buildSources(data, doc) {
    const sources = [];

    (data.citations || []).forEach(c => sources.push(c));
    (data.retrieval_fusion?.fused_results || []).forEach(r => sources.push(r));
    (data.sources || data.source_chunks || data.retrieved_sources || []).forEach(s => sources.push(s));

    const seen = new Set();
    const cleaned = [];

    sources.forEach((src, index) => {
        const sourceId = valueFrom(src, ["source_id", "id", "citation_id"], "S" + (index + 1));
        const chunkId = valueFrom(src, ["chunk_id", "source_chunk_id", "chunk"], sourceId);
        const key = doc.id + "|" + sourceId + "|" + chunkId;

        if (seen.has(key)) return;
        seen.add(key);

        cleaned.push({
            source_id: sourceId,
            document_id: doc.id,
            document_name: valueFrom(src, ["document_name", "source_file_name", "file_name", "filename", "document_title"], doc.name || "Selected document"),
            page: valueFrom(src, ["page_number", "page", "page_no"], "Not available"),
            chunk_id: chunkId,
            preview: valueFrom(src, ["text_preview", "preview", "chunk_preview", "content_preview", "text", "content"], "Preview not available"),
            raw: src
        });
    });

    return cleaned;
}

function updateCitations(sourceGroups) {
    const box = document.getElementById("citationsBox");
    lastSources = [];

    box.innerHTML = "";

    sourceGroups.forEach(group => {
        const heading = document.createElement("div");
        heading.innerHTML = `<h4>${group.label}</h4>`;
        box.appendChild(heading);

        group.sources.forEach(source => {
            const sourceIndex = lastSources.length;
            lastSources.push(source);

            const card = document.createElement("div");
            card.className = "citation-card";

            card.innerHTML = `
                <b>Source ${sourceIndex + 1}: ${source.source_id}</b>
                <div class="source-line"><b>Document:</b> ${source.document_name}</div>
                <div class="source-line"><b>Page:</b> ${source.page}</div>
                <div class="source-line"><b>Chunk:</b> ${source.chunk_id}</div>
                <div class="preview-text">${String(source.preview).slice(0, 260)}</div>
                <br>
                <button class="light" onclick="openSource(${sourceIndex})">Open source</button>
            `;

            box.appendChild(card);
        });
    });

    if (lastSources.length === 0) {
        box.textContent = "No source details returned.";
    }
}

function openSource(index) {
    const source = lastSources[index];

    if (!source) return;

    const sid = encodeURIComponent(source.source_id || "S1");
    const page = encodeURIComponent(source.page || "");
    const chunk = encodeURIComponent(source.chunk_id || "");

    window.open(`/documents/${source.document_id}/sources/${sid}/view?page=${page}&chunk_id=${chunk}`, "_blank");
}

async function sendMessage() {
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument();
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

    setStatus(compareDoc ? "Comparing..." : "Thinking...");
    document.getElementById("metricsBox").innerHTML = "";

    try {
        if (compareDoc) {
            const queryA = buildContextualQuery(userText, true);
            const queryB = buildContextualQuery(userText, true);

            const dataA = await callAsk(askPayload(queryA, doc.id));
            const dataB = await callAsk(askPayload(queryB, compareDoc.id));

            convo.push({
                role: "assistant",
                type: "compare",
                question: userText,
                docAName: doc.name || "Document A",
                docBName: compareDoc.name || "Document B",
                answerA: dataA.answer || "No answer from first document.",
                answerB: dataB.answer || "No answer from second document.",
                rawA: dataA,
                rawB: dataB,
                createdAt: new Date().toISOString()
            });

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

            const answer = data.answer || "I could not generate an answer.";

            convo.push({
                role: "assistant",
                content: answer,
                createdAt: new Date().toISOString(),
                raw: data
            });

            saveConversations();
            renderMessages();

            updateMetrics(data, doc.name || "Selected document");
            updateCitations([
                { label: doc.name || "Selected document", sources: buildSources(data, doc) }
            ]);

            setStatus("Ready");
        }

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

text += compare_app
hf_path.write_text(text, encoding="utf-8")

print("Phase 29 multi-document compare mode added.")
