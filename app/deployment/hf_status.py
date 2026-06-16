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



# =====================================================
# Phase 27 override: clean user-facing home and app UI
# =====================================================

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
            font-weight: 900;
            font-size: 23px;
            letter-spacing: -0.5px;
        }

        .nav a {
            text-decoration: none;
            color: #334155;
            margin-left: 22px;
            font-weight: 700;
        }

        .hero {
            min-height: calc(100vh - 72px);
            display: grid;
            grid-template-columns: 1fr 0.9fr;
            gap: 52px;
            align-items: center;
            padding: 64px 72px;
        }

        .badge {
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: 800;
            font-size: 13px;
            margin-bottom: 18px;
        }

        h1 {
            font-size: 58px;
            line-height: 1.04;
            margin: 0 0 20px;
            letter-spacing: -2px;
        }

        .hero p {
            font-size: 19px;
            line-height: 1.7;
            color: #475569;
            max-width: 710px;
        }

        .actions {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 32px;
        }

        .btn {
            display: inline-block;
            text-decoration: none;
            background: #2563eb;
            color: white;
            padding: 14px 22px;
            border-radius: 12px;
            font-weight: 800;
        }

        .btn.dark {
            background: #0f172a;
        }

        .preview {
            background: #0f172a;
            color: white;
            border-radius: 26px;
            padding: 24px;
            box-shadow: 0 28px 70px rgba(15,23,42,0.24);
        }

        .mini-top {
            display: flex;
            gap: 8px;
            margin-bottom: 18px;
        }

        .dot {
            width: 12px;
            height: 12px;
            background: #64748b;
            border-radius: 50%;
        }

        .preview-card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 14px;
        }

        .preview-card b {
            color: #bfdbfe;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            padding: 0 72px 58px;
        }

        .feature {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 24px;
        }

        .feature p {
            color: #64748b;
            line-height: 1.6;
        }

        @media(max-width: 950px) {
            .nav { padding: 0 22px; }
            .hero {
                grid-template-columns: 1fr;
                padding: 42px 24px;
            }
            h1 { font-size: 42px; }
            .features {
                grid-template-columns: 1fr;
                padding: 0 24px 44px;
            }
        }
    </style>
</head>

