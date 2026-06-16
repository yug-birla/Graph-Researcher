from typing import Dict, Any

from app.core.config import settings
from app.generation.provider_factory import get_llm_provider


def generate_with_local_llm(prompt: str) -> str:
    """
    Backward-compatible function name.

    Earlier answer_service.py calls generate_with_local_llm().
    Now this routes to the configured provider:
    - local
    - huggingface
    - disabled
    """

    provider = get_llm_provider()
    return provider.generate(prompt)


def generate_with_configured_llm(prompt: str) -> str:
    provider = get_llm_provider()
    return provider.generate(prompt)


def get_llm_status() -> Dict[str, Any]:
    provider = get_llm_provider()
    provider_status = provider.status()

    return {
        "active_provider": settings.LLM_PROVIDER,
        "provider_status": provider_status,
        "available_providers": [
            "local",
            "huggingface",
            "disabled"
        ],
        "future_providers": [
            "aws_bedrock",
            "openai"
        ],
        "fallback_behavior": (
            "If the provider returns a weak or empty answer, "
            "answer_service uses evidence-based fallback."
        )
    }


def get_loaded_llm_info() -> Dict[str, Any]:
    provider = get_llm_provider()
    return provider.load_test()
