from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

Path("app/product").mkdir(parents=True, exist_ok=True)

# =====================================================
# 1. Backend compare service
# =====================================================

Path("app/product/document_compare_service.py").write_text(r'''
import inspect
import json
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field


class CompareDocumentsRequest(BaseModel):
    primary_document_id: str = Field(..., description="First document ID")
    compare_document_id: str = Field(..., description="Second document ID")
    query: str = Field(..., description="User comparison question")

    retrieval_mode: str = "hybrid"
    top_k: int = 8
    use_reranker: bool = True
    use_llm: bool = True
    use_graph: bool = True
    graph_entity_limit: int = 12
    use_graph_retrieval: bool = True
    graph_retrieval_top_k: int = 6
    answer_style: str = "comparison"


def response_to_dict(value: Any) -> Dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "body"):
        try:
            body = value.body
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            return json.loads(body)
        except Exception:
            pass

    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass

    return {
        "raw_response": str(value)
    }


def get_model_fields(model_cls) -> set:
    fields = getattr(model_cls, "model_fields", None)

    if fields is None:
        fields = getattr(model_cls, "__fields__", {})

    return set(fields.keys())


def build_ask_payload(
    document_id: str,
    query: str,
    request: CompareDocumentsRequest
) -> Dict[str, Any]:
    return {
        "query": query,
        "document_id": document_id,
        "top_k": request.top_k,
        "retrieval_mode": request.retrieval_mode,
        "use_reranker": request.use_reranker,
        "use_llm": request.use_llm,
        "use_graph": request.use_graph,
        "graph_entity_limit": request.graph_entity_limit,
        "use_graph_retrieval": request.use_graph_retrieval,
        "graph_retrieval_top_k": request.graph_retrieval_top_k
    }


def extract_sources(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    sources = []

    for item in response.get("citations", []) or []:
        if isinstance(item, dict):
            sources.append(item)

    fusion = response.get("retrieval_fusion") or {}

    for item in fusion.get("fused_results", []) or []:
        if isinstance(item, dict):
            sources.append(item)

    for key in ["sources", "source_chunks", "retrieved_sources"]:
        for item in response.get(key, []) or []:
            if isinstance(item, dict):
                sources.append(item)

    cleaned = []
    seen = set()

    for index, src in enumerate(sources):
        source_id = (
            src.get("source_id")
            or src.get("citation_id")
            or src.get("id")
            or f"S{index + 1}"
        )

        chunk_id = (
            src.get("chunk_id")
            or src.get("source_chunk_id")
            or src.get("chunk")
            or source_id
        )

        page = (
            src.get("page")
            or src.get("page_number")
            or src.get("page_no")
            or "Not available"
        )

        key = f"{source_id}|{chunk_id}|{page}"

        if key in seen:
            continue

        seen.add(key)

        cleaned.append({
            "source_id": source_id,
            "chunk_id": chunk_id,
            "page": page,
            "document_name": (
                src.get("document_name")
                or src.get("source_file_name")
                or src.get("file_name")
                or src.get("filename")
                or "Selected document"
            ),
            "preview": (
                src.get("text_preview")
                or src.get("preview")
                or src.get("chunk_preview")
                or src.get("text")
                or src.get("content")
                or ""
            ),
            "raw": src
        })

    return cleaned[:8]


def make_compare_question(user_query: str) -> str:
    """
    Keep retrieval query clean. Do not inject long formatting prompt.
    Long prompts hurt semantic retrieval.
    """
    return user_query.strip()


async def call_existing_ask_endpoint(app, payload: Dict[str, Any]) -> Dict[str, Any]:
    ask_route = None

    for route in app.routes:
        route_path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()

        if route_path == "/ask" and "POST" in methods:
            ask_route = route
            break

    if ask_route is None:
        raise HTTPException(
            status_code=500,
            detail="Could not find existing POST /ask endpoint."
        )

    try:
        from app.schemas.query_schema import AskRequest
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not import AskRequest schema: {exc}"
        )

    allowed_fields = get_model_fields(AskRequest)
    filtered_payload = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    try:
        ask_request = AskRequest(**filtered_payload)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not build AskRequest for compare endpoint: {exc}"
        )

    endpoint = ask_route.endpoint
    signature = inspect.signature(endpoint)
    params = list(signature.parameters.values())

    try:
        if len(params) == 0:
            result = endpoint()
        elif len(params) == 1:
            result = endpoint(ask_request)
        else:
            kwargs = {}

            for param in params:
                param_name = param.name
                annotation = str(param.annotation)

                if "AskRequest" in annotation or param_name in {
                    "request",
                    "ask_request",
                    "payload",
                    "body"
                }:
                    kwargs[param_name] = ask_request

            result = endpoint(**kwargs)

        if inspect.isawaitable(result):
            result = await result

        return response_to_dict(result)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Compare endpoint failed while calling /ask: {exc}"
        )


def build_rule_based_comparison(
    query: str,
    answer_a: str,
    answer_b: str
) -> str:
    return (
        "Comparison summary\n"
        "The system answered the same question separately against both documents. "
        "Use the two document-specific answers and source panels to verify the differences.\n\n"
        "How to read this comparison\n"
        "1. Check Document A answer for claims supported by Document A sources.\n"
        "2. Check Document B answer for claims supported by Document B sources.\n"
        "3. If one answer is weaker or says evidence is missing, that document likely does not contain enough relevant indexed context for the question.\n\n"
        "Important limitation\n"
        "This comparison is evidence-grounded per document. It does not merge unsupported information across documents."
    )


async def compare_documents_with_existing_ask(
    app,
    request: CompareDocumentsRequest
) -> Dict[str, Any]:
    clean_query = make_compare_question(request.query)

    payload_a = build_ask_payload(
        document_id=request.primary_document_id,
        query=clean_query,
        request=request
    )

    payload_b = build_ask_payload(
        document_id=request.compare_document_id,
        query=clean_query,
        request=request
    )

    response_a = await call_existing_ask_endpoint(app, payload_a)
    response_b = await call_existing_ask_endpoint(app, payload_b)

    answer_a = response_a.get("answer", "")
    answer_b = response_b.get("answer", "")

    return {
        "status": "success",
        "mode": "backend_document_compare",
        "query": request.query,
        "primary_document_id": request.primary_document_id,
        "compare_document_id": request.compare_document_id,
        "comparison_summary": build_rule_based_comparison(
            query=request.query,
            answer_a=answer_a,
            answer_b=answer_b
        ),
        "document_a": {
            "document_id": request.primary_document_id,
            "answer": answer_a,
            "sources": extract_sources(response_a),
            "ask_response": response_a
        },
        "document_b": {
            "document_id": request.compare_document_id,
            "answer": answer_b,
            "sources": extract_sources(response_b),
            "ask_response": response_b
        },
        "notes": [
            "Retrieval query is kept clean to preserve semantic search quality.",
            "Each document is queried independently.",
            "Sources are separated per document for verification."
        ]
    }
''', encoding="utf-8")


# =====================================================
# 2. Patch main.py with backend compare endpoint
# =====================================================

main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.product.document_compare_service import" not in text:
    text = (
        "from app.product.document_compare_service import CompareDocumentsRequest, compare_documents_with_existing_ask\n"
        + text
    )

if "# Backend document comparison endpoint" not in text:
    text += '''

# Backend document comparison endpoint

@app.post("/documents/compare")
async def compare_two_documents(request: CompareDocumentsRequest):
    return await compare_documents_with_existing_ask(
        app=app,
        request=request
    )
'''

main_path.write_text(text, encoding="utf-8")


# =====================================================
# 3. Patch UI to use backend compare endpoint
# =====================================================

hf_path = Path("app/deployment/hf_status.py")
ui = hf_path.read_text(encoding="utf-8-sig")
ui = ui.replace("\ufeff", "")

append_code = r'''
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
'''

if "Phase 37 override: use backend /documents/compare" not in ui:
    ui += "\n\n" + append_code
    print("Phase 37 UI backend compare override added.")
else:
    print("Phase 37 UI override already exists.")

hf_path.write_text(ui, encoding="utf-8")

print("Phase 37 backend compare endpoint added.")
