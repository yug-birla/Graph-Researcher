import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.core.config import settings


DOCUMENT_INDEX_PATH = settings.PROCESSED_DIR / "document_index.json"


def load_document_index() -> Dict[str, Any]:
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not DOCUMENT_INDEX_PATH.exists():
        return {}

    with open(DOCUMENT_INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_document_index(index: Dict[str, Any]) -> None:
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with open(DOCUMENT_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def find_duplicate_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    index = load_document_index()
    return index.get(file_hash)


def register_document_hash(
    document_id: str,
    source_file_name: str,
    file_type: str,
    file_hash: str
) -> None:

    index = load_document_index()

    index[file_hash] = {
        "document_id": document_id,
        "source_file_name": source_file_name,
        "file_type": file_type,
        "file_hash": file_hash,
        "registered_at": datetime.now(timezone.utc).isoformat()
    }

    save_document_index(index)


def remove_document_from_index(document_id: str) -> Optional[Dict[str, Any]]:
    index = load_document_index()

    hash_to_remove = None
    removed_entry = None

    for file_hash, document_info in index.items():
        if document_info.get("document_id") == document_id:
            hash_to_remove = file_hash
            removed_entry = document_info
            break

    if hash_to_remove is not None:
        del index[hash_to_remove]
        save_document_index(index)

    return removed_entry
