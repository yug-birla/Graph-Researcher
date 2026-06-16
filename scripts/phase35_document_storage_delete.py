from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

Path("app/product").mkdir(parents=True, exist_ok=True)

Path("app/product/document_storage_manager.py").write_text(r'''
import shutil
from pathlib import Path
from typing import Dict, Any, List

from app.core.config import settings


def as_path(value, fallback: str) -> Path:
    try:
        if value:
            return Path(value)
    except Exception:
        pass

    return Path(fallback)


def get_storage_paths() -> Dict[str, Path]:
    upload_dir = as_path(
        getattr(settings, "UPLOAD_DIR", None),
        "/tmp/graphrag/uploads"
    )

    processed_dir = as_path(
        getattr(settings, "PROCESSED_DIR", None),
        "/tmp/graphrag/processed"
    )

    qdrant_dir = as_path(
        getattr(settings, "QDRANT_LOCAL_PATH", None),
        "/tmp/graphrag/qdrant"
    )

    evaluation_dir = as_path(
        getattr(settings, "EVALUATION_DIR", None),
        "/tmp/graphrag/evaluation"
    )

    return {
        "upload_dir": upload_dir,
        "processed_dir": processed_dir,
        "qdrant_dir": qdrant_dir,
        "evaluation_dir": evaluation_dir
    }


def path_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0

    if path.is_file():
        try:
            return path.stat().st_size
        except Exception:
            return 0

    total = 0

    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except Exception:
                pass

    return total


def find_matching_items(root: Path, document_id: str) -> List[Dict[str, Any]]:
    matches = []

    if not root.exists():
        return matches

    for item in root.rglob("*"):
        try:
            item_name = item.name
            item_path = str(item)
        except Exception:
            continue

        if document_id in item_name or document_id in item_path:
            matches.append({
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size_bytes": path_size_bytes(item)
            })

    return matches


def get_document_storage_status(document_id: str) -> Dict[str, Any]:
    paths = get_storage_paths()

    processed_doc_dir = paths["processed_dir"] / document_id

    upload_matches = find_matching_items(paths["upload_dir"], document_id)
    processed_matches = find_matching_items(paths["processed_dir"], document_id)
    evaluation_matches = find_matching_items(paths["evaluation_dir"], document_id)

    processed_exists = processed_doc_dir.exists()

    return {
        "document_id": document_id,
        "storage_type": "runtime_ephemeral_storage",
        "important_note": (
            "On free/basic Hugging Face Spaces, files stored under /tmp can disappear "
            "after rebuild, restart, or runtime reset unless persistent storage is configured."
        ),
        "paths": {
            "upload_dir": str(paths["upload_dir"]),
            "processed_dir": str(paths["processed_dir"]),
            "processed_document_dir": str(processed_doc_dir),
            "qdrant_dir": str(paths["qdrant_dir"]),
            "evaluation_dir": str(paths["evaluation_dir"])
        },
        "exists": {
            "processed_document_dir": processed_exists,
            "upload_matches_found": len(upload_matches),
            "processed_matches_found": len(processed_matches),
            "evaluation_matches_found": len(evaluation_matches)
        },
        "sizes": {
            "processed_document_size_bytes": path_size_bytes(processed_doc_dir),
            "upload_matches_size_bytes": sum(x["size_bytes"] for x in upload_matches),
            "evaluation_matches_size_bytes": sum(x["size_bytes"] for x in evaluation_matches)
        },
        "matches": {
            "uploads": upload_matches[:50],
            "processed": processed_matches[:50],
            "evaluation": evaluation_matches[:50]
        },
        "status": "available" if processed_exists or upload_matches or processed_matches else "missing_or_runtime_reset",
        "recommendation": (
            "If this says missing_or_runtime_reset but the UI still shows the document, "
            "clear workspace cache and re-upload the document."
        )
    }


def remove_path(path: Path) -> Dict[str, Any]:
    result = {
        "path": str(path),
        "existed": path.exists(),
        "deleted": False,
        "error": None
    }

    if not path.exists():
        return result

    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

        result["deleted"] = True
    except Exception as exc:
        result["error"] = str(exc)

    return result


def delete_product_db_records(document_id: str) -> Dict[str, Any]:
    result = {
        "attempted": True,
        "deleted_records": {},
        "error": None
    }

    try:
        from app.product.product_db import get_connection, init_product_database

        init_product_database()
        conn = get_connection()
        cur = conn.cursor()

        tables = [
            ("messages", "conversation_id", "SELECT conversation_id FROM conversations WHERE document_id = ?"),
            ("conversations", "document_id", None),
            ("user_documents", "document_id", None)
        ]

        # Delete messages belonging to conversations for this document
        cur.execute("SELECT conversation_id FROM conversations WHERE document_id = ?", (document_id,))
        conversation_ids = [row["conversation_id"] for row in cur.fetchall()]

        msg_count = 0
        for cid in conversation_ids:
            cur.execute("DELETE FROM messages WHERE conversation_id = ?", (cid,))
            msg_count += cur.rowcount

        result["deleted_records"]["messages"] = msg_count

        cur.execute("DELETE FROM conversations WHERE document_id = ?", (document_id,))
        result["deleted_records"]["conversations"] = cur.rowcount

        cur.execute("DELETE FROM user_documents WHERE document_id = ?", (document_id,))
        result["deleted_records"]["user_documents"] = cur.rowcount

        conn.commit()
        conn.close()

    except Exception as exc:
        result["error"] = str(exc)

    return result


def delete_document_storage(document_id: str) -> Dict[str, Any]:
    before = get_document_storage_status(document_id)
    paths = get_storage_paths()

    deleted_items = []

    processed_doc_dir = paths["processed_dir"] / document_id
    deleted_items.append(remove_path(processed_doc_dir))

    for match in before["matches"]["uploads"]:
        deleted_items.append(remove_path(Path(match["path"])))

    for match in before["matches"]["evaluation"]:
        deleted_items.append(remove_path(Path(match["path"])))

    db_result = delete_product_db_records(document_id)

    after = get_document_storage_status(document_id)

    return {
        "document_id": document_id,
        "status": "delete_attempt_complete",
        "before": before,
        "deleted_items": deleted_items,
        "database_cleanup": db_result,
        "after": after,
        "qdrant_note": (
            "This endpoint removes runtime files and DB records. "
            "Vector DB point-level deletion is not attempted here unless your existing vector store exposes a safe delete method. "
            "If stale vector results appear, rebuild/restart or add vector deletion in a later phase."
        )
    }
''', encoding="utf-8")


main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.product.document_storage_manager import" not in text:
    text = (
        "from app.product.document_storage_manager import get_document_storage_status, delete_document_storage\n"
        + text
    )

if "# Document storage status and delete endpoints" not in text:
    text += '''

# Document storage status and delete endpoints

@app.get("/documents/{document_id}/storage")
def document_storage_status(document_id: str):
    return get_document_storage_status(document_id)


@app.delete("/documents/{document_id}/delete")
def delete_document_runtime_storage(document_id: str):
    return delete_document_storage(document_id)
'''

main_path.write_text(text, encoding="utf-8")

print("Phase 35 document storage status and backend delete added.")
