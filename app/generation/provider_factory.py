from app.core.config import settings
from app.generation.providers.base_provider import BaseLLMProvider
from app.generation.providers.local_provider import LocalLLMProvider
from app.generation.providers.huggingface_provider import HuggingFaceLLMProvider
from app.generation.providers.disabled_provider import DisabledLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """
    Selects the active LLM provider using settings.LLM_PROVIDER.

    Supported:
    - local
    - huggingface
    - disabled
    """

    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "local":
        return LocalLLMProvider()

    if provider_name in ["hf", "huggingface", "hugging_face"]:
        return HuggingFaceLLMProvider()

    if provider_name in ["none", "off", "disabled"]:
        return DisabledLLMProvider()

    return DisabledLLMProvider()
