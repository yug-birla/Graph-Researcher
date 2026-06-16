# GraphResearcher — Citation-Grounded GraphRAG Document Intelligence Platform

**GraphResearcher** is a document-question answering and research assistant web application built around **RAG + GraphRAG + source verification**.  
It lets users upload documents, ask natural-language questions, inspect citations, open exact source chunks, view document graphs, compare two documents, submit feedback, and monitor the system through a secure admin dashboard.

> Deployment: `https://yugbirla-graphresearcher.hf.space`  
> User App: `/app`  
> Secure Admin Dashboard: `/admin/secure`

---

## 1. Problem Statement

Normal PDF chatbots often answer without showing where the information came from. This makes them risky for research, learning, and professional use because the user cannot easily verify whether the answer is grounded in the document.

GraphResearcher solves this by combining:

- document upload and parsing,
- chunk-based retrieval,
- hybrid / graph-assisted retrieval,
- answer generation,
- citation and source verification,
- document graph visualization,
- multi-document comparison,
- admin monitoring,
- and feedback collection.

The main goal is not just to answer questions, but to make answers **traceable, inspectable, and document-grounded**.

---

## 2. Key Qualities of the Project

| Quality | How the project supports it |
|---|---|
| **Grounded answers** | Answers are generated using retrieved document chunks instead of free-form memory. |
| **Source verification** | The right panel shows document name, page metadata, chunk ID, preview, and source-opening option. |
| **GraphRAG support** | The app builds entity-relation graphs from documents and uses graph context during answering. |
| **User-friendly UI** | Users upload and chat without manually entering document IDs. |
| **Document comparison** | Two documents can be compared side-by-side. |
| **Admin monitoring** | Secure admin dashboard monitors storage, routes, security status, feedback, and runtime state. |
| **Feedback loop** | Users can submit feedback, which is stored locally and backed up to a private Hugging Face Dataset. |
| **Deployment-ready** | The app runs on Hugging Face Spaces with Docker-style runtime support. |
| **Honest limitations** | Runtime file storage is temporary unless persistent storage is configured. |

---

## 3. Feature Overview

### User Features

| Feature | Status |
|---|---|
| Home page / landing page | Implemented |
| ChatGPT-style app UI | Implemented |
| Document upload | Implemented |
| Auto document selection after upload | Implemented |
| Document indexing / re-indexing | Implemented |
| Ask questions over selected document | Implemented |
| Answer style selection | Implemented |
| Source cards with page/chunk metadata | Implemented |
| Open source detail page | Implemented |
| Build / rebuild graph | Implemented |
| View document graph | Implemented |
| Compare two documents | Implemented |
| Delete selected document | Implemented |
| Clear browser workspace cache | Implemented |
| Feedback submission | Implemented |

### Admin Features

| Feature | Status |
|---|---|
| Hidden admin dashboard | Implemented |
| Secure admin dashboard route | Implemented |
| Admin email allowlist | Implemented |
| Admin dashboard key | Implemented |
| Runtime storage monitoring | Implemented |
| Route monitoring | Implemented |
| Security configuration report | Implemented |
| Feedback monitoring | Implemented |
| Feedback JSONL export | Implemented |
| Admin audit log | Implemented |

---

## 4. Architecture

```text
User Browser
    |
    | Upload / Ask / Compare / Feedback
    v
FastAPI Backend
    |
    |-- Document Upload Service
    |-- Document Processing / Parsing
    |-- Chunking + Metadata Creation
    |-- Retrieval Layer
    |      |-- Hybrid Retrieval
    |      |-- Reranking
    |      |-- Graph Retrieval Fusion
    |
    |-- GraphRAG Layer
    |      |-- Entity Extraction
    |      |-- Relation Extraction
    |      |-- Graph Storage
    |      |-- Graph Visualization
    |
    |-- Answer Generation Layer
    |      |-- LLM Provider
    |      |-- Context-grounded Answering
    |      |-- Citation Metadata
    |
    |-- Product Layer
    |      |-- User App UI
    |      |-- Source Viewer
    |      |-- Document Compare
    |      |-- Feedback Service
    |      |-- Admin Monitoring
    |
    v
Runtime Storage / SQLite / Hugging Face Dataset Backup
```

