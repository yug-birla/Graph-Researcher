from pathlib import Path

# Clean BOM
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")


# =====================================================
# 1. requirements.txt update
# =====================================================

req_path = Path("requirements.txt")

if req_path.exists():
    req = req_path.read_text(encoding="utf-8-sig")
else:
    req = ""

extras = [
    "authlib>=1.3.0",
    "itsdangerous>=2.1.2"
]

for item in extras:
    if item.split(">=")[0] not in req:
        req += "\n" + item

req_path.write_text(req.strip() + "\n", encoding="utf-8")
print("requirements.txt updated.")


# =====================================================
# 2. Session-aware auth service
# =====================================================

Path("app/product/auth_service.py").write_text(r'''
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


def get_session_user(request: Request):
    try:
        return request.session.get("user")
    except Exception:
        return None


def get_current_user_from_request(request: Request) -> Dict[str, Any]:
    """
    Preferred:
    - Session cookie from /login or Google OAuth

    Temporary dev fallback:
    - X-User-Email header, controlled by ALLOW_HEADER_AUTH
    """

    session_user = get_session_user(request)

    if session_user and session_user.get("email"):
        email = normalize_email(session_user.get("email"))
        role = infer_role(email)
        user_id = session_user.get("user_id") or make_user_id(email)

        user = upsert_user(
            user_id=user_id,
            email=email,
            name=session_user.get("name") or email.split("@")[0],
            role=role,
            auth_provider=session_user.get("auth_provider", "session")
        )

        user["authenticated"] = True
        return user

    allow_header_auth = os.getenv("ALLOW_HEADER_AUTH", "true").strip().lower() in {
        "1", "true", "yes", "y"
    }

    if allow_header_auth:
        email = normalize_email(request.headers.get("x-user-email"))
        name = request.headers.get("x-user-name")

        if email:
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

    return {
        "authenticated": False,
        "user_id": None,
        "email": None,
        "name": "Guest",
        "role": "guest",
        "auth_provider": "none"
    }


def require_authenticated_user(request: Request) -> Dict[str, Any]:
    user = get_current_user_from_request(request)

    if not user.get("authenticated"):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please login first."
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
        raise HTTPException(status_code=400, detail="email is required")

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
''', encoding="utf-8")


# =====================================================
# 3. OAuth service
# =====================================================

Path("app/product/oauth_service.py").write_text(r'''
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
''', encoding="utf-8")


# =====================================================
# 4. Login UI
# =====================================================

Path("app/product/login_ui.py").write_text(r'''
def get_login_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Login - GraphResearcher</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #1d4ed8);
            color: #0f172a;
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }

        .card {
            width: min(460px, 96vw);
            background: white;
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.32);
        }

        .brand {
            font-size: 28px;
            font-weight: 900;
            margin-bottom: 6px;
            letter-spacing: -0.8px;
        }

        .sub {
            color: #64748b;
            line-height: 1.6;
            margin-bottom: 24px;
        }

        .btn {
            display: block;
            width: 100%;
            text-align: center;
            text-decoration: none;
            border: none;
            border-radius: 12px;
            padding: 13px;
            font-weight: 900;
            margin-bottom: 12px;
            cursor: pointer;
        }

        .google {
            background: #2563eb;
            color: white;
        }

        .dark {
            background: #0f172a;
            color: white;
        }

        input {
            width: 100%;
            border: 1px solid #cbd5e1;
            border-radius: 11px;
            padding: 12px;
            margin-bottom: 10px;
        }

        .small {
            color: #64748b;
            font-size: 13px;
            line-height: 1.5;
        }

        .status {
            background: #f1f5f9;
            border-radius: 12px;
            padding: 12px;
            font-size: 13px;
            color: #334155;
            margin-top: 12px;
            white-space: pre-wrap;
        }
    </style>
</head>

<body>
    <div class="card">
        <div class="brand">GraphResearcher</div>
        <div class="sub">
            Login to upload documents, chat with sources, compare documents, and access your workspace.
        </div>

        <a class="btn google" href="/auth/google/login">Continue with Google</a>

        <p class="small">
            If Google OAuth is not configured yet, use dev login for local testing.
        </p>

        <input id="email" value="2006yugb@gmail.com" placeholder="email">
        <input id="name" value="Admin" placeholder="name">

        <button class="btn dark" onclick="devLogin()">Dev Login</button>

        <div id="status" class="status">Checking OAuth status...</div>
    </div>

<script>
async function checkStatus() {
    try {
        const res = await fetch("/auth/oauth-status");
        const data = await res.json();

        document.getElementById("status").textContent =
            "Google OAuth configured: " + data.google_oauth_configured +
            "\\nAdmin default: " + data.admin_email_default;
    } catch (error) {
        document.getElementById("status").textContent = "Could not load OAuth status.";
    }
}

function devLogin() {
    const email = encodeURIComponent(document.getElementById("email").value.trim());
    const name = encodeURIComponent(document.getElementById("name").value.trim());

    window.location.href = `/auth/dev-session?email=${email}&name=${name}`;
}

checkStatus();
</script>
</body>
</html>
"""
''', encoding="utf-8")


# =====================================================
# 5. Patch main.py
# =====================================================

main_path = Path("app/main.py")
main_text = main_path.read_text(encoding="utf-8-sig")
main_text = main_text.replace("\ufeff", "")

imports = '''
import os
from fastapi import Request, Query
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.product.login_ui import get_login_html
from app.product.oauth_service import (
    get_oauth_status,
    start_google_login,
    finish_google_login,
    dev_session_login,
    clear_session,
    get_session_payload
)
'''

if "from app.product.oauth_service import" not in main_text:
    main_text = imports + "\n" + main_text

# Insert SessionMiddleware after app = FastAPI(...) block
if "app.add_middleware(SessionMiddleware" not in main_text:
    lines = main_text.splitlines()
    insert_index = None

    for i, line in enumerate(lines):
        if "app = FastAPI(" in line:
            balance = 0
            for j in range(i, len(lines)):
                balance += lines[j].count("(")
                balance -= lines[j].count(")")
                if balance <= 0 and j >= i:
                    insert_index = j + 1
                    break
            break

    middleware_lines = [
        "",
        "app.add_middleware(",
        "    SessionMiddleware,",
        "    secret_key=os.getenv('SESSION_SECRET_KEY', 'dev-change-this-session-secret'),",
        "    same_site='lax',",
        "    https_only=False",
        ")",
        ""
    ]

    if insert_index is not None:
        lines[insert_index:insert_index] = middleware_lines
        main_text = "\n".join(lines) + "\n"
        print("Inserted SessionMiddleware.")
    else:
        print("WARNING: Could not find app = FastAPI(...) to insert SessionMiddleware.")

if "# OAuth login endpoints" not in main_text:
    main_text += '''

# OAuth login endpoints

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return get_login_html()


@app.get("/auth/oauth-status")
def auth_oauth_status():
    return get_oauth_status()


@app.get("/auth/session")
def auth_session(request: Request):
    return get_session_payload(request)


@app.get("/auth/google/login")
async def auth_google_login(request: Request):
    return await start_google_login(request)


@app.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    return await finish_google_login(request)


@app.get("/auth/dev-session")
def auth_dev_session(
    request: Request,
    email: str = Query(..., min_length=3),
    name: str = Query(None)
):
    return dev_session_login(
        request=request,
        email=email,
        name=name
    )


@app.get("/auth/logout")
def auth_logout(request: Request):
    return clear_session(request)
'''

main_path.write_text(main_text, encoding="utf-8")

print("Phase 32 Google OAuth + session login foundation added.")
