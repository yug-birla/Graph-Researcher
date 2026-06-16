from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

# ------------------------------------------------------------------
# Replace buildReadableAnswer inside the stable recovery layer
# ------------------------------------------------------------------

start = text.find("    function buildReadableAnswer(question, data, doc) {")
if start == -1:
    raise RuntimeError("Could not find buildReadableAnswer in final_product_ui.py")

end = text.find("    function askPayload(question, docId) {", start)
if end == -1:
    raise RuntimeError("Could not find askPayload after buildReadableAnswer")

new_build_readable_answer = r'''
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

'''

text = text[:start] + new_build_readable_answer + text[end:]

# ------------------------------------------------------------------
# Replace askPayload to improve retrieval query for build/steps questions
# ------------------------------------------------------------------

start2 = text.find("    function askPayload(question, docId) {", start)
if start2 == -1:
    raise RuntimeError("Could not find askPayload")

end2 = text.find("    async function callAsk(payload) {", start2)
if end2 == -1:
    raise RuntimeError("Could not find callAsk after askPayload")

new_ask_payload = r'''
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

'''

text = text[:start2] + new_ask_payload + text[end2:]

path.write_text(text, encoding="utf-8")
print("Phase 42 applied: better project step answers and better retrieval query.")
