from typing import Dict, Any, Optional
import time
import requests
import re

from app.core.config import settings
from app.generation.providers.base_provider import BaseLLMProvider


class HuggingFaceLLMProvider(BaseLLMProvider):
    provider_name = "huggingface"

    def __init__(self):
        self.last_error: Optional[str] = None
        self.last_status_code: Optional[int] = None
        self.last_api_mode: Optional[str] = None

    def generate(self, prompt: str) -> str:
        """
        Generate answer using Hugging Face hosted inference.

        Strategy:
        1. If model looks like chat/instruct provider model, try router chat API.
        2. Otherwise try HF inference model endpoint.
        3. If one fails, try the other.
        4. If all fail, return empty string so answer_service fallback is used.
        """

        self.last_error = None
        self.last_status_code = None
        self.last_api_mode = None

        if not settings.HF_API_TOKEN:
            self.last_error = "HF_API_TOKEN is missing."
            return ""

        api_mode = get_hf_api_mode()

        if api_mode == "chat":
            answer = self.call_chat_completion_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            answer = self.call_hf_inference_model_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""

        if api_mode == "inference":
            answer = self.call_hf_inference_model_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            answer = self.call_chat_completion_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""

        # auto mode
        if should_try_chat_first(settings.HF_INFERENCE_MODEL):
            first_answer = self.call_chat_completion_api(prompt)

            if first_answer:
                return clean_hosted_output(first_answer)

            second_answer = self.call_hf_inference_model_api(prompt)

            if second_answer:
                return clean_hosted_output(second_answer)

            return ""

        first_answer = self.call_hf_inference_model_api(prompt)

        if first_answer:
            return clean_hosted_output(first_answer)

        second_answer = self.call_chat_completion_api(prompt)

        if second_answer:
            return clean_hosted_output(second_answer)

        return ""

    def call_chat_completion_api(self, prompt: str) -> str:
        """
        Uses Hugging Face router OpenAI-compatible chat-completion endpoint.

        Best for provider-backed chat/instruct models.
        """

        self.last_api_mode = "chat"

        url = "https://router.huggingface.co/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": settings.HF_INFERENCE_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful research assistant. "
                        "Answer only from the supplied evidence and preserve citations like [S1]."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": settings.MAX_GENERATION_TOKENS,
            "temperature": 0
        }

        data = self.post_with_retries(url=url, headers=headers, payload=payload)

        if not data:
            return ""

        return parse_chat_completion_response(data)

    def call_hf_inference_model_api(self, prompt: str) -> str:
        """
        Uses Hugging Face HF Inference model endpoint.

        Better for classic text/text2text models like google/flan-t5-base.
        """

        self.last_api_mode = "inference"

        model_name = settings.HF_INFERENCE_MODEL

        if settings.HF_INFERENCE_URL:
            url = settings.HF_INFERENCE_URL
        else:
            url = f"https://router.huggingface.co/hf-inference/models/{model_name}"

        headers = {
            "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": settings.MAX_GENERATION_TOKENS,
                "do_sample": False,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True
            }
        }

        data = self.post_with_retries(url=url, headers=headers, payload=payload)

        if not data:
            return ""

        return parse_huggingface_inference_response(data)

    def post_with_retries(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        max_retries: int = 3
    ) -> Optional[Any]:

        retryable_status_codes = {429, 500, 502, 503, 504}

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=settings.HF_TIMEOUT_SECONDS
                )

                self.last_status_code = response.status_code

                if response.status_code == 200:
                    return response.json()

                error_text = response.text[:500]
                self.last_error = f"HTTP {response.status_code}: {error_text}"

                if response.status_code not in retryable_status_codes:
                    return None

                time.sleep(attempt * 2)

            except requests.Timeout:
                self.last_error = "Hugging Face request timed out."
                time.sleep(attempt * 2)

            except requests.RequestException as error:
                self.last_error = f"Request error: {str(error)}"
                time.sleep(attempt * 2)

            except Exception as error:
                self.last_error = f"Unexpected error: {str(error)}"
                return None

        return None

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": bool(settings.HF_API_TOKEN),
            "model_name": settings.HF_INFERENCE_MODEL,
            "api_mode": get_hf_api_mode(),
            "custom_url_set": bool(settings.HF_INFERENCE_URL),
            "timeout_seconds": settings.HF_TIMEOUT_SECONDS,
            "token_present": bool(settings.HF_API_TOKEN),
            "last_api_mode": self.last_api_mode,
            "last_status_code": self.last_status_code,
            "last_error": self.last_error,
            "notes": {
                "chat_mode": "Uses https://router.huggingface.co/v1/chat/completions",
                "inference_mode": "Uses https://router.huggingface.co/hf-inference/models/{model}",
                "fallback": "If hosted LLM fails, answer_service uses evidence-based fallback."
            }
        }

    def load_test(self) -> Dict[str, Any]:
        if not settings.HF_API_TOKEN:
            return {
                "loaded": False,
                "provider": self.provider_name,
                "message": "HF_API_TOKEN is missing."
            }

        test_prompt = (
            "Answer with one short sentence and include [S1]. "
            "Evidence: S1: RAG stands for Retrieval-Augmented Generation. [S1] "
            "Question: What is RAG?"
        )

        answer = self.generate(test_prompt)

        return {
            "loaded": bool(answer),
            "provider": self.provider_name,
            "model_name": settings.HF_INFERENCE_MODEL,
            "api_mode": get_hf_api_mode(),
            "last_api_mode": self.last_api_mode,
            "last_status_code": self.last_status_code,
            "last_error": self.last_error,
            "answer_preview": answer[:300],
            "message": (
                "Hosted Hugging Face provider test completed."
                if answer
                else "Hosted Hugging Face provider returned no usable answer. Fallback will still work."
            )
        }


