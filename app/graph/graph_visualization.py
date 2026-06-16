
from html import escape


def get_graph_visualization_html(document_id: str) -> str:
    safe_document_id = escape(document_id)

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Graph View - {safe_document_id}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f8fafc;
            color: #111827;
        }}

        header {{
            padding: 16px 22px;
            background: #111827;
            color: white;
        }}

        header h1 {{
            margin: 0;
            font-size: 22px;
        }}

        header p {{
            margin: 6px 0 0 0;
            color: #d1d5db;
            font-size: 14px;
        }}

        .container {{
            display: grid;
            grid-template-columns: 1fr 320px;
            height: calc(100vh - 78px);
        }}

        #canvasWrap {{
            position: relative;
            overflow: hidden;
            background: white;
        }}

        canvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}

        aside {{
            border-left: 1px solid #d1d5db;
            padding: 16px;
            background: #f9fafb;
            overflow-y: auto;
        }}

        .card {{
            border: 1px solid #d1d5db;
            background: white;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
        }}

        .small {{
            font-size: 13px;
            color: #6b7280;
        }}

        .pill {{
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            border-radius: 999px;
            padding: 3px 8px;
            font-size: 12px;
            margin: 2px;
        }}

        button {{
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 11px;
            cursor: pointer;
            margin: 4px 2px;
        }}

        button:hover {{
            background: #1d4ed8;
        }}

        input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            margin: 6px 0;
        }}

        pre {{
            white-space: pre-wrap;
            background: #0f172a;
            color: #e5e7eb;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            max-height: 240px;
            overflow-y: auto;
        }}

        @media (max-width: 900px) {{
            .container {{
                grid-template-columns: 1fr;
                height: auto;
            }}

            #canvasWrap {{
                height: 70vh;
            }}

            aside {{
                border-left: none;
                border-top: 1px solid #d1d5db;
            }}
        }}
    </style>
</head>

<body>
    <header>
        <h1>🕸️ Document Graph View</h1>
        <p>Document ID: <code>{safe_document_id}</code></p>
    </header>

    <div class="container">
        <div id="canvasWrap">
            <canvas id="graphCanvas"></canvas>
        </div>

        <aside>
            <div class="card">
                <h3>Controls</h3>
                <button onclick="loadGraph()">Reload Graph</button>
                <button onclick="resetLayout()">Reset Layout</button>
                <button onclick="toggleLabels()">Toggle Labels</button>
                <p class="small">
                    Drag nodes with your mouse. Click a node to inspect it.
                </p>
            </div>

            <div class="card">
                <h3>Search Entity</h3>
                <input id="searchBox" placeholder="Example: RAG">
                <button onclick="searchNode()">Find</button>
            </div>

            <div class="card">
                <h3>Graph Stats</h3>
                <div id="stats">Loading...</div>
            </div>

            <div class="card">
                <h3>Selected Node</h3>
                <div id="nodeDetails">Click a node to see details.</div>
            </div>

            <div class="card">
                <h3>Raw Selected Data</h3>
                <pre id="rawDetails">{{}}</pre>
            </div>
        </aside>
    </div>

<script>
const documentId = "{safe_document_id}";
const canvas = document.getElementById("graphCanvas");
const ctx = canvas.getContext("2d");

let graphData = null;
let nodes = [];
let edges = [];
let showLabels = true;
let draggingNode = null;
let selectedNode = null;
let mouse = {{ x: 0, y: 0 }};

function resizeCanvas() {{
    const wrap = document.getElementById("canvasWrap");
    canvas.width = wrap.clientWidth;
    canvas.height = wrap.clientHeight;
}}

window.addEventListener("resize", () => {{
    resizeCanvas();
    draw();
}});

function randomBetween(min, max) {{
    return Math.random() * (max - min) + min;
}}

function nodeRadius(node) {{
    const mention = node.mention_count || 1;
    return Math.min(28, Math.max(8, 7 + Math.sqrt(mention) * 3));
}}