<body>
    <div class="nav">
        <div class="brand">GraphResearcher</div>
        <div>
            <a href="/app">Launch App</a>
        </div>
    </div>

    <section class="hero">
        <div>
            <div class="badge">Document Chat + GraphRAG</div>
            <h1>Upload documents. Ask questions. Verify every answer.</h1>
            <p>
                GraphResearcher lets users chat with PDFs and reports using citation-grounded retrieval,
                graph context, and source-backed answers. No document IDs, no Swagger, no developer workflow.
            </p>

            <div class="actions">
                <a class="btn" href="/app">Start Chatting</a>
                <a class="btn dark" href="/deployment/health">System Health</a>
            </div>
        </div>

        <div class="preview">
            <div class="mini-top">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>

            <div class="preview-card">
                <b>1. Upload</b><br>
                Add a PDF or document from the app sidebar.
            </div>

            <div class="preview-card">
                <b>2. Chat</b><br>
                Ask natural questions like ChatGPT or Gemini.
            </div>

            <div class="preview-card">
                <b>3. Verify</b><br>
                See document name, page number, source ID, and evidence preview.
            </div>
        </div>
    </section>

    <section class="features">
        <div class="feature">
            <h3>Simple workspace</h3>
            <p>Users upload and select documents normally. Internal IDs stay hidden.</p>
        </div>

        <div class="feature">
            <h3>Grounded answers</h3>
            <p>Answers are generated from retrieved evidence and source citations.</p>
        </div>

        <div class="feature">
            <h3>GraphRAG inside</h3>
            <p>Graph context and retrieval fusion run behind the scenes for better document reasoning.</p>
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
            max-width: 880px;
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

        .empty {
            max-width: 720px;
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

        .citation-card b {
            color: #0f172a;
        }

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

        .modal {
            position: fixed;
            inset: 0;
            background: rgba(15,23,42,0.55);
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
            z-index: 50;
        }

        .modal-box {
            background: white;
            width: min(760px, 96vw);
            max-height: 82vh;
            overflow-y: auto;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.28);
        }

        .modal-pre {
            background: #0f172a;
            color: #e5e7eb;
            padding: 14px;
            border-radius: 12px;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 13px;
        }

        .danger-zone {
            border-top: 1px solid #e5e7eb;
            padding-top: 14px;
        }

        @media (max-width: 1100px) {
            .app { grid-template-columns: 290px 1fr; }
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
            <p class="small">Upload a PDF/document and start chatting. No document ID needed.</p>
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
                <textarea id="messageInput" placeholder="Ask anything about the selected document..." onkeydown="handleKeyDown(event)"></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="small" style="margin-top: 8px;">
                Example: “Summarize this”, “Explain step by step”, “What are the key points?”, “Give evidence”.
            </div>
        </div>
    </main>

    <aside class="right-panel">
        <div class="panel-section">
            <h3>Selected Document</h3>
            <div id="docDetails" class="small">No document selected.</div>
        </div>

        <div class="panel-section">
            <h3>Answer Style</h3>
            <select id="answerStyle">
                <option value="detailed" selected>Detailed</option>
                <option value="step_by_step">Step-by-step</option>
                <option value="concise">Concise</option>
                <option value="research">Research style</option>
            </select>
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
            <h3>Sources</h3>
            <div id="citationsBox" class="small">Sources will appear here after an answer.</div>
        </div>

        <div class="panel-section danger-zone">
            <h3>Danger Zone</h3>
            <button class="red" onclick="deleteSelectedDocument()">Delete Selected Document</button>
        </div>
    </aside>
</div>

<div id="sourceModal" class="modal">
    <div class="modal-box">
        <h2 id="modalTitle">Source details</h2>
        <div id="modalBody"></div>
        <br>
        <button onclick="closeSourceModal()">Close</button>
    </div>
</div>

<script>
let documents = JSON.parse(localStorage.getItem("graphrag_documents") || "[]");
let selectedDocumentId = localStorage.getItem("graphrag_selected_document_id") || null;
let conversations = JSON.parse(localStorage.getItem("graphrag_conversations_v2") || "{}");
let lastSources = [];

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

    title.innerHTML = `${doc.name || "Untitled document"} <span>Ready for document chat.</span>`;

    details.innerHTML = `
        <b>Name:</b> ${doc.name || "Untitled"}<br>
        <b>Status:</b> ${doc.status || "uploaded"}<br>
        <b>Graph:</b> ${doc.graphStatus || "not built"}<br>
        <b>Uploaded:</b> ${doc.uploadedAt || "unknown"}
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
                <p>No document ID needed. Upload a file from the left sidebar, then chat normally.</p>
            </div>
        `;
        return;
    }

    const convo = getConversation();

    if (convo.length === 0) {
        box.innerHTML = `
            <div class="empty">
                <h1>Chat with ${doc.name || "your document"}</h1>
                <p>Ask a question below. Answers will include citation-backed sources.</p>
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

    if (!confirm(`Delete "${doc.name}" from this workspace?`)) return;

    setStatus("Deleting...");

    await tryEndpoints(
        [`/documents/${doc.id}`, `/documents/${doc.id}/delete`, `/api/documents/${doc.id}`],
        () => ({ method: "DELETE" })
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

function getAnswerStyleInstruction() {
    const style = document.getElementById("answerStyle").value;

    if (style === "concise") {
        return "Answer concisely, but still include citations after important claims.";
    }

    if (style === "step_by_step") {
        return "Answer step by step. Use numbered steps. Explain the reasoning clearly. Include citations after key points.";
    }

    if (style === "research") {
        return "Answer in a research-style format: direct answer, evidence, interpretation, limitations. Include citations after key claims.";
    }

    return "Answer in a detailed, useful, and source-grounded format. Use this structure: Direct answer, Key points, Evidence from sources, and Limitations. Mention citations after important claims.";
}

function buildContextualQuery(currentQuestion) {
    const convo = getConversation().slice(-6);
    const instruction = getAnswerStyleInstruction();

    let context = "";

    if (convo.length > 0) {
        context = convo
            .map(m => `${m.role}: ${m.content}`)
            .join("\\n");
    }

    return `${instruction}\\n\\nConversation so far:\\n${context}\\n\\nCurrent user question:\\n${currentQuestion}`;
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

function buildSources(data) {
    const selectedDoc = getSelectedDocument();
    const sources = [];

    const citations = data.citations || [];
    citations.forEach(c => sources.push(c));

    const fused = data.retrieval_fusion?.fused_results || [];
    fused.forEach(r => sources.push(r));

    const normalSources = data.sources || data.source_chunks || data.retrieved_sources || [];
    normalSources.forEach(s => sources.push(s));

    const seen = new Set();
    const cleaned = [];

    sources.forEach((src, index) => {
        const sourceId = valueFrom(src, ["source_id", "id", "citation_id"], "S" + (index + 1));
        const chunkId = valueFrom(src, ["chunk_id", "source_chunk_id", "chunk"], sourceId);
        const key = sourceId + "|" + chunkId;

        if (seen.has(key)) return;
        seen.add(key);

        cleaned.push({
            source_id: sourceId,
            document_name: valueFrom(src, ["document_name", "source_file_name", "file_name", "filename", "document_title"], selectedDoc?.name || "Selected document"),
            page: valueFrom(src, ["page_number", "page", "page_no"], "Not available"),
            chunk_id: chunkId,
            preview: valueFrom(src, ["text_preview", "preview", "chunk_preview", "content_preview", "text", "content"], "Preview not available"),
            raw: src
        });
    });

    return cleaned;
}

function updateCitations(data) {
    const box = document.getElementById("citationsBox");
    lastSources = buildSources(data);

    if (lastSources.length === 0) {
        box.textContent = "No source details returned.";
        return;
    }

    box.innerHTML = "";

    lastSources.forEach((source, index) => {
        const card = document.createElement("div");
        card.className = "citation-card";

        card.innerHTML = `
            <b>Source ${index + 1}: ${source.source_id}</b>
            <div class="source-line"><b>Document:</b> ${source.document_name}</div>
            <div class="source-line"><b>Page:</b> ${source.page}</div>
            <div class="source-line"><b>Chunk:</b> ${source.chunk_id}</div>
            <div class="preview-text">${String(source.preview).slice(0, 260)}</div>
            <br>
            <button class="light" onclick="openSourceModal(${index})">Open source details</button>
        `;

        box.appendChild(card);
    });
}

function openSourceModal(index) {
    const source = lastSources[index];

    if (!source) return;

    document.getElementById("modalTitle").textContent = `Source ${index + 1}: ${source.source_id}`;

    document.getElementById("modalBody").innerHTML = `
        <p><b>Document:</b> ${source.document_name}</p>
        <p><b>Page:</b> ${source.page}</p>
        <p><b>Chunk:</b> ${source.chunk_id}</p>
        <h3>Preview</h3>
        <div class="modal-pre">${String(source.preview)}</div>
        <h3>Raw source metadata</h3>
        <div class="modal-pre">${JSON.stringify(source.raw, null, 2)}</div>
    `;

    document.getElementById("sourceModal").style.display = "flex";
}

function closeSourceModal() {
    document.getElementById("sourceModal").style.display = "none";
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
        top_k: 8,
        retrieval_mode: "hybrid",
        use_reranker: document.getElementById("useReranker").checked,
        use_llm: document.getElementById("useLLM").checked,
        use_graph: document.getElementById("useGraph").checked,
        graph_entity_limit: 12,
        use_graph_retrieval: document.getElementById("useGraphRetrieval").checked,
        graph_retrieval_top_k: 6
    };

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
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

    return "Answer in a detailed, useful, and source-grounded format. Use this structure: Direct answer, Key points, Evidence from sources, and Limitations. Mention citations after important claims.";
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



# =====================================================
# Phase 33 override: clean retrieval query + stale cache tools
# =====================================================

try:
    _phase33_previous_get_product_app_html = get_product_app_html
except NameError:
    _phase33_previous_get_product_app_html = None


def get_product_app_html() -> str:
    if _phase33_previous_get_product_app_html is None:
        return "<h1>GraphResearcher App</h1><p>App UI is unavailable.</p>"

    html = _phase33_previous_get_product_app_html()

    if "Clear Workspace Cache" not in html:
        buttons = """
        <button class="full secondary" onclick="reindexSelectedDocument()">Re-index Selected</button>
        <button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>
        """

        html = html.replace("</aside>", buttons + "\n    </aside>", 1)

    js = r"""
<script>
/*
Phase 33 fix: clean retrieval query.
Old issue: app was sending answer-style instructions + full conversation as the search query.
That polluted semantic retrieval.
Now retrieval receives only the clean user question.
For short follow-ups, it attaches only recent user questions.
*/

function buildContextualQuery(currentQuestion, compareMode = false) {
    const cleanQuestion = String(currentQuestion || "").trim();

    if (!cleanQuestion) {
        return cleanQuestion;
    }

    let previousUserQuestions = [];

    try {
        previousUserQuestions = getConversation()
            .filter(m => m.role === "user")
            .slice(-2)
            .map(m => String(m.content || "").trim())
            .filter(Boolean);
    } catch (error) {
        previousUserQuestions = [];
    }

    const wordCount = cleanQuestion.split(/\s+/).filter(Boolean).length;
    const looksLikeFollowUp = wordCount <= 8;

    if (looksLikeFollowUp && previousUserQuestions.length > 0) {
        return previousUserQuestions.join(" ") + " " + cleanQuestion;
    }

    return cleanQuestion;
}

async function reindexSelectedDocument() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert("Select a document first.");
        return;
    }

    setStatus("Re-indexing...");

    try {
        await autoIndexDocument(doc.id);
        await buildGraph(false);

        doc.status = "indexed";
        saveDocuments();
        renderDocuments();

        setStatus("Re-indexed");
        alert("Re-index attempt complete. Ask again now.");
    } catch (error) {
        setStatus("Re-index failed");
        alert("Re-index failed. If Hugging Face rebuilt recently, clear cache and upload the document again.");
    }
}

function clearWorkspaceCache() {
    const ok = confirm(
        "Clear saved browser document list and chat history? Use this when Hugging Face rebuilds and old documents show as indexed but answers say no sources found."
    );

    if (!ok) return;

    localStorage.removeItem("graphrag_documents");
    localStorage.removeItem("graphrag_selected_document_id");
    localStorage.removeItem("graphrag_conversations");
    localStorage.removeItem("graphrag_conversations_v2");
    localStorage.removeItem("graphrag_conversations_v3");

    documents = [];
    selectedDocumentId = null;
    conversations = {};

    renderDocuments();
    renderMessages();
    setStatus("Cache cleared");

    alert("Workspace cache cleared. Upload the document again.");
}
</script>
"""

    if "Phase 33 fix: clean retrieval query" not in html:
        html = html.replace("</body>", js + "\n</body>")

    html = html.replace(
        "Upload documents, select one, and chat. You can also compare two documents.",
        "Upload documents, select one, and chat. If answers say no sources found after rebuild, clear cache and re-upload."
    )

    html = html.replace(
        "Upload a PDF/document and start chatting. No document ID needed.",
        "Upload a PDF/document and start chatting. If Hugging Face rebuilt, old cached documents may need re-upload."
    )

    return html



# =====================================================
# Phase 34 override: professional answer rendering
# =====================================================

try:
    _phase34_previous_get_product_app_html = get_product_app_html
except NameError:
    _phase34_previous_get_product_app_html = None


def get_product_app_html() -> str:
    if _phase34_previous_get_product_app_html is None:
        return "<h1>GraphResearcher App</h1><p>App UI is unavailable.</p>"

    html = _phase34_previous_get_product_app_html()

    css = """
<style>
.answer-card {
    line-height: 1.72;
}

.answer-card h2 {
    margin: 0 0 10px;
    font-size: 18px;
    color: #0f172a;
}

.answer-card h3 {
    margin: 18px 0 8px;
    font-size: 15px;
    color: #1d4ed8;
}

.answer-card p {
    margin: 8px 0;
}

.answer-card ol,
.answer-card ul {
    padding-left: 22px;
    margin: 8px 0;
}

.answer-card li {
    margin-bottom: 8px;
}

.evidence-box {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 11px;
    margin-top: 9px;
    font-size: 13px;
    color: #475569;
}

.source-chip {
    display: inline-block;
    background: #eef2ff;
    color: #3730a3;
    padding: 3px 7px;
    border-radius: 999px;
    font-size: 12px;
    margin: 2px;
    font-weight: 700;
}

.answer-warning {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
    padding: 10px;
    border-radius: 12px;
    margin: 10px 0;
}
</style>
"""

    if "answer-card" not in html:
        html = html.replace("</head>", css + "\n</head>")

    js = """
<script>
/*
Phase 34:
Render answers like a real ChatGPT-style app.
The backend may return plain text, but the UI now converts it into:
Direct answer, structured points, evidence, and source grounding.
*/

function htmlEscapePhase34(value) {
    return String(value || '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('\"', '&quot;');
}

function stripHtmlPhase34(value) {
    const div = document.createElement('div');
    div.innerHTML = value || '';
    return div.textContent || div.innerText || '';
}

function answerLooksWeakPhase34(answer) {
    const text = String(answer || '').trim();
    const words = text.split(/\\s+/).filter(Boolean);

    if (words.length < 110) return true;
    if (text.toLowerCase().includes('i could not find relevant indexed sources')) return true;
    if (!text.includes('\\n') && words.length < 170) return true;

    return false;
}

function splitIntoPointsPhase34(text) {
    const cleaned = String(text || '')
        .replace(/\\s+/g, ' ')
        .trim();

    if (!cleaned) return [];

    const numbered = cleaned.split(/(?=\\b\\d+\\.\\s+)/).map(x => x.trim()).filter(Boolean);

    if (numbered.length >= 2) {
        return numbered;
    }

    return cleaned
        .split(/(?<=[.!?])\\s+/)
        .map(x => x.trim())
        .filter(x => x.length > 20)
        .slice(0, 8);
}

function renderPlainAnswerPhase34(answer) {
    const escaped = htmlEscapePhase34(answer);

    let html = escaped;

    html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>');

    const lines = html.split('\\n').map(x => x.trim()).filter(Boolean);

    if (lines.length <= 1) {
        return '<p>' + html + '</p>';
    }

    let out = '';

    lines.forEach(line => {
        if (/^\\d+\\.\\s+/.test(line)) {
            out += '<li>' + line.replace(/^\\d+\\.\\s+/, '') + '</li>';
        } else if (/^[-*]\\s+/.test(line)) {
            out += '<li>' + line.replace(/^[-*]\\s+/, '') + '</li>';
        } else {
            out += '<p>' + line + '</p>';
        }
    });

    if (out.includes('<li>')) {
        out = '<ol>' + out + '</ol>';
    }

    return out;
}

function buildSourceGroundingPhase34(data, doc) {
    let sources = [];

    try {
        sources = buildSources(data, doc).slice(0, 5);
    } catch (error) {
        sources = [];
    }

    if (!sources.length) {
        return {
            html: '<div class=\"answer-warning\">No source metadata was returned with this answer. If this document was uploaded before a Hugging Face rebuild, clear cache and re-upload it.</div>',
            sources: []
        };
    }

    let html = '';

    sources.forEach((source, index) => {
        const label = htmlEscapePhase34(source.source_id || ('S' + (index + 1)));
        const page = htmlEscapePhase34(source.page || 'Not available');
        const chunk = htmlEscapePhase34(source.chunk_id || 'Not available');
        const preview = htmlEscapePhase34(String(source.preview || '').slice(0, 320));

        html += `
            <div class="evidence-box">
                <b>[${label}]</b>
                <span class="source-chip">Page: ${page}</span>
                <span class="source-chip">Chunk: ${chunk}</span>
                <div style="margin-top:6px;">${preview}</div>
            </div>
        `;
    });

    return { html, sources };
}

function formatProfessionalAnswerPhase34(question, data, doc) {
    const rawAnswer = String(data.answer || 'I could not generate an answer.').trim();
    const grounding = buildSourceGroundingPhase34(data, doc);
    const weak = answerLooksWeakPhase34(rawAnswer);

    const questionLower = String(question || '').toLowerCase();
    const wantsSteps =
        questionLower.includes('step') ||
        questionLower.includes('sequential') ||
        questionLower.includes('build') ||
        questionLower.includes('procedure') ||
        questionLower.includes('starting point');

    let html = '<div class="answer-card">';

    if (rawAnswer.toLowerCase().includes('i could not find relevant indexed sources')) {
        html += '<h2>I could not find indexed evidence for this question</h2>';
        html += '<div class="answer-warning">This usually means the browser still remembers an old document, but the Hugging Face backend lost its uploaded/indexed files after rebuild. Use Clear Workspace Cache, re-upload the document, then ask again.</div>';
        html += '</div>';
        return html;
    }

    if (wantsSteps) {
        html += '<h2>Step-by-step answer</h2>';
    } else {
        html += '<h2>Answer</h2>';
    }

    if (weak) {
        const points = splitIntoPointsPhase34(rawAnswer);

        html += '<h3>Direct answer</h3>';
        html += '<p>' + htmlEscapePhase34(points[0] || rawAnswer) + '</p>';

        if (points.length > 1) {
            html += '<h3>Detailed points</h3><ol>';

            points.slice(0, 8).forEach(point => {
                let cleaned = point.replace(/^\\d+\\.\\s+/, '');
                html += '<li>' + htmlEscapePhase34(cleaned) + '</li>';
            });

            html += '</ol>';
        }

        html += '<h3>Evidence used from the document</h3>';
        html += grounding.html;

        html += '<h3>How to verify</h3>';
        html += '<p>Use the source cards on the right. Each source shows the document name, page number, chunk ID, and an Open source button.</p>';
    } else {
        html += renderPlainAnswerPhase34(rawAnswer);
        html += '<h3>Evidence used from the document</h3>';
        html += grounding.html;
    }

    html += '</div>';
    return html;
}

function renderMessages() {
    const box = document.getElementById('messages');
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument ? getCompareDocument() : null;

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
                <h1>${compareDoc ? 'Compare documents' : 'Chat with your document'}</h1>
                <p>
                    ${compareDoc
                        ? `You are comparing ${htmlEscapePhase34(doc.name)} with ${htmlEscapePhase34(compareDoc.name)}. Ask a comparison question below.`
                        : `Ask a question about ${htmlEscapePhase34(doc.name)}. Answers will include source-backed evidence.`}
                </p>
            </div>
        `;
        return;
    }

    box.innerHTML = '';

    convo.forEach(msg => {
        const wrapper = document.createElement('div');
        wrapper.className = 'message ' + msg.role;

        if (msg.type === 'compare') {
            const bubble = document.createElement('div');
            bubble.className = 'compare-bubble';
            bubble.innerHTML = `
                <h2>Comparison Answer</h2>
                <p><b>Question:</b> ${htmlEscapePhase34(msg.question)}</p>
                <div class="compare-grid">
                    <div class="compare-card">
                        <h3>${htmlEscapePhase34(msg.docAName)}</h3>
                        ${msg.answerAHtml || htmlEscapePhase34(msg.answerA)}
                    </div>
                    <div class="compare-card">
                        <h3>${htmlEscapePhase34(msg.docBName)}</h3>
                        ${msg.answerBHtml || htmlEscapePhase34(msg.answerB)}
                    </div>
                </div>
            `;
            wrapper.appendChild(bubble);
        } else {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';

            if (msg.role === 'assistant' && msg.html) {
                bubble.innerHTML = msg.html;
            } else {
                bubble.textContent = msg.content || '';
            }

            wrapper.appendChild(bubble);
        }

        box.appendChild(wrapper);
    });

    box.scrollTop = box.scrollHeight;
}

