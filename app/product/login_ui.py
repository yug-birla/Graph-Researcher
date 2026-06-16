
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
