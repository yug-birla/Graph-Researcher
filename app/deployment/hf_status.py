import os
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
    return """
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
"""