async function sendMessage() {
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument ? getCompareDocument() : null;
    const input = document.getElementById('messageInput');
    const userText = input.value.trim();

    if (!doc) {
        alert('Upload or select a document first.');
        return;
    }

    if (!userText) return;

    const convo = getConversation();

    convo.push({
        role: 'user',
        content: userText,
        createdAt: new Date().toISOString()
    });

    input.value = '';
    saveConversations();
    renderMessages();

    setStatus(compareDoc ? 'Comparing...' : 'Thinking...');
    document.getElementById('metricsBox').innerHTML = '';

    try {
        if (compareDoc) {
            const dataA = await callAsk(askPayload(buildContextualQuery(userText, true), doc.id));
            const dataB = await callAsk(askPayload(buildContextualQuery(userText, true), compareDoc.id));

            const answerAHtml = formatProfessionalAnswerPhase34(userText, dataA, doc);
            const answerBHtml = formatProfessionalAnswerPhase34(userText, dataB, compareDoc);

            convo.push({
                role: 'assistant',
                type: 'compare',
                question: userText,
                docAName: doc.name || 'Document A',
                docBName: compareDoc.name || 'Document B',
                answerA: dataA.answer || 'No answer from first document.',
                answerB: dataB.answer || 'No answer from second document.',
                answerAHtml,
                answerBHtml,
                rawA: dataA,
                rawB: dataB,
                createdAt: new Date().toISOString()
            });

            saveConversations();
            renderMessages();

            updateMetrics(dataA, doc.name || 'Document A');
            updateMetrics(dataB, compareDoc.name || 'Document B');

            updateCitations([
                { label: doc.name || 'Document A', sources: buildSources(dataA, doc) },
                { label: compareDoc.name || 'Document B', sources: buildSources(dataB, compareDoc) }
            ]);

            setStatus('Comparison ready');
        } else {
            const data = await callAsk(askPayload(buildContextualQuery(userText), doc.id));
            const answer = data.answer || 'I could not generate an answer.';
            const html = formatProfessionalAnswerPhase34(userText, data, doc);

            convo.push({
                role: 'assistant',
                content: stripHtmlPhase34(html),
                html,
                createdAt: new Date().toISOString(),
                raw: data
            });

            saveConversations();
            renderMessages();

            updateMetrics(data, doc.name || 'Selected document');
            updateCitations([
                { label: doc.name || 'Selected document', sources: buildSources(data, doc) }
            ]);

            setStatus('Ready');
        }
    } catch (error) {
        convo.push({
            role: 'assistant',
            content: 'Error: ' + error.message,
            createdAt: new Date().toISOString()
        });

        saveConversations();
        renderMessages();
        setStatus('Error');
    }
}
</script>
"""

    if "Phase 34:" not in html:
        html = html.replace("</body>", js + "\n</body>")

    return html



# =====================================================
# Phase 36 override: restore graph actions in user app
# =====================================================

try:
    _phase36_previous_get_product_app_html = get_product_app_html
except NameError:
    _phase36_previous_get_product_app_html = None


def get_product_app_html() -> str:
    if _phase36_previous_get_product_app_html is None:
        return "<h1>GraphResearcher App</h1><p>App UI is unavailable.</p>"

    html = _phase36_previous_get_product_app_html()

    graph_section = """
        <div class="panel-section" id="graphActionsPhase36">
            <h3>Graph View</h3>
            <button class="green" onclick="buildGraphPhase36()">Build / Rebuild Graph</button>
            <button class="secondary" onclick="openGraphViewerPhase36()">View Graph</button>
            <p class="small" style="color:#64748b;margin-top:8px;">
                Open the entity-relation graph created from the selected document.
            </p>
        </div>
