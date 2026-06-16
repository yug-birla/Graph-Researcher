
import os
from typing import Optional, Dict, Any

from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse

from app.product.auth_service import infer_role, make_user_id, normalize_email
from app.product.product_db import upsert_user

try:
    from authlib.integrations.starlette_client import OAuth
    AUTHLIB_AVAILABLE = True
    AUTHLIB_ERROR = None
except Exception as exc:
    OAuth = None
    AUTHLIB_AVAILABLE = False
    AUTHLIB_ERROR = str(exc)


def get_google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()


def get_google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()


def is_google_oauth_configured() -> bool:
    return bool(AUTHLIB_AVAILABLE and get_google_client_id() and get_google_client_secret())


def get_oauth_status() -> Dict[str, Any]:
    return {
        "authlib_available": AUTHLIB_AVAILABLE,
        "authlib_error": AUTHLIB_ERROR,
        "google_oauth_configured": is_google_oauth_configured(),
        "required_env_vars": [
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "SESSION_SECRET_KEY",
            "ADMIN_EMAILS"
        ],
        "admin_email_default": "2006yugb@gmail.com"
    }


def build_oauth_client():
    if not AUTHLIB_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail=f"Authlib is not installed or failed to import: {AUTHLIB_ERROR}"
        )

    if not get_google_client_id() or not get_google_client_secret():
        raise HTTPException(
            status_code=400,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    oauth = OAuth()

    oauth.register(
        name="google",
        client_id=get_google_client_id(),
        client_secret=get_google_client_secret(),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    return oauth


def set_user_session(
    request: Request,
    email: str,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    auth_provider: str = "session"
) -> Dict[str, Any]:
    email = normalize_email(email)

    if not email:
        raise HTTPException(status_code=400, detail="Email is required for login.")

    role = infer_role(email)
    user_id = make_user_id(email)

    user = upsert_user(
        user_id=user_id,
        email=email,
        name=name or email.split("@")[0],
        role=role,
        auth_provider=auth_provider,
        avatar_url=avatar_url
    )

    session_user = {
        "authenticated": True,
        "user_id": user_id,
        "email": email,
        "name": name or email.split("@")[0],
        "role": role,
        "avatar_url": avatar_url,
        "auth_provider": auth_provider
    }

    request.session["user"] = session_user

    return session_user


async def start_google_login(request: Request):
    oauth = build_oauth_client()

    redirect_uri = request.url_for("auth_google_callback")

    return await oauth.google.authorize_redirect(request, redirect_uri)


async def finish_google_login(request: Request):
    oauth = build_oauth_client()

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth callback failed: {exc}"
        )

    userinfo = token.get("userinfo")

    if not userinfo:
        try:
            userinfo = await oauth.google.parse_id_token(request, token)
        except Exception:
            userinfo = {}

    email = normalize_email(userinfo.get("email"))
    name = userinfo.get("name") or userinfo.get("given_name")
    avatar_url = userinfo.get("picture")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google login succeeded, but email was not returned."
        )

    set_user_session(
        request=request,
        email=email,
        name=name,
        avatar_url=avatar_url,
        auth_provider="google"
    )

    return RedirectResponse(url="/app", status_code=302)


def dev_session_login(request: Request, email: str, name: Optional[str] = None):
    set_user_session(
        request=request,
        email=email,
        name=name,
        avatar_url=None,
        auth_provider="dev_session"
    )

    return RedirectResponse(url="/app", status_code=302)


def clear_session(request: Request):
    try:
        request.session.clear()
    except Exception:
        pass

    return RedirectResponse(url="/login", status_code=302)


def get_session_payload(request: Request):
    try:
        user = request.session.get("user")
    except Exception:
        user = None

    if not user:
        return {
            "authenticated": False,
            "user": None
        }

    return {
        "authenticated": True,
        "user": user
    }
