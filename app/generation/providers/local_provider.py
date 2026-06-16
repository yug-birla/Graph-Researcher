from functools import lru_cache
from typing import Dict, Any
import re

import torch
from transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM
)

from app.core.config import settings
from app.generation.providers.base_provider import BaseLLMProvider


class LocalLLMProvider(BaseLLMProvider):
    provider_name = "local"

    def generate(self, prompt: str) -> str:
        if not settings.ENABLE_LOCAL_LLM:
            return ""

        try:
            llm_bundle = get_local_llm()

            tokenizer = llm_bundle["tokenizer"]
            model = llm_bundle["model"]
            model_type = llm_bundle["model_type"]

            if model_type == "seq2seq":
                answer = generate_seq2seq_answer(
                    tokenizer=tokenizer,
                    model=model,
                    prompt=prompt
                )
            else:
                answer = generate_causal_answer(
                    tokenizer=tokenizer,
                    model=model,
                    prompt=prompt
                )

            return clean_llm_output(answer)

        except Exception:
            return ""

    def status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "enabled": settings.ENABLE_LOCAL_LLM,
            "model_name": settings.LOCAL_LLM_MODEL_NAME,
            "device": settings.LOCAL_LLM_DEVICE,
            "max_generation_tokens": settings.MAX_GENERATION_TOKENS,
            "max_input_tokens": settings.LOCAL_LLM_MAX_INPUT_TOKENS,
            "min_answer_words": settings.MIN_LLM_ANSWER_WORDS
        }

    def load_test(self) -> Dict[str, Any]:
        try:
            llm_bundle = get_local_llm()

            return {
                "loaded": True,
                "provider": self.provider_name,
                "model_name": llm_bundle["model_name"],
                "model_type": llm_bundle["model_type"],
                "enabled": settings.ENABLE_LOCAL_LLM
            }

        except Exception as error:
            return {
                "loaded": False,
                "provider": self.provider_name,
                "model_name": settings.LOCAL_LLM_MODEL_NAME,
                "error": str(error)
            }


@lru_cache(maxsize=1)
def get_local_llm():
    tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_LLM_MODEL_NAME)
    config = AutoConfig.from_pretrained(settings.LOCAL_LLM_MODEL_NAME)

    if getattr(config, "is_encoder_decoder", False):
        model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.LOCAL_LLM_MODEL_NAME
        )
        model_type = "seq2seq"
    else:
        model = AutoModelForCausalLM.from_pretrained(
            settings.LOCAL_LLM_MODEL_NAME
        )
        model_type = "causal"

    model.eval()

    return {
        "tokenizer": tokenizer,
        "model": model,
        "model_type": model_type,
        "model_name": settings.LOCAL_LLM_MODEL_NAME
    }


def generate_seq2seq_answer(tokenizer, model, prompt: str) -> str:
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=settings.LOCAL_LLM_MAX_INPUT_TOKENS
    )

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=settings.MAX_GENERATION_TOKENS,
            do_sample=False,
            num_beams=4,
            early_stopping=True
        )

    answer = tokenizer.decode(
        output_ids[0],
        skip_special_tokens=True
    )

    return answer


def generate_causal_answer(tokenizer, model, prompt: str) -> str:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=settings.LOCAL_LLM_MAX_INPUT_TOKENS
    )

    input_length = inputs["input_ids"].shape[-1]

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=settings.MAX_GENERATION_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_ids = output_ids[0][input_length:]

    answer = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    )

    return answer


def clean_llm_output(answer: str) -> str:
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