def get_hf_api_mode() -> str:
    """
    Supported:
    - auto
    - chat
    - inference

    Default is auto.
    """

    mode = getattr(settings, "HF_API_MODE", "auto")
    mode = str(mode).lower().strip()

    if mode in ["chat", "inference", "auto"]:
        return mode

    return "auto"


def should_try_chat_first(model_name: str) -> bool:
    model_lower = model_name.lower()

    chat_markers = [
        "instruct",
        "chat",
        "qwen",
        "llama",
        "mistral",
        "gemma",
        "phi",
        ":"
    ]

    return any(marker in model_lower for marker in chat_markers)


def parse_chat_completion_response(data: Any) -> str:
    if not isinstance(data, dict):
        return ""

    choices = data.get("choices", [])

    if not choices:
        return ""

    first_choice = choices[0]

    if not isinstance(first_choice, dict):
        return ""

    message = first_choice.get("message", {})

    if isinstance(message, dict):
        content = message.get("content", "")

        if isinstance(content, str):
            return content

    text = first_choice.get("text", "")

    if isinstance(text, str):
        return text

    return ""


def parse_huggingface_inference_response(data: Any) -> str:
    if isinstance(data, list) and data:
        first_item = data[0]

        if isinstance(first_item, dict):
            for key in [
                "generated_text",
                "summary_text",
                "translation_text"
            ]:
                if key in first_item:
                    return str(first_item[key])

        if isinstance(first_item, str):
            return first_item

    if isinstance(data, dict):
        for key in [
            "generated_text",
            "summary_text",
            "translation_text"
        ]:
            if key in data:
                return str(data[key])

        if "error" in data:
            return ""

    if isinstance(data, str):
        return data

    return ""


def clean_hosted_output(answer: str) -> str:
    if not answer:
        return ""

    cleaned = answer.strip()

    unwanted_prefixes = [
        "final answer:",
        "answer:",
        "the answer is:",
        "output:"
    ]

    for prefix in unwanted_prefixes:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" .", ".")
    cleaned = cleaned.replace(" ,", ",")
    cleaned = cleaned.strip()

    return cleaned
