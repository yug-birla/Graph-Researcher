from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

hf_path = Path("app/deployment/hf_status.py")
text = hf_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

append_code = r'''
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
'''

if "Phase 33 override: clean retrieval query + stale cache tools" not in text:
    text += "\n\n" + append_code
    print("Phase 33 patch added.")
else:
    print("Phase 33 patch already exists.")

hf_path.write_text(text, encoding="utf-8")
print("Fixed Phase 33 complete.")
