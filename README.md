---
title: GraphResearcher
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# GraphResearcher

![Python syntax check](https://github.com/yug-birla/Graph-Researcher/actions/workflows/python-syntax-check.yml/badge.svg)

Citation-grounded document intelligence platform combining RAG with graph-based retrieval.

**Live demo:** [yugbirla-graphresearcher.hf.space](https://yugbirla-graphresearcher.hf.space) · [App UI](https://yugbirla-graphresearcher.hf.space/app) · [Admin](https://yugbirla-graphresearcher.hf.space/admin/secure)

---

## Problem

PDF chatbots typically generate answers without showing where the information came from. Users cannot verify whether the output is grounded in the document. GraphResearcher addresses this by combining chunk-based retrieval, a document knowledge graph, source-level citation, and a verification UI that lets users trace every claim back to a specific page and chunk.

---

## Architecture

```text
User Browser
    │  Upload / Ask / Compare / Feedback
    ▼
FastAPI Backend
    ├── Ingestion: PDF parsing → chunking → metadata preservation
    ├── Retrieval: hybrid (BM25 + vector) → cross-encoder reranking → graph fusion
    ├── GraphRAG: entity extraction → relation extraction → graph storage → graph-guided retrieval
    ├── Generation: evidence extraction → grounded prompt → LLM answer → citation attachment
    ├── Product: app UI, source viewer, document comparison, feedback, admin monitoring
    └── Storage: runtime filesystem, SQLite, optional HF Dataset backup
```

---

## GraphRAG Algorithm

Entities are extracted from processed document chunks using rule-based pattern matching: capitalized multi-word phrases and uppercase acronyms are identified, normalized by stripping punctuation and deduplicating via lowercased entity IDs, and classified as CONCEPT, ACRONYM, ORGANIZATION, or TECHNICAL_TERM. Noisy candidates (stopwords, overly short/long strings) are filtered using a quality module. Relations are constructed by co-occurrence: when two or more entities appear in the same sentence, an edge is created between each pair, with the relation type inferred from verb phrases (e.g., "uses" → USES, "reduces" → REDUCES) or defaulting to RELATED_TO. Edge weights increment with repeated co-occurrence across chunks.

During answering, query terms are tokenized and matched against graph entity names and IDs using exact and substring scoring. The top-k matched entities and their neighboring relations are retrieved, and every chunk ID linked to those entities/relations receives a graph score based on entity mention count and relation weight. These graph-scored chunks are fused with normal hybrid retrieval results: chunks appearing in both lists get a score boost; graph-only chunks are appended. The fused set is re-sorted by score and truncated to the final top-k. The LLM prompt then includes both the standard evidence context and a structured graph context block listing matched entities (with types, mention counts, and pages) and relations (with types and weights).

---

## Evaluation

The project includes an ablation evaluation framework comparing **RAG only** vs. **RAG + Graph** retrieval.

**Metrics computed:**
- **Recall@K** (K=3,5,10): fraction of manually labeled gold chunk IDs retrieved in top K
- **Estimated faithfulness**: automatic heuristic checking whether answer sentences are supported by retrieved source text (not human judgment)
- **Answer completeness**: fraction of expected gold terms present in the answer
- **Latency**: end-to-end request time

<!-- EVAL_RESULTS_START -->

### 15-Question Starter Evaluation (Vectorless RAG Master Guide)

Generated: 2026-06-18
QA file: `eval/qa_15_starter.jsonl`

| Mode | Recall@3 | Recall@5 | Recall@10 | Faithfulness | Completeness | Avg Latency (ms) | Avg Answer Words | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RAG | 0.2944 | 0.4722 | 0.6389 | 0.9333 | 0.7167 | 7388.7 | 238.5 | 0 |
| RAG + Graph | 0.2944 | 0.4722 | 0.6389 | 0.9333 | 0.7167 | 7114.3 | 238.5 | 0 |

**Conclusion:** On this specific 15-question dataset, the rule-based GraphRAG implementation had **no significant effect** on retrieval recall or estimated faithfulness compared to standard hybrid retrieval with reranking. Latency was similar.

<!-- EVAL_RESULTS_END -->

---

## Setup

```bash
git clone https://github.com/yug-birla/Graph-Researcher.git
cd Graph-Researcher/backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
cp .env.example .env         # edit with your keys
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000/app`

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `huggingface`, `local`, or `disabled` |
| `HF_API_TOKEN` | Hugging Face API token for inference |
| `HF_INFERENCE_MODEL` | Model name (default: `Qwen/Qwen3-4B-Instruct-2507`) |
| `ADMIN_EMAILS` | Comma-separated admin email allowlist |
| `ADMIN_DASHBOARD_KEY` | Password for `/admin/secure` |
| `SESSION_SECRET_KEY` | Session middleware secret |
| `HF_FEEDBACK_DATASET` | Optional HF dataset for permanent feedback backup |
| `HF_FEEDBACK_TOKEN` | HF write token for feedback backup |

---

## Limitations

- **Temporary storage on HF Spaces.** Uploaded documents may disappear after runtime restart unless persistent storage is configured.
- **Rule-based entity extraction.** The graph layer uses regex patterns, not a trained NER model. It may miss entities that don't follow capitalization conventions and may extract noisy candidates.
- **Heuristic faithfulness.** The automatic faithfulness metric is a bag-of-words overlap check, not a semantic entailment model. It can overestimate faithfulness for topically relevant but factually incorrect answers.
- **No proven GraphRAG improvement yet.** The ablation framework exists but has not been run with verified gold labels. Whether graph-guided retrieval improves results on real documents is an open question until evaluation is completed.
- **OCR.** Scanned PDFs require stronger OCR support than currently provided.
- **Single-user storage.** Production-level per-user persistent document workspaces are future work.

---

## License

MIT
