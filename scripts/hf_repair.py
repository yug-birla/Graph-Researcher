from pathlib import Path

# -----------------------------
# Dockerfile
# -----------------------------
Path("Dockerfile").write_text("""FROM python:3.11-slim

RUN useradd -m -u 1000 user

ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR $HOME/app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl git && rm -rf /var/lib/apt/lists/*

COPY --chown=user requirements.txt $HOME/app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . $HOME/app

USER user

ENV PORT=7860
ENV LLM_PROVIDER=huggingface
ENV ENABLE_LOCAL_LLM=false
ENV HF_INFERENCE_MODEL=google/flan-t5-base
ENV HF_TIMEOUT_SECONDS=60

ENV UPLOAD_DIR=data/uploads
ENV PROCESSED_DIR=data/processed
ENV QDRANT_LOCAL_PATH=data/qdrant
ENV EVALUATION_DIR=data/evaluation

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
""", encoding="utf-8")

# -----------------------------
# .dockerignore
# -----------------------------
Path(".dockerignore").write_text(""".git
.gitignore

venv
.venv
env

__pycache__
*.pyc
*.pyo
*.pyd

.env
.env.*
*.log

data/uploads
data/processed
data/qdrant
data/evaluation

outputs
reports
notebooks

*.pt
*.pth
*.bin
*.safetensors
*.onnx

.DS_Store
Thumbs.db
""", encoding="utf-8")

# -----------------------------
# README.md with HF metadata
# -----------------------------
Path("README.md").write_text("""---
title: GraphRAG Research Scientist
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# GraphRAG Research Scientist

A FastAPI-based GraphRAG research assistant for document-grounded question answering.

## Main endpoints

- `/` health check
- `/demo` simple browser demo
- `/docs` Swagger API docs
- `/deployment/health` deployment health
- `/deployment/config` deployment config
- `/upload` upload document
- `/documents/{document_id}/index` index document
- `/ask` ask question

## Hugging Face Variables

LLM_PROVIDER=huggingface  
ENABLE_LOCAL_LLM=false  
HF_INFERENCE_MODEL=google/flan-t5-base  
HF_TIMEOUT_SECONDS=60  

## Hugging Face Secret

HF_API_TOKEN should be added in Space Settings as a secret.
""", encoding="utf-8")

# -----------------------------
# app/deployment/hf_status.py
# -----------------------------
Path("app/deployment/hf_status.py").write_text("""import os
from typing import Dict, Any

from app.core.config import settings


def get_deployment_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "deployment_target": "hugging_face_spaces",
        "port": os.getenv("PORT", "7860"),
        "message": "FastAPI app is running and ready for Hugging Face Spaces."
    }


def get_deployment_config() -> Dict[str, Any]:
    return {
        "deployment_target": "hugging_face_spaces",
        "llm_provider": settings.LLM_PROVIDER,
        "local_llm_enabled": settings.ENABLE_LOCAL_LLM,
        "hf_model": settings.HF_INFERENCE_MODEL,
        "hf_token_present": bool(settings.HF_API_TOKEN),
        "upload_dir": str(settings.UPLOAD_DIR),
        "processed_dir": str(settings.PROCESSED_DIR),
        "qdrant_path": str(settings.QDRANT_LOCAL_PATH),
        "evaluation_dir": str(settings.EVALUATION_DIR),
        "reranker_enabled": settings.ENABLE_RERANKER,
        "storage_warning": "Local Space storage can reset after restart unless persistent storage is attached."
    }


def get_demo_html() -> str:
    return \"\"\"
<!DOCTYPE html>
<html>
<head>
    <title>GraphRAG Research Scientist</title>
</head>
<body style="font-family: Arial; max-width: 900px; margin: 40px auto; line-height: 1.6;">
    <h1>🧠 GraphRAG Research Scientist</h1>
    <p>FastAPI backend is running.</p>
    <h2>Useful links</h2>
    <ul>
        <li><a href="/docs">Swagger API Docs</a></li>
        <li><a href="/deployment/health">Deployment Health</a></li>
        <li><a href="/deployment/config">Deployment Config</a></li>
        <li><a href="/llm/status">LLM Status</a></li>
    </ul>
</body>
</html>
\"\"\"
""", encoding="utf-8")

# -----------------------------
# Patch main.py
# -----------------------------
main_path = Path("app/main.py")
text = main_path.read_text(encoding="utf-8")

if "from fastapi.responses import HTMLResponse" not in text:
    text = text.replace(
        "from fastapi.staticfiles import StaticFiles",
        "from fastapi.staticfiles import StaticFiles\nfrom fastapi.responses import HTMLResponse"
    )

if "from app.deployment.hf_status import" not in text:
    insert_after = "from app.generation.llm_service import get_llm_status, get_loaded_llm_info\n"
    deployment_import = (
        "from app.deployment.hf_status import (\n"
        "    get_deployment_health,\n"
        "    get_deployment_config,\n"
        "    get_demo_html\n"
        ")\n"
    )

    if insert_after in text:
        text = text.replace(insert_after, insert_after + deployment_import)
    else:
        text = deployment_import + text

for old in [
    "Phase 10 - LLM Provider Abstraction",
    "Phase 9 - Answer Evaluation System",
    "Phase 8 - Retrieval Evaluation System",
    "Phase 7 - Better Local LLM Strategy",
    "Phase 6.1 - Clean Answer Refinement",
    "Phase 6 - Answer Quality Improvement Layer"
]:
    text = text.replace(old, "Phase 11 - Hugging Face Deployment Readiness")

if "# Hugging Face deployment endpoints" not in text:
    text += '''

# Hugging Face deployment endpoints

@app.get("/deployment/health")
def deployment_health():
    return get_deployment_health()


@app.get("/deployment/config")
def deployment_config():
    return get_deployment_config()


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return get_demo_html()
'''

main_path.write_text(text, encoding="utf-8")

# -----------------------------
# requirements.txt safety
# -----------------------------
req_path = Path("requirements.txt")
req_text = req_path.read_text(encoding="utf-8")

if "requests" not in req_text:
    req_text += "\\nrequests\\n"

req_path.write_text(req_text, encoding="utf-8")

print("HF deployment repair files created successfully.")