"""

    if "id=\"graphActionsPhase36\"" not in html:
        if '<div class="panel-section">' in html and "Advanced Settings" in html:
            html = html.replace(
                '<div class="panel-section">\n            <h3>Advanced Settings</h3>',
                graph_section + '\n        <div class="panel-section">\n            <h3>Advanced Settings</h3>',
                1
            )
        elif "</aside>" in html:
            html = html.replace("</aside>", graph_section + "\n    </aside>", 1)

    sidebar_buttons = """
        <button class="full secondary" onclick="buildGraphPhase36()">Build / Rebuild Graph</button>
        <button class="full secondary" onclick="openGraphViewerPhase36()">View Graph</button>
"""

    if "openGraphViewerPhase36" not in html.split("</aside>", 1)[0]:
        if "Clear Workspace Cache" in html:
            html = html.replace(
                '<button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>',
                '<button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>\n' + sidebar_buttons,
                1
            )
        elif '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>' in html:
            html = html.replace(
                '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>',
                '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>\n' + sidebar_buttons,
                1
            )

    js = """
<script>
/*
Phase 36: restore View Graph in the normal user app.
This is not a developer-only feature. It helps users inspect the document entity-relation graph.
*/

async function buildGraphPhase36() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert('Select a document first.');
        return;
    }

    setStatus('Building graph...');

    try {
        const response = await fetch(`/documents/${doc.id}/graph/build`, {
            method: 'POST'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        doc.graphStatus = 'graph built';
        doc.graphData = {
            entities: data.total_entities ?? data.entity_count ?? null,
            relations: data.total_relations ?? data.relation_count ?? null
        };

        saveDocuments();
        renderDocuments();

        const metricsBox = document.getElementById('metricsBox');
        if (metricsBox) {
            metricsBox.innerHTML = `
                <span class="metric">graph built</span>
                <span class="metric">entities: ${doc.graphData.entities ?? 'NA'}</span>
                <span class="metric">relations: ${doc.graphData.relations ?? 'NA'}</span>
            `;
        }

        setStatus('Graph ready');
        alert('Graph built. Click View Graph to open it.');

    } catch (error) {
        setStatus('Graph build failed');
        alert('Graph build failed. Re-index or re-upload the document if Hugging Face rebuilt recently. Error: ' + error.message);
    }
}

function openGraphViewerPhase36() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert('Select a document first.');
        return;
    }

    window.open(`/documents/${doc.id}/graph/view`, '_blank');
}
</script>
"""

    if "Phase 36: restore View Graph" not in html:
        html = html.replace("</body>", js + "\n</body>")

    return html



# =====================================================
# Phase 37 override: use backend /documents/compare
# =====================================================

try:
    _phase37_previous_get_product_app_html = get_product_app_html
except NameError:
    _phase37_previous_get_product_app_html = None


def get_product_app_html() -> str:
    if _phase37_previous_get_product_app_html is None:
        return "<h1>GraphResearcher App</h1><p>App UI is unavailable.</p>"

    html = _phase37_previous_get_product_app_html()

    js = """
