
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.core.config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_database_path() -> Path:
    """
    Uses APP_DATABASE_PATH if provided.
    Otherwise stores DB near processed data.

    On Hugging Face free Spaces, this may be temporary unless persistent storage is attached.
    """
    env_path = os.getenv("APP_DATABASE_PATH")

    if env_path:
        db_path = Path(env_path)
    else:
        db_path = settings.PROCESSED_DIR.parent / "product_app.sqlite3"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection():
    db_path = get_database_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row) -> Dict[str, Any]:
    if row is None:
        return {}

    return dict(row)


def rows_to_dicts(rows) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]


def init_product_database() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        auth_provider TEXT DEFAULT 'local',
        avatar_url TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        last_login_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_documents (
        document_id TEXT PRIMARY KEY,
        owner_user_id TEXT,
        source_file_name TEXT,
        upload_status TEXT DEFAULT 'uploaded',
        index_status TEXT DEFAULT 'not_indexed',
        graph_status TEXT DEFAULT 'not_built',
        chunk_count INTEGER DEFAULT 0,
        entity_count INTEGER DEFAULT 0,
        relation_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        indexed_at TEXT,
        graph_built_at TEXT,
        metadata_json TEXT,
        FOREIGN KEY(owner_user_id) REFERENCES users(user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        owner_user_id TEXT,
        document_id TEXT,
        title TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(owner_user_id) REFERENCES users(user_id),
        FOREIGN KEY(document_id) REFERENCES user_documents(document_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        metadata_json TEXT,
        FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_logs (
        log_id TEXT PRIMARY KEY,
        actor_user_id TEXT,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id TEXT,
        created_at TEXT NOT NULL,
        metadata_json TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()

    tables = get_table_counts(conn)
    conn.close()

    return {
        "status": "success",
        "message": "Product database initialized.",
        "database_path": str(get_database_path()),
        "tables": tables
    }


def get_table_counts(conn=None) -> Dict[str, int]:
    should_close = False

    if conn is None:
        conn = get_connection()
        should_close = True

    cursor = conn.cursor()

    table_names = [
        "users",
        "user_documents",
        "conversations",
        "messages",
        "admin_logs",
        "app_settings"
    ]

    counts = {}

    for table in table_names:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        counts[table] = int(cursor.fetchone()["count"])

    if should_close:
        conn.close()

    return counts


def get_database_status() -> Dict[str, Any]:
    init_product_database()

    conn = get_connection()
    counts = get_table_counts(conn)
    conn.close()

    return {
        "status": "healthy",
        "database_path": str(get_database_path()),
        "table_counts": counts,
        "storage_note": "On free Hugging Face Spaces, SQLite data may reset unless persistent storage is enabled."
    }


def upsert_user(
    user_id: str,
    email: str,
    name: Optional[str] = None,
    role: str = "user",
    auth_provider: str = "local",
    avatar_url: Optional[str] = None
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (
        user_id, email, name, role, auth_provider, avatar_url,
        is_active, created_at, last_login_at
    )
    VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
        name = excluded.name,
        role = excluded.role,
        auth_provider = excluded.auth_provider,
        avatar_url = excluded.avatar_url,
        last_login_at = excluded.last_login_at
    """, (
        user_id,
        email,
        name,
        role,
        auth_provider,
        avatar_url,
        now,
        now
    ))

    conn.commit()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = row_to_dict(cursor.fetchone())

    conn.close()

    return user


def list_users(limit: int = 100) -> List[Dict[str, Any]]:
    init_product_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, email, name, role, auth_provider, is_active, created_at, last_login_at
    FROM users
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    users = rows_to_dicts(cursor.fetchall())
    conn.close()

    return users


def register_document_record(
    document_id: str,
    source_file_name: Optional[str] = None,
    owner_user_id: Optional[str] = None,
    upload_status: str = "uploaded"
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO user_documents (
        document_id, owner_user_id, source_file_name, upload_status,
        index_status, graph_status, created_at
    )
    VALUES (?, ?, ?, ?, 'not_indexed', 'not_built', ?)
    ON CONFLICT(document_id) DO UPDATE SET
        source_file_name = COALESCE(excluded.source_file_name, user_documents.source_file_name),
        owner_user_id = COALESCE(excluded.owner_user_id, user_documents.owner_user_id),
        upload_status = excluded.upload_status
    """, (
        document_id,
        owner_user_id,
        source_file_name,
        upload_status,
        now
    ))

    conn.commit()

    cursor.execute("SELECT * FROM user_documents WHERE document_id = ?", (document_id,))
    document = row_to_dict(cursor.fetchone())

    conn.close()

    return document


def update_document_index_status(
    document_id: str,
    index_status: str = "indexed",
    chunk_count: int = 0
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE user_documents
    SET index_status = ?, chunk_count = ?, indexed_at = ?
    WHERE document_id = ?
    """, (
        index_status,
        chunk_count,
        now,
        document_id
    ))

    conn.commit()

    cursor.execute("SELECT * FROM user_documents WHERE document_id = ?", (document_id,))
    document = row_to_dict(cursor.fetchone())

    conn.close()

    return document


def update_document_graph_status(
    document_id: str,
    graph_status: str = "built",
    entity_count: int = 0,
    relation_count: int = 0
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE user_documents
    SET graph_status = ?, entity_count = ?, relation_count = ?, graph_built_at = ?
    WHERE document_id = ?
    """, (
        graph_status,
        entity_count,
        relation_count,
        now,
        document_id
    ))

    conn.commit()

    cursor.execute("SELECT * FROM user_documents WHERE document_id = ?", (document_id,))
    document = row_to_dict(cursor.fetchone())

    conn.close()

    return document


def list_documents(limit: int = 100) -> List[Dict[str, Any]]:
    init_product_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM user_documents
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    documents = rows_to_dicts(cursor.fetchall())
    conn.close()

    return documents


def create_conversation(
    conversation_id: str,
    owner_user_id: Optional[str],
    document_id: Optional[str],
    title: str
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO conversations (
        conversation_id, owner_user_id, document_id, title, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        owner_user_id,
        document_id,
        title,
        now,
        now
    ))

    conn.commit()

    cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,))
    conversation = row_to_dict(cursor.fetchone())

    conn.close()

    return conversation


def list_conversations(limit: int = 100) -> List[Dict[str, Any]]:
    init_product_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM conversations
    ORDER BY updated_at DESC
    LIMIT ?
    """, (limit,))

    conversations = rows_to_dicts(cursor.fetchall())
    conn.close()

    return conversations


def add_message(
    message_id: str,
    conversation_id: str,
    role: str,
    content: str,
    metadata_json: Optional[str] = None
) -> Dict[str, Any]:
    init_product_database()

    now = utc_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (
        message_id, conversation_id, role, content, created_at, metadata_json
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        message_id,
        conversation_id,
        role,
        content,
        now,
        metadata_json
    ))

    cursor.execute("""
    UPDATE conversations
    SET updated_at = ?
    WHERE conversation_id = ?
    """, (
        now,
        conversation_id
    ))

    conn.commit()

    cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
    message = row_to_dict(cursor.fetchone())

    conn.close()

    return message


def list_messages(conversation_id: str) -> List[Dict[str, Any]]:
    init_product_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM messages
    WHERE conversation_id = ?
    ORDER BY created_at ASC
    """, (conversation_id,))

    messages = rows_to_dicts(cursor.fetchall())
    conn.close()

    return messages
