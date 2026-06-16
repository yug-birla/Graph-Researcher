from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

stable_js = r'''
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

    function buildReadableAnswer(question, data, doc) {
        const styleEl = byId("answerStyle");
        const style = styleEl ? styleEl.value : "detailed";
        let answer = cleanAnswer(data && data.answer ? data.answer : "I could not generate an answer.");

        const sources = buildSources(data || {}, doc);
        const sourceSentences = [];

        sources.forEach(src => {
            sentenceSplit(src.preview).forEach(s => {
                if (sourceSentences.length < 8) sourceSentences.push(s);
            });
        });

        const words = answer.split(" ").filter(Boolean).length;
        const lower = answer.toLowerCase();

        if (words < 90 || lower.includes("chunk_id") || lower.includes("document_id") || lower.includes("entity_id")) {
            if (sourceSentences.length) {
                answer = sourceSentences.join(" ");
            }
        }

        let points = sentenceSplit(answer);

        if (!points.length) points = [answer];

        if (style === "concise") points = points.slice(0, 3);
        else if (style === "step_by_step") points = points.slice(0, 8);
        else if (style === "research") points = [
            "Overview: " + (points[0] || answer),
            "Key details: " + points.slice(1, 4).join(" "),
            "Interpretation: The document presents these ideas as part of the system design and implementation flow."
        ];
        else points = points.slice(0, 7);

        const isStep = style === "step_by_step" || String(question || "").toLowerCase().includes("step") || String(question || "").toLowerCase().includes("build");

        let html = '<div class="answer-card">';
        html += '<h2>' + (style === "concise" ? "Concise answer" : isStep ? "Step-by-step answer" : style === "research" ? "Research-style answer" : "Detailed answer") + '</h2>';

        if (isStep) {
            html += "<ol>";
            points.forEach(p => { html += "<li>" + esc(p) + "</li>"; });
            html += "</ol>";
        } else if (points.length >= 3) {
            html += "<ul>";
            points.forEach(p => { html += "<li>" + esc(p) + "</li>"; });
            html += "</ul>";
        } else {
            points.forEach(p => { html += "<p>" + esc(p) + "</p>"; });
        }

        html += "</div>";
        return html;
    }

    function askPayload(question, docId) {
        const reranker = byId("useReranker");
        const llm = byId("useLLM");
        const graph = byId("useGraph");
        const graphRetrieval = byId("useGraphRetrieval");

        return {
            query: question,
            document_id: docId,
            top_k: 8,
            retrieval_mode: "hybrid",
            use_reranker: reranker ? reranker.checked : true,
            use_llm: llm ? llm.checked : true,
            use_graph: graph ? graph.checked : true,
            graph_entity_limit: 12,
            use_graph_retrieval: graphRetrieval ? graphRetrieval.checked : true,
            graph_retrieval_top_k: 6
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
'''

if "stable-button-recovery-layer" not in text:
    idx = text.rfind("</body>")
    if idx == -1:
        raise RuntimeError("Could not find </body> in final_product_ui.py")

    text = text[:idx] + stable_js + "\n" + text[idx:]
    print("Added stable button recovery layer.")
else:
    print("Stable button recovery layer already exists.")

path.write_text(text, encoding="utf-8")
print("Phase 41B complete.")
