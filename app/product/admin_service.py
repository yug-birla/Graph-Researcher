
from typing import Dict, Any

from app.product.product_db import (
    get_database_status,
    list_users,
    list_documents,
    list_conversations
)


def get_admin_status(current_admin: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "ok",
        "message": "Admin backend is available.",
        "admin": {
            "email": current_admin.get("email"),
            "role": current_admin.get("role")
        },
        "database": get_database_status()
    }


def get_admin_users(limit: int = 100) -> Dict[str, Any]:
    users = list_users(limit=limit)

    return {
        "count": len(users),
        "users": users
    }


def get_admin_documents(limit: int = 100) -> Dict[str, Any]:
    documents = list_documents(limit=limit)

    return {
        "count": len(documents),
        "documents": documents
    }


def get_admin_conversations(limit: int = 100) -> Dict[str, Any]:
    conversations = list_conversations(limit=limit)

    return {
        "count": len(conversations),
        "conversations": conversations
    }


def get_admin_system_summary() -> Dict[str, Any]:
    db = get_database_status()

    return {
        "status": "ok",
        "database": db,
        "notes": [
            "Admin tools are separated from the normal user app.",
            "Normal users should not see API docs or GraphRAG console links.",
            "Admin APIs are protected by backend role checks."
        ]
    }
