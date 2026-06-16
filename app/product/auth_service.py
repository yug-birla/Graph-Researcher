import os
from typing import Dict, Any, Optional

from fastapi import Request, HTTPException

from app.product.product_db import upsert_user


DEFAULT_ADMIN_EMAILS = {
    "2006yugb@gmail.com"
}


def get_admin_emails():
    raw = os.getenv("ADMIN_EMAILS", "")

    emails = {
        email.strip().lower()
        for email in raw.split(",")
        if email.strip()
    }

    return emails | DEFAULT_ADMIN_EMAILS


def normalize_email(email: Optional[str]) -> str:
    return str(email or "").strip().lower()


def make_user_id(email: str) -> str:
    return "user_" + email.replace("@", "_").replace(".", "_")


def infer_role(email: str) -> str:
    if normalize_email(email) in get_admin_emails():
        return "admin"

    return "user"


def get_current_user_from_request(request: Request) -> Dict[str, Any]:
    email = normalize_email(request.headers.get("x-user-email"))
    name = request.headers.get("x-user-name")

    if not email:
        return {
            "authenticated": False,
            "user_id": None,
            "email": None,
            "name": "Guest",
            "role": "guest",
            "auth_provider": "none"
        }

    role = infer_role(email)
    user_id = make_user_id(email)

    user = upsert_user(
        user_id=user_id,
        email=email,
        name=name or email.split("@")[0],
        role=role,
        auth_provider="header_dev"
    )

    user["authenticated"] = True

    return user


def require_authenticated_user(request: Request) -> Dict[str, Any]:
    user = get_current_user_from_request(request)

    if not user.get("authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. For dev testing, pass X-User-Email header."
        )

    return user


def require_admin_user(request: Request) -> Dict[str, Any]:
    user = require_authenticated_user(request)

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return user


def dev_login_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    email = normalize_email(email)

    if not email:
        raise HTTPException(
            status_code=400,
            detail="email is required"
        )

    role = infer_role(email)
    user_id = make_user_id(email)

    user = upsert_user(
        user_id=user_id,
        email=email,
        name=name or email.split("@")[0],
        role=role,
        auth_provider="dev_login"
    )

    user["authenticated"] = True
    user["dev_header_hint"] = {
        "X-User-Email": email,
        "X-User-Name": name or email.split("@")[0]
    }

    return user
