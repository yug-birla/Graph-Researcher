from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

start = text.find("function renderAnswerHtml(question, data, doc) {")
if start == -1:
    raise RuntimeError("renderAnswerHtml function not found.")

end = text.find("\n\nasync function sendMessage()", start)
if end == -1:
    raise RuntimeError("Could not find end of renderAnswerHtml function.")

new_block = r'''
function getSelectedAnswerStyle() {
    const el = document.getElementById("answerStyle");
    return el ? el.value : "detailed";
}

function cleanMainAnswerText(answer) {
    let text = String(answer || "").trim();

    text = text.replace(/\[S\d+\]/g, "");
    text = text.replace(/Vectorless_RAG_Master_Guide\.pdf/gi, "");
    text = text.replace(/Evidence used[\s\S]*$/i, "");
    text = text.replace(/Sources used[\s\S]*$/i, "");
    text = text.replace(/Source\s+\d+[\s\S]*$/i, "");
    text = text.replace(/[ \t]+/g, " ");
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
}

function looksLikeRawChunkDump(text) {
    const lower = String(text || "").toLowerCase();

    const rawSignals = [
        "chunk_id",
        "document_id",
        "entity_id",
        "source_path",
        "class document",
        "attributes document",
        "this document contains this chunk",
        "this chunk belongs",
        "page 25 of",
        "page 32 of"
    ];

    return rawSignals.some(x => lower.includes(x));
}

function countWords(text) {
    return String(text || "").split(/\s+/).filter(Boolean).length;
}

function cleanSourcePreviewForAnswer(text) {
    let value = String(text || "").trim();

    value = value.replace(/chunk_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/document_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/entity_id[:\s]+[A-Za-z0-9_\-]+/gi, "");
    value = value.replace(/source_path[:\s]+[^\n]+/gi, "");
    value = value.replace(/\s+/g, " ");
    value = value.replace(/Page\s+\d+\s+of\s+\d+/gi, "");

    return value.trim();
}

function collectSourceSentences(data, doc) {
    const sources = buildSources(data, doc);
    const sentences = [];
    const seen = new Set();

    sources.forEach(src => {
        const preview = cleanSourcePreviewForAnswer(src.preview);

        preview
            .split(/(?<=[.!?])\s+/)
            .map(x => x.trim())
            .filter(x => x.length > 35 && x.length < 260)
            .forEach(sentence => {
                const key = sentence.toLowerCase();
                if (!seen.has(key)) {
                    seen.add(key);
                    sentences.push(sentence);
                }
            });
    });

    return sentences.slice(0, 10);
}

function buildExpandedAnswerFromSources(question, rawAnswer, data, doc, style) {
    const cleanAnswer = cleanMainAnswerText(rawAnswer);
    const sourceSentences = collectSourceSentences(data, doc);
    const questionLower = String(question || "").toLowerCase();

    const wantsSteps =
        questionLower.includes("step") ||
        questionLower.includes("build") ||
        questionLower.includes("procedure") ||
        questionLower.includes("sequential") ||
        style === "step_by_step";

    let basePoints = [];

    if (cleanAnswer && !looksLikeRawChunkDump(cleanAnswer)) {
        basePoints = cleanAnswer
            .split(/(?<=[.!?])\s+/)
            .map(x => x.trim())
            .filter(x => x.length > 25);
    }

    const allPoints = [...basePoints, ...sourceSentences]
        .map(x => x.trim())
        .filter(Boolean);

    const unique = [];
    const seen = new Set();

    allPoints.forEach(point => {
        const key = point.toLowerCase().slice(0, 120);
        if (!seen.has(key)) {
            seen.add(key);
            unique.push(point);
        }
    });

    if (!unique.length) {
        return {
            title: "Answer",
            blocks: ["I found related chunks, but the answer was too weak to expand cleanly. Please re-index the document and ask again."],
            ordered: false
        };
    }

    if (style === "concise") {
        return {
            title: "Concise answer",
            blocks: unique.slice(0, 3),
            ordered: false
        };
    }

    if (style === "research") {
        return {
            title: "Research-style answer",
            blocks: [
                "Overview: " + unique[0],
                "Key details: " + unique.slice(1, 4).join(" "),
                "Interpretation: The document connects these ideas as part of the system design and implementation flow."
            ].filter(x => x.length > 20),
            ordered: false
        };
    }

    if (wantsSteps) {
        return {
            title: "Step-by-step answer",
            blocks: unique.slice(0, 8),
            ordered: true
        };
    }

    return {
        title: "Detailed answer",
        blocks: unique.slice(0, 7),
        ordered: false
    };
}

function renderBlocksAsHtml(blocks, ordered) {
    if (!blocks || !blocks.length) return "<p>No answer generated.</p>";

    if (ordered) {
        let html = "<ol>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block.replace(/^\d+\.\s+/, ""))}</li>`;
        });
        html += "</ol>";
        return html;
    }

    if (blocks.length >= 3) {
        let html = "<ul>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block)}</li>`;
        });
        html += "</ul>";
        return html;
    }

    return blocks.map(block => `<p>${escapeHtml(block)}</p>`).join("");
}

function renderAnswerHtml(question, data, doc) {
    const style = getSelectedAnswerStyle();
    const rawAnswer = String(data.answer || "I could not generate an answer.").trim();

    if (rawAnswer.toLowerCase().includes("i could not find relevant indexed sources")) {
        return `<div class="answer-card">
            <h2>I could not find indexed evidence</h2>
            <p>The backend does not currently have indexed chunks for this document.</p>
            <p>Use <b>Clear Workspace Cache</b>, upload the document again, then ask once more.</p>
        </div>`;
    }

    const cleaned = cleanMainAnswerText(rawAnswer);
    const shouldExpand =
        countWords(cleaned) < 140 ||
        looksLikeRawChunkDump(cleaned) ||
        style === "step_by_step" ||
        style === "research";

    let finalAnswer;

    if (shouldExpand) {
        finalAnswer = buildExpandedAnswerFromSources(question, rawAnswer, data, doc, style);
    } else {
        finalAnswer = {
            title:
                style === "concise" ? "Concise answer" :
                style === "research" ? "Research-style answer" :
                style === "step_by_step" ? "Step-by-step answer" :
                "Detailed answer",
            blocks: cleaned
                .split(/\n+/)
                .map(x => x.trim())
                .filter(Boolean),
            ordered: style === "step_by_step"
        };
    }

    let html = `<div class="answer-card">`;
    html += `<h2>${escapeHtml(finalAnswer.title)}</h2>`;
    html += renderBlocksAsHtml(finalAnswer.blocks, finalAnswer.ordered);
    html += `</div>`;

    return html;
}
'''

text = text[:start] + new_block.strip() + text[end:]

path.write_text(text, encoding="utf-8")
print("Phase 41 applied: Answer Style now affects final output.")
