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
'''

if "Phase 34 override: professional answer rendering" not in text:
    text += "\n\n" + append_code
    print("Phase 34 professional answer renderer added.")
else:
    print("Phase 34 already exists.")

hf_path.write_text(text, encoding="utf-8")
print("Done.")
