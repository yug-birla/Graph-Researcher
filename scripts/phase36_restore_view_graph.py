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
# Phase 36 override: restore graph actions in user app
# =====================================================

try:
    _phase36_previous_get_product_app_html = get_product_app_html
except NameError:
    _phase36_previous_get_product_app_html = None


def get_product_app_html() -> str:
    if _phase36_previous_get_product_app_html is None:
        return "<h1>GraphResearcher App</h1><p>App UI is unavailable.</p>"

    html = _phase36_previous_get_product_app_html()

    graph_section = """
        <div class="panel-section" id="graphActionsPhase36">
            <h3>Graph View</h3>
            <button class="green" onclick="buildGraphPhase36()">Build / Rebuild Graph</button>
            <button class="secondary" onclick="openGraphViewerPhase36()">View Graph</button>
            <p class="small" style="color:#64748b;margin-top:8px;">
                Open the entity-relation graph created from the selected document.
            </p>
        </div>
"""

    if "id=\"graphActionsPhase36\"" not in html:
        if '<div class="panel-section">' in html and "Advanced Settings" in html:
            html = html.replace(
                '<div class="panel-section">\n            <h3>Advanced Settings</h3>',
                graph_section + '\n        <div class="panel-section">\n            <h3>Advanced Settings</h3>',
                1
            )
        elif "</aside>" in html:
            html = html.replace("</aside>", graph_section + "\n    </aside>", 1)

    sidebar_buttons = """
        <button class="full secondary" onclick="buildGraphPhase36()">Build / Rebuild Graph</button>
        <button class="full secondary" onclick="openGraphViewerPhase36()">View Graph</button>
"""

    if "openGraphViewerPhase36" not in html.split("</aside>", 1)[0]:
        if "Clear Workspace Cache" in html:
            html = html.replace(
                '<button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>',
                '<button class="full secondary" onclick="clearWorkspaceCache()">Clear Workspace Cache</button>\n' + sidebar_buttons,
                1
            )
        elif '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>' in html:
            html = html.replace(
                '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>',
                '<button class="full secondary" onclick="window.location.href=\'/\'">Home</button>\n' + sidebar_buttons,
                1
            )

    js = """
<script>
/*
Phase 36: restore View Graph in the normal user app.
This is not a developer-only feature. It helps users inspect the document entity-relation graph.
*/

async function buildGraphPhase36() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert('Select a document first.');
        return;
    }

    setStatus('Building graph...');

    try {
        const response = await fetch(`/documents/${doc.id}/graph/build`, {
            method: 'POST'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(data));
        }

        doc.graphStatus = 'graph built';
        doc.graphData = {
            entities: data.total_entities ?? data.entity_count ?? null,
            relations: data.total_relations ?? data.relation_count ?? null
        };

        saveDocuments();
        renderDocuments();

        const metricsBox = document.getElementById('metricsBox');
        if (metricsBox) {
            metricsBox.innerHTML = `
                <span class="metric">graph built</span>
                <span class="metric">entities: ${doc.graphData.entities ?? 'NA'}</span>
                <span class="metric">relations: ${doc.graphData.relations ?? 'NA'}</span>
            `;
        }

        setStatus('Graph ready');
        alert('Graph built. Click View Graph to open it.');

    } catch (error) {
        setStatus('Graph build failed');
        alert('Graph build failed. Re-index or re-upload the document if Hugging Face rebuilt recently. Error: ' + error.message);
    }
}

function openGraphViewerPhase36() {
    const doc = getSelectedDocument();

    if (!doc) {
        alert('Select a document first.');
        return;
    }

    window.open(`/documents/${doc.id}/graph/view`, '_blank');
}
</script>
"""

    if "Phase 36: restore View Graph" not in html:
        html = html.replace("</body>", js + "\n</body>")

    return html
'''

if "Phase 36 override: restore graph actions in user app" not in text:
    text += "\n\n" + append_code
    print("Phase 36 restore View Graph patch added.")
else:
    print("Phase 36 patch already exists.")

hf_path.write_text(text, encoding="utf-8")
print("Done.")
