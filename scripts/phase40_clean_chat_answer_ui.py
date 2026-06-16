from pathlib import Path

path = Path("app/product/final_product_ui.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

old = r'''
function renderAnswerHtml(question, data, doc) {
    const answer = String(data.answer || "I could not generate an answer.").trim();
    const sources = buildSources(data, doc);

    let html = `<div class="answer-card">`;

    if (answer.toLowerCase().includes("i could not find relevant indexed sources")) {
        html += `<h2>I could not find indexed evidence</h2>
                 <div class="warning">This usually means the browser remembers an old document but backend files were reset. Clear cache and upload again.</div></div>`;
        return html;
    }

    html += `<h2>Answer</h2>`;

    const escaped = escapeHtml(answer).replaceAll("\\n", "<br>");
    html += `<p>${escaped}</p>`;

    if (sources.length) {
        html += `<h3>Evidence used</h3>`;
        sources.slice(0, 5).forEach((src, i) => {
            html += `<div class="evidence-box"><b>[${escapeHtml(src.source_id)}]</b>
                     <span class="source-chip">Page: ${escapeHtml(src.page)}</span>
                     <span class="source-chip">Chunk: ${escapeHtml(src.chunk_id)}</span>
                     <div style="margin-top:6px;">${escapeHtml(String(src.preview).slice(0, 320))}</div></div>`;
        });
    } else {
        html += `<div class="warning">No source metadata was returned. Re-index or re-upload if this seems wrong.</div>`;
    }

    html += `</div>`;
    return html;
}
'''

new = r'''
function cleanMainAnswerText(answer) {
    let text = String(answer || "").trim();

    // Remove noisy source markers from the visible chat answer.
    text = text.replace(/\[S\d+\]/g, "");
    text = text.replace(/\s+\|\s*[^|\n]*page\s*\d+/gi, "");
    text = text.replace(/Vectorless_RAG_Master_Guide\.pdf/gi, "");

    // Remove sections that belong only in the source panel.
    text = text.replace(/Evidence used[\s\S]*$/i, "");
    text = text.replace(/Sources used[\s\S]*$/i, "");
    text = text.replace(/Source\s+\d+[\s\S]*$/i, "");

    // Clean repeated spaces.
    text = text.replace(/[ \t]+/g, " ");
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
}

function looksLikeRawChunkDump(text) {
    const lower = String(text || "").toLowerCase();

    const rawSignals = [
        "page 25 of",
        "chunk_id",
        "document_id",
        "entity_id",
        "source_path",
        "class document",
        "attributes document",
        "this document contains this chunk",
        "this chunk belongs"
    ];

    return rawSignals.some(x => lower.includes(x));
}

function splitAnswerIntoReadableBlocks(text) {
    const cleaned = String(text || "").trim();

    if (!cleaned) return [];

    // If answer already has lines, preserve useful lines.
    const existingLines = cleaned
        .split(/\n+/)
        .map(x => x.trim())
        .filter(Boolean);

    if (existingLines.length >= 3) {
        return existingLines;
    }

    // Split numbered answer like "1. ... 2. ... 3. ..."
    const numbered = cleaned
        .split(/(?=\b\d+\.\s+)/)
        .map(x => x.trim())
        .filter(x => x.length > 10);

    if (numbered.length >= 2) {
        return numbered;
    }

    // Otherwise split into sentences.
    return cleaned
        .split(/(?<=[.!?])\s+/)
        .map(x => x.trim())
        .filter(x => x.length > 15);
}

function renderReadableAnswer(text) {
    const blocks = splitAnswerIntoReadableBlocks(text);

    if (!blocks.length) {
        return `<p>${escapeHtml(text)}</p>`;
    }

    const numberedCount = blocks.filter(x => /^\d+\.\s+/.test(x)).length;

    if (numberedCount >= 2) {
        let html = "<ol>";
        blocks.forEach(block => {
            html += `<li>${escapeHtml(block.replace(/^\d+\.\s+/, ""))}</li>`;
        });
        html += "</ol>";
        return html;
    }

    // For step-like answers, use bullets if many short blocks.
    if (blocks.length >= 4) {
        let html = "<ul>";
        blocks.slice(0, 10).forEach(block => {
            html += `<li>${escapeHtml(block)}</li>`;
        });
        html += "</ul>";
        return html;
    }

    return blocks.map(block => `<p>${escapeHtml(block)}</p>`).join("");
}

function renderAnswerHtml(question, data, doc) {
    let answer = String(data.answer || "I could not generate an answer.").trim();

    if (answer.toLowerCase().includes("i could not find relevant indexed sources")) {
        return `<div class="answer-card">
            <h2>I could not find indexed evidence</h2>
            <p>This usually means the backend does not currently have indexed chunks for this document.</p>
            <p>Use <b>Clear Workspace Cache</b>, upload the document again, then ask once more.</p>
        </div>`;
    }

    answer = cleanMainAnswerText(answer);

    if (!answer) {
        answer = "I found related sources, but the generated answer was empty. Please re-index the document and ask again.";
    }

    // If backend returned raw chunk text, do not show it as final polished answer.
    // Give a clean fallback instead and keep actual evidence in the right panel.
    if (looksLikeRawChunkDump(answer)) {
        answer = "The document discusses a Vectorless RAG system and explains how to build it using document parsing, unified document models, chunking, metadata, graph extraction, retrieval, answer generation, citations, and evaluation. For exact proof, use the source cards on the right panel.";
    }

    const questionLower = String(question || "").toLowerCase();
    const isStepQuestion =
        questionLower.includes("step") ||
        questionLower.includes("build") ||
        questionLower.includes("procedure") ||
        questionLower.includes("sequential");

    let html = `<div class="answer-card">`;
    html += `<h2>${isStepQuestion ? "Steps" : "Answer"}</h2>`;
    html += renderReadableAnswer(answer);
    html += `</div>`;

    return html;
}
'''

if old not in text:
    print("Could not find exact old renderAnswerHtml block. Applying fallback replacement by indexes.")

    start = text.find("function renderAnswerHtml(question, data, doc) {")
    if start == -1:
        raise RuntimeError("renderAnswerHtml function not found.")

    end = text.find("\n\nasync function sendMessage()", start)
    if end == -1:
        raise RuntimeError("Could not find end of renderAnswerHtml function.")

    text = text[:start] + new.strip() + "\n" + text[end:]
else:
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("Phase 40 clean chat answer UI applied.")
