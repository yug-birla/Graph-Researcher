from pathlib import Path

# Remove BOM from Python files
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

hf_path = Path("app/deployment/hf_status.py")
text = hf_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

extra_function = r'''


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
'''

if "def get_graphrag_demo_html" not in text:
    text += extra_function
    print("Added get_graphrag_demo_html to hf_status.py")
else:
    print("get_graphrag_demo_html already exists")

hf_path.write_text(text, encoding="utf-8")


# Patch main.py
main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

if "get_graphrag_demo_html" not in main_text:
    if "from app.deployment.hf_status import" in main_text:
        main_text = main_text.replace(
            "from app.deployment.hf_status import",
            "from app.deployment.hf_status import"
        )

    # Try to extend existing import block.
    if "get_demo_html" in main_text and "get_graphrag_demo_html" not in main_text:
        main_text = main_text.replace(
            "get_demo_html",
            "get_demo_html, get_graphrag_demo_html",
            1
        )
    else:
        main_text = "from app.deployment.hf_status import get_graphrag_demo_html\n" + main_text

if "# GraphRAG demo UI endpoint" not in main_text:
    main_text += '''

# GraphRAG demo UI endpoint

@app.get("/graphrag-demo", response_class=HTMLResponse)
def graphrag_demo_page():
    return get_graphrag_demo_html()
'''
    print("Added /graphrag-demo route to main.py")
else:
    print("/graphrag-demo route already exists")

main_path.write_text(main_text, encoding="utf-8")

print("Phase 22 GraphRAG demo UI patch complete.")