---

## 5. Core System Pipeline

```text
1. User uploads a document.
2. Backend assigns a document ID.
3. Document text is extracted.
4. Extracted text is split into chunks.
5. Each chunk keeps metadata:
   - document ID
   - file name
   - page number when available
   - chunk ID
   - text preview
6. Chunks are indexed for retrieval.
7. Optional graph is built from document entities and relations.
8. User asks a question.
9. Retriever finds relevant chunks.
10. Graph context can add relationship-aware context.
11. LLM generates an answer from retrieved context.
12. UI shows clean answer in the chat area.
13. UI shows sources separately in the right-side source panel.
14. User can open exact source detail for verification.
```

---

## 6. GraphRAG Design

GraphResearcher does not stop at vector-style retrieval. It adds a graph layer to represent relationships inside the document.

### GraphRAG Components

| Component | Role |
|---|---|
| Entity extractor | Finds important entities/concepts in document chunks. |
| Relation extractor | Finds relationships between entities. |
| Graph storage | Stores graph nodes and edges for each document. |
| Graph visualization | Shows entity-relation graph in browser. |
| Graph context service | Adds graph-based context to answers. |
| Graph-guided retriever | Uses graph information to improve retrieval. |
| Graph fusion | Combines normal retrieval and graph-supported retrieval. |

### GraphRAG Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /documents/{document_id}/graph/build` | Build or rebuild document graph |
| `GET /documents/{document_id}/graph` | Get graph data |
| `GET /documents/{document_id}/graph/view` | Open graph visualization |
| `GET /documents/{document_id}/graph/entities` | Inspect extracted entities |
| `GET /documents/{document_id}/graph/search` | Search graph |
| `GET /documents/{document_id}/graph/neighborhood` | Inspect local graph neighborhood |

---

## 7. Metrics and Measurable Project Indicators

The project includes several measurable system-level metrics. Some are configuration metrics, some are product coverage metrics, and some are monitoring metrics visible from the admin dashboard.

### 7.1 Product Feature Metrics

| Metric | Value |
|---|---:|
| Core user workflows supported | 10+ |
| Main user-facing pages | 3 |
| Admin/monitoring pages | 1 secure dashboard |
| Answer styles available | 5 |
| Feedback categories available | 5 |
| Document comparison modes | 1 side-by-side comparison mode |
| Source verification fields shown | 4+ |
| Admin monitoring sections | 5 |
| Runtime storage categories monitored | 4 |
| Feedback storage modes | 2 |

### 7.2 Retrieval and Answering Configuration Metrics

| Metric | Current value |
|---|---:|
| Default retrieval `top_k` | 8 to 10 |
| Graph entity limit | 12 |
| Graph retrieval top-k | 6 to 8 |
| Supported answer styles | Detailed, concise, step-by-step, research, comparison |
| Source preview length in UI | Around 260 characters |
| Answer fallback mode | Enabled for short/weak answers |
| Query improvement for build/step questions | Enabled |

### 7.3 Source Verification Metrics

| Verification item | Included |
|---|---|
| Document name | Yes |
| Page number metadata | Yes, when available |
| Chunk ID | Yes |
| Source preview | Yes |
| Open source button | Yes |
| Raw metadata source page | Yes |
| Citations separated from main answer | Yes |

### 7.4 Admin Monitoring Metrics

The secure admin dashboard tracks:

| Monitoring metric | Purpose |
|---|---|
| Uploaded runtime items | Shows uploaded files/items present in runtime storage |
| Processed document folders | Shows indexed/processed document folders |
| Runtime storage size | Tracks storage used by upload, processed, qdrant, and evaluation directories |
| Runtime file count | Tracks number of files in storage locations |
| Routes count | Shows available FastAPI routes |
| Product DB existence | Confirms product database presence |
| Admin key configuration | Confirms whether dashboard key is enabled |
| Session secret configuration | Confirms whether session secret is set |
| OAuth configuration status | Shows whether Google OAuth keys exist |
| Recent admin audit events | Tracks admin monitoring access |
| Feedback count | Shows collected feedback records |

