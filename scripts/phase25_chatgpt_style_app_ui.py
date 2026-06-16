from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")

hf_path = Path("app/deployment/hf_status.py")
text = hf_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

product_app_html = r'''


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
'''

if "def get_product_app_html" not in text:
    text += product_app_html
    print("Added get_product_app_html.")
else:
    print("get_product_app_html already exists.")

hf_path.write_text(text, encoding="utf-8")


# Patch main.py
main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

if "from app.deployment.hf_status import get_product_app_html" not in main_text:
    main_text = "from app.deployment.hf_status import get_product_app_html\n" + main_text

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

if "# Product ChatGPT-style app UI endpoint" not in main_text:
    main_text += '''

# Product ChatGPT-style app UI endpoint

@app.get("/app", response_class=HTMLResponse)
def product_app_page():
    return get_product_app_html()
'''
    print("Added /app route.")
else:
    print("/app route already exists.")

main_path.write_text(main_text, encoding="utf-8")

print("Phase 25 ChatGPT-style product app UI added.")
