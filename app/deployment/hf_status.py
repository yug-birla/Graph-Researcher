import os
from typing import Dict, Any

from app.core.config import settings


def get_deployment_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "deployment_target": "hugging_face_spaces",
        "port": os.getenv("PORT", "7860"),
        "message": "FastAPI app is running and ready for Hugging Face Spaces."
    }


def get_deployment_config() -> Dict[str, Any]:
    return {
        "deployment_target": "hugging_face_spaces",
        "llm_provider": settings.LLM_PROVIDER,
        "local_llm_enabled": settings.ENABLE_LOCAL_LLM,
        "hf_model": settings.HF_INFERENCE_MODEL,
        "hf_token_present": bool(settings.HF_API_TOKEN),
        "upload_dir": str(settings.UPLOAD_DIR),
        "processed_dir": str(settings.PROCESSED_DIR),
        "qdrant_path": str(settings.QDRANT_LOCAL_PATH),
        "evaluation_dir": str(settings.EVALUATION_DIR),
        "reranker_enabled": settings.ENABLE_RERANKER,
        "storage_warning": "Local Space storage can reset after restart unless persistent storage is attached."
    }


def get_demo_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphRAG Research Scientist</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1100px;
            margin: 35px auto;
            line-height: 1.6;
            padding: 0 20px;
            background: #f8fafc;
            color: #111827;
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #4b5563;
            margin-top: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 18px;
        }

        .card {
            border: 1px solid #d1d5db;
            border-radius: 14px;
            padding: 20px;
            background: white;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        .row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }

        input[type="text"], textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
        }

        textarea {
            min-height: 85px;
        }

        button {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 14px;
            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        button.secondary {
            background: #374151;
        }

        button.secondary:hover {
            background: #1f2937;
        }

        button.danger {
            background: #dc2626;
        }

        code {
            background: #e5e7eb;
            padding: 2px 6px;
            border-radius: 5px;
        }

        pre {
            background: #0f172a;
            color: #e5e7eb;
            padding: 15px;
            border-radius: 10px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .status {
            padding: 10px 12px;
            border-radius: 8px;
            background: #eff6ff;
            color: #1e40af;
            margin-top: 10px;
        }

        .success {
            background: #ecfdf5;
            color: #065f46;
        }

        .error {
            background: #fef2f2;
            color: #991b1b;
        }

        .small {
            font-size: 13px;
            color: #6b7280;
        }

        .answer-box {
            background: #f9fafb;
            border-left: 4px solid #2563eb;
            padding: 14px;
            border-radius: 8px;
            margin-top: 12px;
        }

        .pill {
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 12px;
            margin: 3px;
        }

        a {
            color: #2563eb;
        }
    </style>
</head>

<body>
    <h1>🧠 GraphRAG Research Scientist</h1>
    <p class="subtitle">
        Deployment demo for document upload, indexing, retrieval, citations, hosted LLM, and fallback answering.
    </p>

    <div class="grid">

        <div class="card">
            <h2>1. System Status</h2>
            <p class="small">
                Use this to quickly confirm that deployment and LLM provider are alive.
            </p>

            <div class="row">
                <button onclick="checkDeploymentHealth()">Check Deployment</button>
                <button onclick="checkLLMStatus()" class="secondary">Check LLM Status</button>
                <button onclick="openDocs()" class="secondary">Open Swagger Docs</button>
            </div>

            <div id="statusBox" class="status">Status output will appear here.</div>
        </div>

        <div class="card">
            <h2>2. Upload Document</h2>
            <p class="small">
                Upload a small PDF/TXT/DOCX/CSV file for demo. On Hugging Face free CPU, keep files small.
            </p>

            <input type="file" id="fileInput">
            <br><br>
            <button onclick="uploadDocument()">Upload</button>

            <div id="uploadStatus" class="status">No document uploaded yet.</div>

            <label><b>Current Document ID</b></label>
            <input type="text" id="documentIdInput" placeholder="document_id will appear here after upload">
        </div>

        <div class="card">
            <h2>3. Index Document</h2>
            <p class="small">
                Indexing creates embeddings and stores chunks in the vector database.
            </p>

            <button onclick="indexDocument()">Index Current Document</button>
            <div id="indexStatus" class="status">Document not indexed yet.</div>
        </div>

        <div class="card">
            <h2>4. Ask Question</h2>

            <label><b>Question</b></label>
            <textarea id="questionInput" placeholder="Example: What is RAG?"></textarea>

            <div class="row">
                <div style="flex: 1;">
                    <label><b>Retrieval Mode</b></label>
                    <select id="retrievalMode">
                        <option value="hybrid" selected>hybrid</option>
                        <option value="vector">vector</option>
                        <option value="keyword">keyword</option>
                    </select>
                </div>

                <div style="flex: 1;">
                    <label><b>Top K</b></label>
                    <select id="topK">
                        <option value="3">3</option>
                        <option value="5" selected>5</option>
                        <option value="8">8</option>
                        <option value="10">10</option>
                    </select>
                </div>
            </div>

            <br>

            <div class="row">
                <label>
                    <input type="checkbox" id="useReranker" checked>
                    Use reranker
                </label>

                <label>
                    <input type="checkbox" id="useLLM" checked>
                    Use hosted LLM
                </label>
            </div>

            <br>

            <button onclick="askQuestion()">Ask</button>
            <button onclick="clearAnswer()" class="secondary">Clear</button>

            <div id="answerStatus" class="status">Ask output will appear here.</div>

            <div id="answerBox" class="answer-box" style="display:none;"></div>

            <h3>Raw Response</h3>
            <pre id="rawResponse">{}</pre>
        </div>

    </div>

<script>
function showStatus(elementId, message, type = "normal") {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = "status";

    if (type === "success") {
        element.classList.add("success");
    }

    if (type === "error") {
        element.classList.add("error");
    }
}

function openDocs() {
    window.open("/docs", "_blank");
}

async function checkDeploymentHealth() {
    try {
        const response = await fetch("/deployment/health");
        const data = await response.json();

        showStatus(
            "statusBox",
            "Deployment healthy: " + JSON.stringify(data, null, 2),
            "success"
        );
    } catch (error) {
        showStatus("statusBox", "Deployment health failed: " + error, "error");
    }
}

async function checkLLMStatus() {
    try {
        const response = await fetch("/llm/status");
        const data = await response.json();

        showStatus(
            "statusBox",
            "LLM status: " + JSON.stringify(data, null, 2),
            "success"
        );
    } catch (error) {
        showStatus("statusBox", "LLM status failed: " + error, "error");
    }
}

async function uploadDocument() {
    const fileInput = document.getElementById("fileInput");

    if (!fileInput.files.length) {
        showStatus("uploadStatus", "Please choose a file first.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    showStatus("uploadStatus", "Uploading and processing document...");

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showStatus("uploadStatus", JSON.stringify(data, null, 2), "error");
            return;
        }

        const documentId =
            data.document_id ||
            data.metadata?.document_id ||
            data.status?.document_id ||
            "";

        if (documentId) {
            document.getElementById("documentIdInput").value = documentId;
        }

        showStatus(
            "uploadStatus",
            "Upload complete. Document ID: " + documentId,
            "success"
        );

        document.getElementById("rawResponse").textContent =
            JSON.stringify(data, null, 2);

    } catch (error) {
        showStatus("uploadStatus", "Upload failed: " + error, "error");
    }
}

async function indexDocument() {
    const documentId = document.getElementById("documentIdInput").value.trim();

    if (!documentId) {
        showStatus("indexStatus", "Please upload or paste a document_id first.", "error");
        return;
    }

    showStatus("indexStatus", "Indexing document...");

    try {
        const response = await fetch(`/documents/${documentId}/index`, {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            showStatus("indexStatus", JSON.stringify(data, null, 2), "error");
            return;
        }

        showStatus("indexStatus", "Indexing complete.", "success");

        document.getElementById("rawResponse").textContent =
            JSON.stringify(data, null, 2);

    } catch (error) {
        showStatus("indexStatus", "Indexing failed: " + error, "error");
    }
}

async function askQuestion() {
    const question = document.getElementById("questionInput").value.trim();
    const documentId = document.getElementById("documentIdInput").value.trim();

    if (!question) {
        showStatus("answerStatus", "Please enter a question.", "error");
        return;
    }

    if (!documentId) {
        showStatus("answerStatus", "Please upload/index a document first.", "error");
        return;
    }

    const payload = {
        query: question,
        document_id: documentId,
        top_k: Number(document.getElementById("topK").value),
        retrieval_mode: document.getElementById("retrievalMode").value,
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked
    };

    showStatus("answerStatus", "Thinking... retrieving sources and generating answer...");

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        document.getElementById("rawResponse").textContent =
            JSON.stringify(data, null, 2);

        if (!response.ok) {
            showStatus("answerStatus", JSON.stringify(data, null, 2), "error");
            return;
        }

        renderAnswer(data);

        showStatus(
            "answerStatus",
            "Answer generated. Strategy: " + data.answer_strategy,
            "success"
        );

    } catch (error) {
        showStatus("answerStatus", "Ask failed: " + error, "error");
    }
}

function renderAnswer(data) {
    const answerBox = document.getElementById("answerBox");
    answerBox.style.display = "block";

    const citations = data.citations || [];
    const sources = data.sources || [];

    let citationHtml = "";

    if (citations.length) {
        citationHtml = "<h3>Citations</h3>";

        for (const citation of citations.slice(0, 5)) {
            citationHtml += `
                <div class="pill">
                    ${citation.source_id || ""}
                    ${citation.source_file_name || ""}
                    page ${citation.page_number || "?"}
                </div>
            `;
        }
    }

    let sourceHtml = "";

    if (sources.length) {
        sourceHtml = "<h3>Top Sources</h3>";

        for (const source of sources.slice(0, 3)) {
            sourceHtml += `
                <p>
                    <b>${source.source_id || ""}</b>
                    ${source.source_file_name || ""}
                    page ${source.page_number || "?"}
                    <br>
                    <span class="small">${(source.content || "").slice(0, 350)}...</span>
                </p>
            `;
        }
    }

    answerBox.innerHTML = `
        <h3>Answer</h3>
        <p>${escapeHtml(data.answer || "")}</p>

        <h3>System Decision</h3>
        <p>
            <span class="pill">strategy: ${data.answer_strategy}</span>
            <span class="pill">used_llm: ${data.used_llm}</span>
            <span class="pill">used_reranker: ${data.used_reranker}</span>
            <span class="pill">mode: ${data.retrieval_mode}</span>
        </p>

        ${citationHtml}
        ${sourceHtml}
    `;
}

function clearAnswer() {
    document.getElementById("answerStatus").textContent = "Ask output will appear here.";
    document.getElementById("answerBox").style.display = "none";
    document.getElementById("rawResponse").textContent = "{}";
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
</script>

</body>
</html>
"""



def get_graphrag_demo_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>GraphRAG Demo - GraphRAG Research Scientist</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1150px;
            margin: 30px auto;
            padding: 0 20px;
            background: #f8fafc;
            color: #111827;
            line-height: 1.55;
        }

        h1 {
            margin-bottom: 4px;
        }

        .subtitle {
            color: #4b5563;
            margin-top: 0;
        }

        .card {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        .row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
        }

        textarea {
            min-height: 80px;
        }

        button {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 9px 13px;
            font-size: 14px;
            cursor: pointer;
            margin: 3px 0;
        }

        button:hover {
            background: #1d4ed8;
        }

        button.secondary {
            background: #374151;
        }

        button.secondary:hover {
            background: #1f2937;
        }

        button.green {
            background: #059669;
        }

        button.green:hover {
            background: #047857;
        }

        button.orange {
            background: #ea580c;
        }

        button.orange:hover {
            background: #c2410c;
        }

        pre {
            background: #0f172a;
            color: #e5e7eb;
            padding: 14px;
            border-radius: 10px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 520px;
        }

        .status {
            background: #eff6ff;
            color: #1e40af;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
        }

        .success {
            background: #ecfdf5;
            color: #065f46;
        }

        .error {
            background: #fef2f2;
            color: #991b1b;
        }

        .small {
            font-size: 13px;
            color: #6b7280;
        }

        .pill {
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 12px;
            margin: 3px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        @media (max-width: 850px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
    <h1>GraphRAG Demo Console</h1>
    <p class="subtitle">
        Test graph build, graph visualization, graph context, graph retrieval fusion, and GraphRAG evaluation.
    </p>

    <div class="card">
        <h2>1. Document Setup</h2>
        <p class="small">
            Paste a document_id from your uploaded/indexed document. If using Hugging Face, upload and index from /demo or /docs first.
        </p>

        <label><b>Document ID</b></label>
        <input id="documentId" placeholder="paste document_id here">

        <br><br>

        <label><b>Question</b></label>
        <textarea id="queryInput">What is RAG?</textarea>

        <div class="row">
            <button onclick="openSwagger()" class="secondary">Open Swagger</button>
            <button onclick="openBasicDemo()" class="secondary">Open Basic Demo</button>
            <button onclick="checkLLMStatus()" class="secondary">Check LLM Status</button>
        </div>

        <div id="setupStatus" class="status">Ready.</div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>2. Graph Actions</h2>
            <div class="row">
                <button onclick="buildGraph()" class="green">Build Graph</button>
                <button onclick="getGraphContext()">Graph Context</button>
                <button onclick="graphRetrieve()">Graph Retrieve</button>
                <button onclick="openGraphView()" class="orange">Open Graph View</button>
            </div>
            <p class="small">
                Build graph first, then test context/retrieve/view.
            </p>
        </div>

        <div class="card">
            <h2>3. Evaluation Actions</h2>
            <div class="row">
                <button onclick="runSingleFusionEval()">Single Fusion Eval</button>
                <button onclick="runBatchFusionEval()" class="green">Batch Fusion Eval</button>
            </div>
            <p class="small">
                Evaluation compares normal retrieval vs graph-guided retrieval vs fused retrieval.
            </p>
        </div>
    </div>

    <div class="card">
        <h2>4. Ask with GraphRAG</h2>

        <div class="grid">
            <div>
                <label><b>Retrieval mode</b></label>
                <select id="retrievalMode">
                    <option value="hybrid" selected>hybrid</option>
                    <option value="vector">vector</option>
                    <option value="keyword">keyword</option>
                </select>
            </div>

            <div>
                <label><b>Top K</b></label>
                <select id="topK">
                    <option value="3">3</option>
                    <option value="5" selected>5</option>
                    <option value="8">8</option>
                    <option value="10">10</option>
                </select>
            </div>
        </div>

        <br>

        <div class="row">
            <label><input type="checkbox" id="useReranker" checked> Use reranker</label>
            <label><input type="checkbox" id="useLLM" checked> Use LLM</label>
            <label><input type="checkbox" id="useGraph" checked> Use graph context</label>
            <label><input type="checkbox" id="useGraphRetrieval" checked> Use graph retrieval fusion</label>
        </div>

        <br>

        <button onclick="askGraphRAG()" class="green">Ask with GraphRAG</button>

        <div id="answerSummary" class="status">GraphRAG answer summary will appear here.</div>
    </div>

    <div class="card">
        <h2>5. Output Summary</h2>
        <div id="summaryBox">
            <span class="pill">No output yet</span>
        </div>
    </div>

    <div class="card">
        <h2>6. Raw JSON Output</h2>
        <pre id="rawOutput">{}</pre>
    </div>

<script>
function getDocumentId() {
    return document.getElementById("documentId").value.trim();
}

function getQuery() {
    return document.getElementById("queryInput").value.trim();
}

function showStatus(id, message, type = "normal") {
    const el = document.getElementById(id);
    el.textContent = message;
    el.className = "status";

    if (type === "success") {
        el.classList.add("success");
    }

    if (type === "error") {
        el.classList.add("error");
    }
}

function showRaw(data) {
    document.getElementById("rawOutput").textContent = JSON.stringify(data, null, 2);
}

function showSummaryFromAsk(data) {
    const fusion = data.retrieval_fusion || {};
    const graph = data.graph_context || {};

    document.getElementById("summaryBox").innerHTML = `
        <span class="pill">answer_strategy: ${data.answer_strategy}</span>
        <span class="pill">used_llm: ${data.used_llm}</span>
        <span class="pill">graph_used: ${data.graph_used}</span>
        <span class="pill">graph_available: ${graph.graph_available}</span>
        <span class="pill">fusion_used: ${fusion.fusion_used}</span>
        <span class="pill">graph_added: ${fusion.graph_added_count ?? "NA"}</span>
        <span class="pill">graph_supported: ${fusion.graph_supported_count ?? "NA"}</span>
    `;
}

function showSummaryFromEval(data) {
    const comparison = data.comparison || {};
    const stats = data.fusion_stats || {};

    document.getElementById("summaryBox").innerHTML = `
        <span class="pill">verdict: ${comparison.verdict}</span>
        <span class="pill">normal quality: ${comparison.normal_average_quality}</span>
        <span class="pill">graph quality: ${comparison.graph_average_quality}</span>
        <span class="pill">fused quality: ${comparison.fused_average_quality}</span>
        <span class="pill">delta: ${comparison.fusion_quality_delta}</span>
        <span class="pill">fusion_used: ${stats.fusion_used}</span>
    `;
}

function showSummaryFromBatch(data) {
    const summary = data.summary || {};

    document.getElementById("summaryBox").innerHTML = `
        <span class="pill">questions: ${summary.total_questions}</span>
        <span class="pill">improved: ${summary.fusion_improved_count}</span>
        <span class="pill">same: ${summary.fusion_same_count}</span>
        <span class="pill">worse: ${summary.fusion_worse_count}</span>
        <span class="pill">avg delta: ${summary.average_fusion_delta}</span>
        <span class="pill">verdict: ${summary.final_verdict}</span>
    `;
}

function openSwagger() {
    window.open("/docs", "_blank");
}

function openBasicDemo() {
    window.open("/demo", "_blank");
}

async function checkLLMStatus() {
    try {
        const response = await fetch("/llm/status");
        const data = await response.json();

        showRaw(data);
        showStatus("setupStatus", "LLM status loaded.", "success");
    } catch (error) {
        showStatus("setupStatus", "LLM status failed: " + error, "error");
    }
}

async function buildGraph() {
    const documentId = getDocumentId();

    if (!documentId) {
        showStatus("setupStatus", "Paste document_id first.", "error");
        return;
    }

    showStatus("setupStatus", "Building graph...");

    try {
        const response = await fetch(`/documents/${documentId}/graph/build`, {
            method: "POST"
        });

        const data = await response.json();

        showRaw(data);

        if (!response.ok) {
            showStatus("setupStatus", "Graph build failed.", "error");
            return;
        }

        document.getElementById("summaryBox").innerHTML = `
            <span class="pill">entities: ${data.total_entities}</span>
            <span class="pill">relations: ${data.total_relations}</span>
            <span class="pill">status: ${data.status}</span>
        `;

        showStatus("setupStatus", "Graph built successfully.", "success");

    } catch (error) {
        showStatus("setupStatus", "Graph build error: " + error, "error");
    }
}

async function getGraphContext() {
    const documentId = getDocumentId();
    const query = encodeURIComponent(getQuery());

    if (!documentId || !query) {
        showStatus("setupStatus", "Paste document_id and question first.", "error");
        return;
    }

    try {
        const response = await fetch(`/documents/${documentId}/graph/context?query=${query}`);
        const data = await response.json();

        showRaw(data);

        document.getElementById("summaryBox").innerHTML = `
            <span class="pill">graph_available: ${data.graph_available}</span>
            <span class="pill">entities: ${(data.matched_entities || []).length}</span>
            <span class="pill">relations: ${(data.matched_relations || []).length}</span>
        `;

        showStatus("setupStatus", "Graph context loaded.", "success");

    } catch (error) {
        showStatus("setupStatus", "Graph context failed: " + error, "error");
    }
}

async function graphRetrieve() {
    const documentId = getDocumentId();
    const query = encodeURIComponent(getQuery());

    if (!documentId || !query) {
        showStatus("setupStatus", "Paste document_id and question first.", "error");
        return;
    }

    try {
        const response = await fetch(`/documents/${documentId}/graph/retrieve?query=${query}&top_k=5`);
        const data = await response.json();

        showRaw(data);

        document.getElementById("summaryBox").innerHTML = `
            <span class="pill">status: ${data.status}</span>
            <span class="pill">returned_chunks: ${data.returned_chunks}</span>
            <span class="pill">matched_entities: ${data.matched_entity_count}</span>
            <span class="pill">matched_relations: ${data.matched_relation_count}</span>
        `;

        showStatus("setupStatus", "Graph retrieval loaded.", "success");

    } catch (error) {
        showStatus("setupStatus", "Graph retrieve failed: " + error, "error");
    }
}

function openGraphView() {
    const documentId = getDocumentId();

    if (!documentId) {
        showStatus("setupStatus", "Paste document_id first.", "error");
        return;
    }

    window.open(`/documents/${documentId}/graph/view`, "_blank");
}

async function runSingleFusionEval() {
    const documentId = getDocumentId();
    const query = encodeURIComponent(getQuery());

    if (!documentId || !query) {
        showStatus("setupStatus", "Paste document_id and question first.", "error");
        return;
    }

    showStatus("setupStatus", "Running single fusion evaluation...");

    try {
        const response = await fetch(`/documents/${documentId}/evaluation/graph-fusion?query=${query}&top_k=5&retrieval_mode=hybrid&use_reranker=true`);
        const data = await response.json();

        showRaw(data);
        showSummaryFromEval(data);
        showStatus("setupStatus", "Single fusion evaluation complete.", "success");

    } catch (error) {
        showStatus("setupStatus", "Single fusion eval failed: " + error, "error");
    }
}

async function runBatchFusionEval() {
    const documentId = getDocumentId();

    if (!documentId) {
        showStatus("setupStatus", "Paste document_id first.", "error");
        return;
    }

    showStatus("setupStatus", "Running batch fusion evaluation...");

    try {
        const response = await fetch(`/documents/${documentId}/evaluation/graph-fusion/batch?top_k=5&retrieval_mode=hybrid&use_reranker=true&compact=true`);
        const data = await response.json();

        showRaw(data);
        showSummaryFromBatch(data);
        showStatus("setupStatus", "Batch fusion evaluation complete.", "success");

    } catch (error) {
        showStatus("setupStatus", "Batch eval failed: " + error, "error");
    }
}

async function askGraphRAG() {
    const documentId = getDocumentId();
    const query = getQuery();

    if (!documentId || !query) {
        showStatus("answerSummary", "Paste document_id and question first.", "error");
        return;
    }

    const payload = {
        query: query,
        document_id: documentId,
        top_k: Number(document.getElementById("topK").value),
        retrieval_mode: document.getElementById("retrievalMode").value,
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked,
        use_graph: document.getElementById("useGraph").checked,
        graph_entity_limit: 8,
        use_graph_retrieval: document.getElementById("useGraphRetrieval").checked,
        graph_retrieval_top_k: 5
    };

    showStatus("answerSummary", "Asking GraphRAG pipeline...");

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        showRaw(data);

        if (!response.ok) {
            showStatus("answerSummary", "Ask failed.", "error");
            return;
        }

        showSummaryFromAsk(data);

        showStatus(
            "answerSummary",
            "Answer: " + (data.answer || "").slice(0, 400),
            "success"
        );

    } catch (error) {
        showStatus("answerSummary", "Ask failed: " + error, "error");
    }
}
</script>

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
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: #f8fafc;
            color: #111827;
        }

        .app {
            display: grid;
            grid-template-columns: 280px 1fr 360px;
            height: 100vh;
        }

        .sidebar {
            background: #0f172a;
            color: white;
            padding: 16px;
            overflow-y: auto;
        }

        .sidebar h2 {
            margin-top: 0;
            font-size: 20px;
        }

        .new-chat {
            width: 100%;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 11px;
            cursor: pointer;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .conversation {
            padding: 10px;
            border-radius: 9px;
            cursor: pointer;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.07);
            font-size: 14px;
        }

        .conversation.active {
            background: #2563eb;
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
            gap: 10px;
            align-items: center;
        }

        .topbar input {
            flex: 1;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
        }

        .status-pill {
            font-size: 12px;
            padding: 6px 9px;
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

        button {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 16px;
            cursor: pointer;
            font-size: 14px;
        }

        button:hover {
            background: #1d4ed8;
        }

        button.secondary {
            background: #334155;
        }

        button.green {
            background: #059669;
        }

        .right-panel {
            background: white;
            border-left: 1px solid #e5e7eb;
            padding: 16px;
            overflow-y: auto;
        }

        .panel-section {
            margin-bottom: 18px;
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

        .citation-card {
            border: 1px solid #e5e7eb;
            background: #f8fafc;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 13px;
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

        .small {
            font-size: 12px;
            color: #64748b;
        }

        .hidden {
            display: none;
        }

        @media (max-width: 1050px) {
            .app {
                grid-template-columns: 240px 1fr;
            }

            .right-panel {
                display: none;
            }
        }

        @media (max-width: 760px) {
            .app {
                grid-template-columns: 1fr;
            }

            .sidebar {
                display: none;
            }
        }
    </style>
</head>

<body>
<div class="app">

    <aside class="sidebar">
        <h2>GraphResearcher</h2>
        <button class="new-chat" onclick="newChat()">+ New chat</button>

        <div class="small" style="margin-bottom: 10px;">Conversations</div>
        <div id="conversationList"></div>

        <hr style="border-color: rgba(255,255,255,0.15); margin: 18px 0;">

        <button class="new-chat secondary" onclick="window.open('/graphrag-demo','_blank')">GraphRAG Console</button>
        <button class="new-chat secondary" onclick="window.open('/docs','_blank')">Swagger Docs</button>
    </aside>

    <main class="main">
        <div class="topbar">
            <input id="documentId" placeholder="Paste document_id here">
            <span id="appStatus" class="status-pill">Ready</span>
        </div>

        <div id="messages" class="messages"></div>

        <div class="composer">
            <div class="composer-box">
                <textarea id="messageInput" placeholder="Ask anything about your document..." onkeydown="handleKeyDown(event)"></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="small" style="margin-top: 8px;">
                Tip: ask follow-ups like “explain it simply” or “how is it different?” The app sends recent chat context with your question.
            </div>
        </div>
    </main>

    <aside class="right-panel">
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
    </aside>

</div>

<script>
let conversations = JSON.parse(localStorage.getItem("graphrag_conversations") || "[]");
let activeConversationId = localStorage.getItem("graphrag_active_conversation");

function saveState() {
    localStorage.setItem("graphrag_conversations", JSON.stringify(conversations));
    if (activeConversationId) {
        localStorage.setItem("graphrag_active_conversation", activeConversationId);
    }
}

function getActiveConversation() {
    let convo = conversations.find(c => c.id === activeConversationId);

    if (!convo) {
        convo = {
            id: crypto.randomUUID(),
            title: "New chat",
            messages: [],
            createdAt: new Date().toISOString()
        };

        conversations.unshift(convo);
        activeConversationId = convo.id;
        saveState();
    }

    return convo;
}

function newChat() {
    const convo = {
        id: crypto.randomUUID(),
        title: "New chat",
        messages: [],
        createdAt: new Date().toISOString()
    };

    conversations.unshift(convo);
    activeConversationId = convo.id;
    saveState();
    renderConversations();
    renderMessages();
}

function selectConversation(id) {
    activeConversationId = id;
    saveState();
    renderConversations();
    renderMessages();
}

function renderConversations() {
    const list = document.getElementById("conversationList");
    list.innerHTML = "";

    conversations.forEach(convo => {
        const div = document.createElement("div");
        div.className = "conversation" + (convo.id === activeConversationId ? " active" : "");
        div.textContent = convo.title || "New chat";
        div.onclick = () => selectConversation(convo.id);
        list.appendChild(div);
    });
}

function renderMessages() {
    const convo = getActiveConversation();
    const box = document.getElementById("messages");
    box.innerHTML = "";

    if (convo.messages.length === 0) {
        box.innerHTML = `
            <div class="message assistant">
                <div class="bubble">
                    Hi, I am your GraphRAG research assistant. Paste a document_id above and ask a question.
                    I can answer with citations, graph context, and retrieval fusion.
                </div>
            </div>
        `;
        return;
    }

    convo.messages.forEach(msg => {
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

function setStatus(text) {
    document.getElementById("appStatus").textContent = text;
}

function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function buildContextualQuery(currentQuestion) {
    const convo = getActiveConversation();
    const recentMessages = convo.messages.slice(-6);

    if (recentMessages.length === 0) {
        return currentQuestion;
    }

    const context = recentMessages
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
            <span class="small">${citation.text_preview || citation.preview || ""}</span>
        `;

        box.appendChild(card);
    });
}

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const userText = input.value.trim();
    const documentId = document.getElementById("documentId").value.trim();

    if (!userText) return;

    if (!documentId) {
        alert("Paste document_id first.");
        return;
    }

    const convo = getActiveConversation();

    if (convo.title === "New chat") {
        convo.title = userText.slice(0, 35);
    }

    convo.messages.push({
        role: "user",
        content: userText,
        createdAt: new Date().toISOString()
    });

    input.value = "";
    saveState();
    renderConversations();
    renderMessages();

    setStatus("Thinking...");

    const contextualQuery = buildContextualQuery(userText);

    const payload = {
        query: contextualQuery,
        document_id: documentId,
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

        convo.messages.push({
            role: "assistant",
            content: answer,
            createdAt: new Date().toISOString(),
            raw: data
        });

        saveState();
        renderMessages();
        updateMetrics(data);
        updateCitations(data);
        setStatus("Ready");

    } catch (error) {
        convo.messages.push({
            role: "assistant",
            content: "Error: " + error.message,
            createdAt: new Date().toISOString()
        });

        saveState();
        renderMessages();
        setStatus("Error");
    }
}

async function buildGraph() {
    const documentId = document.getElementById("documentId").value.trim();

    if (!documentId) {
        alert("Paste document_id first.");
        return;
    }

    setStatus("Building graph...");

    try {
        const response = await fetch(`/documents/${documentId}/graph/build`, {
            method: "POST"
        });

        const data = await response.json();

        document.getElementById("metricsBox").innerHTML = `
            <span class="metric">graph status: ${data.status || "done"}</span>
            <span class="metric">entities: ${data.total_entities ?? data.entity_count ?? "NA"}</span>
            <span class="metric">relations: ${data.total_relations ?? data.relation_count ?? "NA"}</span>
        `;

        setStatus("Graph built");

    } catch (error) {
        setStatus("Graph error");
        alert("Graph build failed: " + error.message);
    }
}

function openGraph() {
    const documentId = document.getElementById("documentId").value.trim();

    if (!documentId) {
        alert("Paste document_id first.");
        return;
    }

    window.open(`/documents/${documentId}/graph/view`, "_blank");
}

if (!activeConversationId || conversations.length === 0) {
    newChat();
} else {
    renderConversations();
    renderMessages();
}
</script>

</body>
</html>
"""