<script>
/*
Phase 37:
Compare mode now uses backend /documents/compare instead of doing only browser-side comparison.
Single-document chat still uses the previous sendMessage logic.
*/

if (!window.phase37OriginalSendMessage) {
    window.phase37OriginalSendMessage = window.sendMessage;
}

function phase37AnswerHtml(question, askResponse, doc) {
    if (typeof formatProfessionalAnswerPhase34 === 'function') {
        return formatProfessionalAnswerPhase34(question, askResponse, doc);
    }

    const answer = String(askResponse.answer || 'No answer generated.');
    return '<div class="answer-card"><h2>Answer</h2><p>' + htmlEscapePhase37(answer) + '</p></div>';
}

function htmlEscapePhase37(value) {
    return String(value || '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('\"', '&quot;');
}

window.sendMessage = async function() {
    const doc = getSelectedDocument();
    const compareDoc = getCompareDocument ? getCompareDocument() : null;
    const input = document.getElementById('messageInput');
    const userText = input.value.trim();

    if (!doc) {
        alert('Upload or select a document first.');
        return;
    }

    if (!userText) return;

    if (!compareDoc) {
        return window.phase37OriginalSendMessage();
    }

    const convo = getConversation();

    convo.push({
        role: 'user',
        content: userText,
        createdAt: new Date().toISOString()
    });

    input.value = '';
    saveConversations();
    renderMessages();

    setStatus('Comparing documents...');
    document.getElementById('metricsBox').innerHTML = '';

    try {
        const payload = {
            primary_document_id: doc.id,
            compare_document_id: compareDoc.id,
            query: userText,
            retrieval_mode: 'hybrid',
            top_k: 8,
            use_reranker: document.getElementById('useReranker').checked,
            use_llm: document.getElementById('useLLM').checked,
            use_graph: document.getElementById('useGraph').checked,
            graph_entity_limit: 12,
            use_graph_retrieval: document.getElementById('useGraphRetrieval').checked,
            graph_retrieval_top_k: 6,
            answer_style: document.getElementById('answerStyle')?.value || 'comparison'
        };

        const response = await fetch('/documents/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        const dataA = data.document_a?.ask_response || {
            answer: data.document_a?.answer || 'No answer from first document.',
            citations: data.document_a?.sources || []
        };

        const dataB = data.document_b?.ask_response || {
            answer: data.document_b?.answer || 'No answer from second document.',
            citations: data.document_b?.sources || []
        };

        const answerAHtml = phase37AnswerHtml(userText, dataA, doc);
        const answerBHtml = phase37AnswerHtml(userText, dataB, compareDoc);

        convo.push({
            role: 'assistant',
            type: 'compare',
            question: userText,
            docAName: doc.name || 'Document A',
            docBName: compareDoc.name || 'Document B',
            answerA: data.document_a?.answer || 'No answer from first document.',
            answerB: data.document_b?.answer || 'No answer from second document.',
            answerAHtml,
            answerBHtml,
            comparisonSummary: data.comparison_summary || '',
            rawCompare: data,
            createdAt: new Date().toISOString()
        });

        saveConversations();
        renderMessages();

        if (typeof updateMetrics === 'function') {
            updateMetrics(dataA, doc.name || 'Document A');
            updateMetrics(dataB, compareDoc.name || 'Document B');
        }

        if (typeof updateCitations === 'function' && typeof buildSources === 'function') {
            updateCitations([
                { label: doc.name || 'Document A', sources: buildSources(dataA, doc) },
                { label: compareDoc.name || 'Document B', sources: buildSources(dataB, compareDoc) }
            ]);
        }

        setStatus('Backend comparison ready');

    } catch (error) {
        convo.push({
            role: 'assistant',
            content: 'Comparison error: ' + error.message,
            createdAt: new Date().toISOString()
        });

        saveConversations();
        renderMessages();
        setStatus('Comparison error');
    }
}
</script>
"""

    if "Phase 37:" not in html:
        html = html.replace("</body>", js + "\n</body>")

    return html
# =====================================================
# Phase 38 final stable UI export
# This keeps old helper functions but forces / and /app to use the clean final UI.
# =====================================================
from app.product.final_product_ui import get_home_html, get_product_app_html