function entityColor(type) {{
    if (type === "ACRONYM") return "#2563eb";
    if (type === "ORGANIZATION") return "#7c3aed";
    if (type === "TECHNICAL_TERM") return "#059669";
    return "#f97316";
}}

async function loadGraph() {{
    resizeCanvas();

    const stats = document.getElementById("stats");
    stats.textContent = "Loading graph...";

    try {{
        const response = await fetch(`/documents/${{documentId}}/graph`);

        if (!response.ok) {{
            const err = await response.json();
            stats.innerHTML = `
                <span style="color:#991b1b;">
                    Graph not found. First run POST /documents/${{documentId}}/graph/build from /docs.
                </span>
            `;
            return;
        }}

        graphData = await response.json();

        const rawEntities = graphData.entities || [];
        const rawRelations = graphData.relations || [];

        const topEntities = rawEntities.slice(0, 80);
        const allowedIds = new Set(topEntities.map(e => e.entity_id));

        nodes = topEntities.map(entity => ({{
            ...entity,
            x: randomBetween(80, canvas.width - 80),
            y: randomBetween(80, canvas.height - 80),
            vx: 0,
            vy: 0
        }}));

        edges = rawRelations
            .filter(edge =>
                allowedIds.has(edge.source_entity_id) &&
                allowedIds.has(edge.target_entity_id)
            )
            .slice(0, 160);

        stats.innerHTML = `
            <p><span class="pill">entities: ${{graphData.total_entities}}</span></p>
            <p><span class="pill">relations: ${{graphData.total_relations}}</span></p>
            <p><span class="pill">displayed nodes: ${{nodes.length}}</span></p>
            <p><span class="pill">displayed edges: ${{edges.length}}</span></p>
            <p class="small">Only top entities are shown to keep the graph readable.</p>
        `;

        runLayoutSteps(180);
        draw();

    }} catch (error) {{
        stats.textContent = "Failed to load graph: " + error;
    }}
}}

function getNodeById(id) {{
    return nodes.find(node => node.entity_id === id);
}}

function runLayoutSteps(steps) {{
    for (let i = 0; i < steps; i++) {{
        layoutStep();
    }}
}}

function layoutStep() {{
    const repulsion = 1200;
    const springLength = 120;
    const springStrength = 0.015;
    const damping = 0.85;

    // Repel nodes
    for (let i = 0; i < nodes.length; i++) {{
        for (let j = i + 1; j < nodes.length; j++) {{
            const a = nodes[i];
            const b = nodes[j];

            let dx = a.x - b.x;
            let dy = a.y - b.y;
            let distSq = dx * dx + dy * dy + 0.01;
            let dist = Math.sqrt(distSq);

            let force = repulsion / distSq;

            let fx = (dx / dist) * force;
            let fy = (dy / dist) * force;

            a.vx += fx;
            a.vy += fy;
            b.vx -= fx;
            b.vy -= fy;
        }}
    }}

    // Pull connected nodes
    for (const edge of edges) {{
        const source = getNodeById(edge.source_entity_id);
        const target = getNodeById(edge.target_entity_id);

        if (!source || !target) continue;

        let dx = target.x - source.x;
        let dy = target.y - source.y;
        let dist = Math.sqrt(dx * dx + dy * dy) || 1;

        let force = (dist - springLength) * springStrength;

        let fx = (dx / dist) * force;
        let fy = (dy / dist) * force;

        source.vx += fx;
        source.vy += fy;
        target.vx -= fx;
        target.vy -= fy;
    }}

    // Move nodes
    for (const node of nodes) {{
        node.vx *= damping;
        node.vy *= damping;

        node.x += node.vx;
        node.y += node.vy;

        const r = nodeRadius(node);
        node.x = Math.max(r + 10, Math.min(canvas.width - r - 10, node.x));
        node.y = Math.max(r + 10, Math.min(canvas.height - r - 10, node.y));
    }}
}}

