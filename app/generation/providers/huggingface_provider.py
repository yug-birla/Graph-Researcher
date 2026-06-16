from typing import Dict, Any
import requests
import re

from app.core.config import settings
from app.generation.providers.base_provider import BaseLLMProvider


class HuggingFaceLLMProvider(BaseLLMProvider):
    provider_name = "huggingface"

    def generate(self, prompt: str) -> str:
        if not settings.HF_API_TOKEN:
            return ""

        try:
            url = get_hf_inference_url()

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
                }
            }

            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=settings.HF_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                return ""

            data = response.json()
            answer = parse_huggingface_response(data)

            return clean_hosted_output(answer)

        except Exception:
            return ""

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": bool(settings.HF_API_TOKEN),
            "model_name": settings.HF_INFERENCE_MODEL,
            "custom_url_set": bool(settings.HF_INFERENCE_URL),
            "timeout_seconds": settings.HF_TIMEOUT_SECONDS,
            "token_present": bool(settings.HF_API_TOKEN)
        }

    def load_test(self) -> Dict[str, Any]:
        if not settings.HF_API_TOKEN:
            return {
                "loaded": False,
                "provider": self.provider_name,
                "message": "HF_API_TOKEN is missing."
            }

        try:
            test_prompt = "Answer briefly: What is RAG?"

            answer = self.generate(test_prompt)

            return {
                "loaded": bool(answer),
                "provider": self.provider_name,
                "model_name": settings.HF_INFERENCE_MODEL,
                "answer_preview": answer[:200],
                "message": "Hugging Face provider call completed."
            }

        except Exception as error:
            return {
                "loaded": False,
                "provider": self.provider_name,
                "model_name": settings.HF_INFERENCE_MODEL,
                "error": str(error)
            }


def get_hf_inference_url() -> str:
    if settings.HF_INFERENCE_URL:
        return settings.HF_INFERENCE_URL

    return f"https://api-inference.huggingface.co/models/{settings.HF_INFERENCE_MODEL}"


def parse_huggingface_response(data) -> str:
    if isinstance(data, list) and data:
        first_item = data[0]

        if isinstance(first_item, dict):
            if "generated_text" in first_item:
                return str(first_item["generated_text"])

            if "summary_text" in first_item:
                return str(first_item["summary_text"])

    if isinstance(data, dict):
        if "generated_text" in data:
            return str(data["generated_text"])

        if "summary_text" in data:
            return str(data["summary_text"])

        if "error" in data:
            return ""

    return ""


def clean_hosted_output(answer: str) -> str:
    if not answer:
        return ""

    cleaned = answer.strip()

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" .", ".")
    cleaned = cleaned.replace(" ,", ",")
    cleaned = cleaned.strip()

    return cleaned
