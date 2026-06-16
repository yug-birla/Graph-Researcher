import os
from dataclasses import dataclass
from pathlib import Path


def get_int_env(variable_name: str, default_value: int) -> int:
    value = os.getenv(variable_name)

    if value is None:
        return default_value

    try:
        return int(value)
    except ValueError:
        return default_value


def get_float_env(variable_name: str, default_value: float) -> float:
    value = os.getenv(variable_name)

    if value is None:
        return default_value

    try:
        return float(value)
    except ValueError:
        return default_value


def get_bool_env(variable_name: str, default_value: bool) -> bool:
    value = os.getenv(variable_name)

    if value is None:
        return default_value

    value = value.lower().strip()

    if value in ["true", "1", "yes", "y"]:
        return True

    if value in ["false", "0", "no", "n"]:
        return False

    return default_value


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "GraphRAG Research Scientist"
    APP_VERSION: str = "10.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")

    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DIR", "data/processed"))
    QDRANT_LOCAL_PATH: Path = Path(os.getenv("QDRANT_LOCAL_PATH", "data/qdrant"))
    EVALUATION_DIR: Path = Path(os.getenv("EVALUATION_DIR", "data/evaluation"))

    DEFAULT_CHUNK_SIZE: int = get_int_env("DEFAULT_CHUNK_SIZE", 1000)
    DEFAULT_CHUNK_OVERLAP: int = get_int_env("DEFAULT_CHUNK_OVERLAP", 150)
    MAX_ROWS_PER_TABLE_BLOCK: int = get_int_env("MAX_ROWS_PER_TABLE_BLOCK", 50)
    MAX_UPLOAD_SIZE_MB: int = get_int_env("MAX_UPLOAD_SIZE_MB", 100)

    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_DIMENSION: int = get_int_env("EMBEDDING_DIMENSION", 384)

    QDRANT_COLLECTION_NAME: str = os.getenv(
        "QDRANT_COLLECTION_NAME",
        "research_chunks"
    )

    DEFAULT_TOP_K: int = get_int_env("DEFAULT_TOP_K", 5)

    HYBRID_VECTOR_WEIGHT: float = get_float_env("HYBRID_VECTOR_WEIGHT", 0.65)
    HYBRID_KEYWORD_WEIGHT: float = get_float_env("HYBRID_KEYWORD_WEIGHT", 0.35)

    ENABLE_RERANKER: bool = get_bool_env("ENABLE_RERANKER", True)
    RERANKER_MODEL_NAME: str = os.getenv(
        "RERANKER_MODEL_NAME",
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    RERANKER_CANDIDATE_MULTIPLIER: int = get_int_env(
        "RERANKER_CANDIDATE_MULTIPLIER",
        4
    )

    # =====================================================
    # LLM provider settings
    # =====================================================
    ENABLE_LOCAL_LLM: bool = get_bool_env("ENABLE_LOCAL_LLM", True)

    # Supported now:
    # local
    # huggingface
    # disabled
    #
    # Future:
    # aws_bedrock
    # openai
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "local")

    LOCAL_LLM_MODEL_NAME: str = os.getenv(
        "LOCAL_LLM_MODEL_NAME",
        "google/flan-t5-base"
    )

    LOCAL_LLM_DEVICE: str = os.getenv("LOCAL_LLM_DEVICE", "cpu")

    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    HF_INFERENCE_MODEL: str = os.getenv(
        "HF_INFERENCE_MODEL",
        "google/flan-t5-base"
    )
    HF_INFERENCE_URL: str = os.getenv(
        "HF_INFERENCE_URL",
        ""
    )
    HF_TIMEOUT_SECONDS: int = get_int_env("HF_TIMEOUT_SECONDS", 60)

    MAX_GENERATION_TOKENS: int = get_int_env("MAX_GENERATION_TOKENS", 220)
    LOCAL_LLM_MAX_INPUT_TOKENS: int = get_int_env("LOCAL_LLM_MAX_INPUT_TOKENS", 1024)

    MIN_LLM_ANSWER_WORDS: int = get_int_env("MIN_LLM_ANSWER_WORDS", 20)
    MAX_CONTEXT_CHARS: int = get_int_env("MAX_CONTEXT_CHARS", 5000)

    ENABLE_STATIC_ASSETS: bool = get_bool_env("ENABLE_STATIC_ASSETS", True)

    def ensure_directories(self) -> None:
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.QDRANT_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
        self.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