### 7.5 Feedback Metrics

| Metric | Value |
|---|---|
| Feedback types | General, answer quality, UI bug, source/citation issue, feature request |
| Rating scale | 1 to 5 |
| Local SQLite feedback storage | Yes |
| Local JSONL feedback storage | Yes |
| Permanent Hugging Face Dataset backup | Yes, when configured |
| Admin feedback export | JSONL export available |

### 7.6 Manual Smoke Test Coverage

The tested final workflow includes:

| Test workflow | Expected behavior |
|---|---|
| Clear workspace cache | Removes stale browser state |
| Upload PDF | Document appears in sidebar |
| Ask normal question | Answer appears in chat |
| Ask detailed/step question | Structured response appears |
| Change answer style | Output format changes |
| Open source | Source detail opens |
| Build graph | Graph status updates |
| View graph | Graph opens in new page |
| Upload second PDF | Second document appears |
| Compare documents | Side-by-side comparison appears |
| Delete document | Document removed from workspace |
| Open secure admin | Monitoring dashboard opens after login/key |

---

## 8. Important Routes

### User Routes

| Route | Purpose |
|---|---|
| `/` | Landing page |
| `/app` | Main user app |
| `/login` | Login/dev-login page |
| `/feedback/status` | Feedback storage status |

### Document Routes

| Route | Purpose |
|---|---|
| `POST /documents/upload` | Upload document |
| `POST /documents/{document_id}/index` | Index/process document |
| `POST /documents/{document_id}/graph/build` | Build graph |
| `GET /documents/{document_id}/graph/view` | View graph |
| `GET /documents/{document_id}/sources/{source_id}/view` | View source detail |
| `GET /documents/{document_id}/storage` | Check document storage |
| `DELETE /documents/{document_id}/delete` | Delete document storage |
| `POST /documents/compare` | Backend document comparison |

### Admin Routes

| Route | Purpose |
|---|---|
| `/admin` | Basic hidden admin panel |
| `/admin/secure` | Secure monitoring dashboard |
| `/admin/api/monitor/overview` | Admin overview metrics |
| `/admin/api/monitor/storage` | Storage monitoring |
| `/admin/api/monitor/security` | Security status |
| `/admin/api/monitor/routes` | Route monitoring |
| `/admin/api/feedback` | View feedback |
| `/admin/api/feedback/export` | Export feedback JSONL |

---

## 9. Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Data validation | Pydantic |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Hugging Face Spaces |
| LLM provider | Hugging Face Inference-compatible provider |
| Model setting used in deployment | `Qwen/Qwen3-4B-Instruct-2507` |
| Runtime DB | SQLite |
| Feedback backup | Hugging Face Dataset |
| Graph layer | Custom entity-relation graph modules |
| Retrieval | Hybrid retrieval + reranking + graph fusion |
| Storage | Runtime `/tmp/graphrag/...` paths |
| Admin security | Session login + admin email allowlist + admin dashboard key |

---

## 10. Environment Variables

### Core Runtime

```env
LLM_PROVIDER=huggingface
ENABLE_LOCAL_LLM=false
HF_API_MODE=chat
HF_INFERENCE_MODEL=Qwen/Qwen3-4B-Instruct-2507
HF_TIMEOUT_SECONDS=60
HF_API_TOKEN=<secret>
```

### Admin Security

```env
ADMIN_EMAILS=2006yugb@gmail.com
SESSION_SECRET_KEY=<long-random-secret>
ADMIN_DASHBOARD_KEY=<strong-admin-password>
```

### Feedback Backup

```env
HF_FEEDBACK_DATASET=yugbirla/graphresearcher-feedback
HF_FEEDBACK_TOKEN=<huggingface-write-token>
```

---

## 11. Runtime Storage

Current runtime paths:

```text
Original uploaded files: /tmp/graphrag/uploads
Processed chunks/graphs: /tmp/graphrag/processed
Vector database/runtime index: /tmp/graphrag/qdrant
Evaluation reports: /tmp/graphrag/evaluation
Feedback local files: /tmp/graphrag/feedback
```

Important note:

