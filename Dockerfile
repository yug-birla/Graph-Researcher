FROM python:3.11-slim

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
