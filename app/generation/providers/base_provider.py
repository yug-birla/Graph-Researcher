from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    """
    Base interface for all LLM providers.

    Every provider must implement:
    - generate()
    - status()
    - load_test()
    """

    provider_name: str = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def load_test(self) -> Dict[str, Any]:
        pass
