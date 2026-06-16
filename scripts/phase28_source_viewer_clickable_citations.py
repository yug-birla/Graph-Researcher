from pathlib import Path
import re

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

Path("app/product").mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# 1. Create source_viewer.py
# -----------------------------------------------------

Path("app/product/source_viewer.py").write_text(r"""
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import settings


def safe_str(value) -> str:
    if value is None:
        return ""
    return str(value)


def html_escape(value: str) -> str:
    return (
        safe_str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def normalize(value) -> str:
    return safe_str(value).strip().lower()


def get_processed_document_dir(document_id: str) -> Path:
    return Path(settings.PROCESSED_DIR) / document_id


def load_json_file(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return None


def load_jsonl_file(path: Path) -> List[Dict[str, Any]]:
    rows = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except Exception:
            return rows

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        except Exception:
            pass

    return rows


def load_csv_file(path: Path) -> List[Dict[str, Any]]:
    rows = []

    for enc in ["utf-8", "utf-8-sig"]:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
            return rows
        except Exception:
            rows = []

    return rows


def flatten_json_records(data) -> List[Dict[str, Any]]:
    records = []

    if isinstance(data, dict):
        for key in ["chunks", "results", "pages", "items", "documents", "data"]:
            if isinstance(data.get(key), list):
                for item in data[key]:
                    if isinstance(item, dict):
                        records.append(item)

        if not records:
            records.append(data)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                records.append(item)

    return records


def collect_candidate_records(document_id: str) -> List[Dict[str, Any]]:
    doc_dir = get_processed_document_dir(document_id)
    processed_dir = Path(settings.PROCESSED_DIR)

    roots = []

    if doc_dir.exists():
        roots.append(doc_dir)

    if processed_dir.exists():
        roots.append(processed_dir)

    records = []
    seen_files = set()

    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path in seen_files:
                continue

            seen_files.add(path)

            suffix = path.suffix.lower()
            file_records = []

            if suffix == ".json":
                file_records = flatten_json_records(load_json_file(path))
            elif suffix == ".jsonl":
                file_records = load_jsonl_file(path)
            elif suffix == ".csv":
                file_records = load_csv_file(path)

            for record in file_records:
                enriched = dict(record)
                enriched["_source_file_path"] = str(path)
                records.append(enriched)

    return records


def value_from(record: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        if key in record and record[key] not in [None, ""]:
            return safe_str(record[key])

    metadata = record.get("metadata")

    if isinstance(metadata, dict):
        for key in keys:
            if key in metadata and metadata[key] not in [None, ""]:
                return safe_str(metadata[key])

    return default


def record_text(record: Dict[str, Any]) -> str:
    return value_from(
        record,
        [
            "text",
            "content",
            "chunk_text",
            "page_text",
            "cleaned_text",
            "raw_text",
            "body",
            "preview",
            "text_preview",
            "chunk_preview"
        ],
        ""
    )


def record_match_score(
    record: Dict[str, Any],
    source_id: str,
    page: Optional[str] = None,
    chunk_id: Optional[str] = None
) -> int:
    score = 0

    source_id_norm = normalize(source_id)
    page_norm = normalize(page)
    chunk_id_norm = normalize(chunk_id)

    candidate_source_values = [
        value_from(record, ["source_id", "citation_id", "id", "source"]),
        value_from(record, ["chunk_id", "chunk", "chunk_index", "chunk_number"]),
        value_from(record, ["page_id", "page_source_id"])
    ]

    candidate_page_values = [
        value_from(record, ["page", "page_number", "page_no", "page_index"])
    ]

    candidate_chunk_values = [
        value_from(record, ["chunk_id", "chunk", "chunk_index", "chunk_number", "id"])
    ]

    if source_id_norm:
        for value in candidate_source_values:
            value_norm = normalize(value)

            if value_norm == source_id_norm:
                score += 10
            elif source_id_norm in value_norm or value_norm in source_id_norm:
                score += 3

    if page_norm:
        for value in candidate_page_values:
            if normalize(value) == page_norm:
                score += 5

    if chunk_id_norm:
        for value in candidate_chunk_values:
            if normalize(value) == chunk_id_norm:
                score += 8

    if record_text(record):
        score += 1

    return score


def find_best_source_record(
    document_id: str,
    source_id: str,
    page: Optional[str] = None,
    chunk_id: Optional[str] = None
) -> Dict[str, Any]:
    records = collect_candidate_records(document_id)

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No processed records found. Upload/index the document first."
        )

    scored = []

    for record in records:
        score = record_match_score(
            record=record,
            source_id=source_id,
            page=page,
            chunk_id=chunk_id
        )
        scored.append((score, record))

    scored.sort(key=lambda item: item[0], reverse=True)

    best_score, best_record = scored[0]

    if best_score <= 0:
        raise HTTPException(
            status_code=404,
            detail="Source record not found."
        )

    return best_record


def get_source_details(
    document_id: str,
    source_id: str,
    page: Optional[str] = None,
    chunk_id: Optional[str] = None
) -> Dict[str, Any]:
    record = find_best_source_record(
        document_id=document_id,
        source_id=source_id,
        page=page,
        chunk_id=chunk_id
    )

    document_name = value_from(
        record,
        ["document_name", "source_file_name", "file_name", "filename", "document_title"],
        "Selected document"
    )

    page_number = value_from(
        record,
        ["page", "page_number", "page_no", "page_index"],
        page or "Not available"
    )

    resolved_chunk_id = value_from(
        record,
        ["chunk_id", "chunk", "chunk_index", "chunk_number", "id"],
        chunk_id or source_id
    )

    text = record_text(record)

    return {
        "document_id": document_id,
        "source_id": source_id,
        "document_name": document_name,
        "page": page_number,
        "chunk_id": resolved_chunk_id,
        "text": text,
        "text_preview": text[:1200],
        "metadata": record,
        "source_file_path": record.get("_source_file_path")
    }


def get_source_html(
    document_id: str,
    source_id: str,
    page: Optional[str] = None,
    chunk_id: Optional[str] = None
) -> HTMLResponse:
    details = get_source_details(
        document_id=document_id,
        source_id=source_id,
        page=page,
        chunk_id=chunk_id
    )

    document_name = html_escape(details.get("document_name", "Selected document"))
    page_value = html_escape(details.get("page", "Not available"))
    chunk_value = html_escape(details.get("chunk_id", source_id))
    text_value = html_escape(details.get("text", "Source text not available."))
    metadata_value = html_escape(json.dumps(details.get("metadata", {}), indent=2, ensure_ascii=False))

    html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Source {html_escape(source_id)} - GraphResearcher</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {{
            font-family: Inter, Arial, sans-serif;
            background: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 32px;
        }}

        .container {{
            max-width: 980px;
            margin: 0 auto;
        }}

        .card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }}

        .pill {{
            display: inline-block;
            background: #eef2ff;
            color: #3730a3;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 13px;
            margin: 4px 5px 4px 0;
        }}

        pre {{
            white-space: pre-wrap;
            word-break: break-word;
            background: #0f172a;
            color: #e5e7eb;
            padding: 16px;
            border-radius: 14px;
            line-height: 1.55;
        }}

        .source-text {{
            white-space: pre-wrap;
            line-height: 1.75;
            font-size: 16px;
        }}

        a {{
            color: #2563eb;
            font-weight: 800;
            text-decoration: none;
        }}
    </style>
</head>

<body>
    <div class="container">
        <p><a href="/app">← Back to app</a></p>

        <div class="card">
            <h1>Source {html_escape(source_id)}</h1>
            <span class="pill">Document: {document_name}</span>
            <span class="pill">Page: {page_value}</span>
            <span class="pill">Chunk: {chunk_value}</span>
        </div>

        <div class="card">
            <h2>Evidence Text</h2>
            <div class="source-text">{text_value or "Source text not available."}</div>
        </div>

        <div class="card">
            <h2>Raw Metadata</h2>
            <pre>{metadata_value}</pre>
        </div>
    </div>
</body>
</html>
'''

    return HTMLResponse(content=html)
""", encoding="utf-8")


