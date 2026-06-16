from typing import Dict, Any

from app.generation.providers.base_provider import BaseLLMProvider


class DisabledLLMProvider(BaseLLMProvider):
    provider_name = "disabled"

    def generate(self, prompt: str) -> str:
        return ""

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": False,
            "message": "LLM provider is disabled. Evidence-based fallback will be used."
        }

    def load_test(self) -> Dict[str, Any]:
        return {
            "loaded": False,
            "provider": self.provider_name,
            "message": "LLM provider is disabled."
        }
