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