> Hugging Face runtime `/tmp` storage can reset after rebuild, restart, or runtime reset.  
> Feedback can be backed up permanently to a private Hugging Face Dataset when `HF_FEEDBACK_DATASET` and `HF_FEEDBACK_TOKEN` are configured.

---

## 12. Local Setup

```bash
git clone <your-repo-url>
cd graphrag-research-scientist/backend

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/app
```

---

## 13. Deployment

The project is deployed on Hugging Face Spaces.

```text
https://yugbirla-graphresearcher.hf.space
```

After each push to the Hugging Face Space repository, the Space rebuilds automatically.

---

## 14. Final User Workflow

```text
1. Open /app.
2. Clear Workspace Cache if needed.
3. Upload a PDF/document.
4. Ask a question.
5. View answer in the chat area.
6. Verify sources from the right-side source panel.
7. Open source detail when needed.
8. Build or view the document graph.
9. Upload a second document for comparison.
10. Submit feedback if answer quality or UI behavior needs improvement.
```

---

## 15. Admin Workflow

```text
1. Login using admin dev session or configured login.
2. Open /admin/secure.
3. Enter ADMIN_DASHBOARD_KEY.
4. Monitor:
   - storage,
   - routes,
   - security,
   - feedback,
   - admin audit logs.
5. Export feedback if needed.
```

---

## 16. Limitations

| Limitation | Explanation |
|---|---|
| Temporary document storage | Uploaded documents may disappear after Hugging Face rebuild/restart unless persistent storage is added. |
| OCR not fully productionized | Scanned PDFs may need stronger OCR support. |
| Answer quality depends on retrieval | If irrelevant chunks are retrieved, answer quality can degrade. |
| Feedback permanence needs token | Permanent dataset backup requires Hugging Face write token. |
| Multi-user storage is basic | Full production-level per-user persistent document workspace is future work. |
| Vector deletion may need deeper cleanup | Runtime files are deleted, but vector DB point-level deletion may require additional backend-specific deletion. |

---

## 17. Future Improvements

Only future work, not part of current final scope:

- persistent document storage,
- stronger OCR for scanned documents,
- production Google OAuth flow,
- vector DB point-level deletion,
- better automatic evaluation metrics,
- role-based multi-user workspaces,
- stronger prompt optimization,
- deployed persistent database.

---

## 18. Resume Bullets

- Built **GraphResearcher**, a citation-grounded GraphRAG document intelligence platform using FastAPI, hybrid retrieval, graph-based context, source verification, and Hugging Face Spaces deployment.
- Implemented document upload, parsing, chunking, retrieval, graph construction, graph visualization, source viewer, answer-style rendering, and multi-document comparison.
- Added secure admin monitoring with route, storage, security, feedback, and audit-log visibility using admin email allowlist and dashboard key authentication.
- Integrated a feedback collection system with SQLite/JSONL local storage and optional permanent backup to a private Hugging Face Dataset.

---

## 19. 30-Second Project Explanation

GraphResearcher is a document intelligence app where users can upload PDFs, ask questions, and verify answers using citations and source chunks. It combines RAG-style retrieval with a GraphRAG layer that extracts entities and relationships from documents. The app also supports graph visualization, multi-document comparison, feedback collection, and a secure admin monitoring dashboard. The main focus is not just answering questions, but making answers explainable and verifiable.

---

## 20. 2-Minute Project Explanation

GraphResearcher is a full-stack AI application for document-based question answering. The user uploads a document, and the backend processes it into searchable chunks while preserving metadata like document ID, page number, and chunk ID. When the user asks a question, the system retrieves relevant chunks, optionally uses graph context from extracted entities and relationships, and generates a grounded answer.

The app keeps the main answer clean and shows sources separately, so users can verify the answer using the right-side source panel or open the exact source detail page. It also includes graph visualization to inspect relationships inside the document and a comparison mode to compare two uploaded documents.

For admin use, the project includes a secure monitoring dashboard that tracks runtime storage, available routes, security configuration, feedback, and audit logs. Feedback can be saved locally and permanently backed up to a private Hugging Face Dataset. The project is deployed on Hugging Face Spaces and designed as a practical, resume-worthy GraphRAG application with honest limitations around temporary runtime storage and OCR support.
