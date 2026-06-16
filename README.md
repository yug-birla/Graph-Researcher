---
title: GraphRAG Research Scientist
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# GraphRAG Research Scientist

A FastAPI-based GraphRAG research assistant for document-grounded question answering.

## Main endpoints

- `/` health check
- `/demo` simple browser demo
- `/docs` Swagger API docs
- `/deployment/health` deployment health
- `/deployment/config` deployment config
- `/upload` upload document
- `/documents/{document_id}/index` index document
- `/ask` ask question

## Hugging Face Variables

LLM_PROVIDER=huggingface  
ENABLE_LOCAL_LLM=false  
HF_INFERENCE_MODEL=google/flan-t5-base  
HF_TIMEOUT_SECONDS=60  

## Hugging Face Secret

HF_API_TOKEN should be added in Space Settings as a secret.