# -----------------------------------------------------
# 2. Patch main.py
# -----------------------------------------------------

main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

if "from app.product.source_viewer import" not in main_text:
    main_text = (
        "from app.product.source_viewer import get_source_details, get_source_html\n"
        + main_text
    )

if "# Source viewer endpoints" not in main_text:
    main_text += '''

# Source viewer endpoints

@app.get("/documents/{document_id}/sources/{source_id}")
def document_source_details(
    document_id: str,
    source_id: str,
    page: str = "",
    chunk_id: str = ""
):
    return get_source_details(
        document_id=document_id,
        source_id=source_id,
        page=page,
        chunk_id=chunk_id
    )


@app.get("/documents/{document_id}/sources/{source_id}/view", response_class=HTMLResponse)
def document_source_view(
    document_id: str,
    source_id: str,
    page: str = "",
    chunk_id: str = ""
):
    return get_source_html(
        document_id=document_id,
        source_id=source_id,
        page=page,
        chunk_id=chunk_id
    )
'''

main_path.write_text(main_text, encoding="utf-8")


# -----------------------------------------------------
# 3. Patch app UI button text only
# -----------------------------------------------------

hf_path = Path("app/deployment/hf_status.py")
ui_text = hf_path.read_text(encoding="utf-8-sig")
ui_text = ui_text.replace("\ufeff", "")

ui_text = ui_text.replace("View source details", "Open source details")

hf_path.write_text(ui_text, encoding="utf-8")

print("Fixed Phase 28 source viewer patch complete.")