function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    for (const edge of edges) {{
        const source = getNodeById(edge.source_entity_id);
        const target = getNodeById(edge.target_entity_id);

        if (!source || !target) continue;

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = "#cbd5e1";
        ctx.lineWidth = Math.min(4, 1 + (edge.weight || 1) * 0.4);
        ctx.stroke();

        if (showLabels && edge.weight > 1) {{
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;

            ctx.fillStyle = "#64748b";
            ctx.font = "10px Arial";
            ctx.fillText(edge.relation_type || "RELATED_TO", midX, midY);
        }}
    }}

    // Draw nodes
    for (const node of nodes) {{
        const r = nodeRadius(node);

        ctx.beginPath();
        ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
        ctx.fillStyle = entityColor(node.entity_type);
        ctx.fill();

        if (selectedNode && selectedNode.entity_id === node.entity_id) {{
            ctx.strokeStyle = "#111827";
            ctx.lineWidth = 4;
            ctx.stroke();
        }}

        if (showLabels) {{
            ctx.fillStyle = "#111827";
            ctx.font = "12px Arial";
            ctx.fillText(node.name, node.x + r + 4, node.y + 4);
        }}
    }}
}}

function animate() {{
    layoutStep();
    draw();
    requestAnimationFrame(animate);
}}

function getMousePos(event) {{
    const rect = canvas.getBoundingClientRect();
    return {{
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    }};
}}

function getNodeAt(x, y) {{
    for (let i = nodes.length - 1; i >= 0; i--) {{
        const node = nodes[i];
        const r = nodeRadius(node);
        const dx = x - node.x;
        const dy = y - node.y;

        if (dx * dx + dy * dy <= r * r) {{
            return node;
        }}
    }}

    return null;
}}

canvas.addEventListener("mousedown", event => {{
    mouse = getMousePos(event);
    draggingNode = getNodeAt(mouse.x, mouse.y);

    if (draggingNode) {{
        selectedNode = draggingNode;
        showNodeDetails(selectedNode);
    }}
}});

canvas.addEventListener("mousemove", event => {{
    mouse = getMousePos(event);

    if (draggingNode) {{
        draggingNode.x = mouse.x;
        draggingNode.y = mouse.y;
        draggingNode.vx = 0;
        draggingNode.vy = 0;
        draw();
    }}
}});

canvas.addEventListener("mouseup", () => {{
    draggingNode = null;
}});

canvas.addEventListener("click", event => {{
    const pos = getMousePos(event);
    const node = getNodeAt(pos.x, pos.y);

    if (node) {{
        selectedNode = node;
        showNodeDetails(node);
        draw();
    }}
}});

function showNodeDetails(node) {{
    const details = document.getElementById("nodeDetails");
    const raw = document.getElementById("rawDetails");

    details.innerHTML = `
        <p><b>Name:</b> ${{node.name}}</p>
        <p><b>Type:</b> <span class="pill">${{node.entity_type}}</span></p>
        <p><b>Mentions:</b> ${{node.mention_count}}</p>
        <p><b>Pages:</b> ${{(node.pages || []).join(", ") || "N/A"}}</p>
        <p><b>Chunks:</b> ${{(node.chunk_ids || []).slice(0, 5).join(", ")}}</p>
    `;

    raw.textContent = JSON.stringify(node, null, 2);
}}

function searchNode() {{
    const query = document.getElementById("searchBox").value.trim().toLowerCase();

    if (!query) return;

    const found = nodes.find(node =>
        node.name.toLowerCase().includes(query) ||
        node.entity_id.toLowerCase().includes(query)
    );

    if (!found) {{
        alert("Entity not found in displayed graph.");
        return;
    }}

    selectedNode = found;
    found.x = canvas.width / 2;
    found.y = canvas.height / 2;
    showNodeDetails(found);
    draw();
}}

function resetLayout() {{
    for (const node of nodes) {{
        node.x = randomBetween(80, canvas.width - 80);
        node.y = randomBetween(80, canvas.height - 80);
        node.vx = 0;
        node.vy = 0;
    }}

    runLayoutSteps(100);
    draw();
}}

function toggleLabels() {{
    showLabels = !showLabels;
    draw();
}}

resizeCanvas();
loadGraph();
animate();
</script>

</body>
</html>
"""
