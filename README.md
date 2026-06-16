
# GraphResearcher

## Citation-Grounded GraphRAG Document Intelligence Platform

GraphResearcher is a full-stack AI document intelligence platform that allows users to upload documents, ask questions, verify answers through sources, inspect document graphs, compare two documents, submit feedback, and monitor the system through a secure admin dashboard.

The project is built around the idea that a document chatbot should not only answer questions, but should also show **where the answer came from**.

<p align="center">
  <b>RAG + GraphRAG + Source Verification + Document Comparison + Admin Monitoring</b>
</p>

<p align="center">
  <a href="https://yugbirla-graphresearcher.hf.space">Live Demo</a> •
  <a href="https://yugbirla-graphresearcher.hf.space/app">User App</a> •
  <a href="https://yugbirla-graphresearcher.hf.space/admin/secure">Admin Dashboard</a>
</p>

---
## Project Highlights

* Upload and chat with PDFs/documents
* Ask questions without manually entering document IDs
* Source-backed answers with page and chunk metadata
* Separate source panel for verification
* Open exact source detail page
* GraphRAG-based entity and relation graph generation
* Graph visualization for uploaded documents
* Multi-document comparison
* Feedback collection with optional permanent Hugging Face Dataset backup
* Secure admin dashboard for monitoring storage, routes, security, and feedback
* Hugging Face Spaces deployment

---

## Problem Statement

Most PDF chatbots give answers without clearly showing the supporting evidence. This makes them difficult to trust, especially for research, learning, documentation, and professional workflows.

GraphResearcher solves this by building a system where every answer is connected to retrieved document context and where the user can verify the answer using source cards, source detail pages, page metadata, and chunk metadata.

The goal is to make document question answering:

* more reliable,
* more transparent,
* more inspectable,
* and more useful for real document analysis.

---

## Live Links

| Page                   | Link                                                     |
| ---------------------- | -------------------------------------------------------- |
| Landing page           | `https://yugbirla-graphresearcher.hf.space`              |
| User app               | `https://yugbirla-graphresearcher.hf.space/app`          |
| Login page             | `https://yugbirla-graphresearcher.hf.space/login`        |
| Secure admin dashboard | `https://yugbirla-graphresearcher.hf.space/admin/secure` |

---

## Core Features

### User Features

| Feature                         | Status      |
| ------------------------------- | ----------- |
| Landing page                    | Implemented |
| ChatGPT-style document chat UI  | Implemented |
| Document upload                 | Implemented |
| Automatic document selection    | Implemented |
| Document indexing / re-indexing | Implemented |
| Document question answering     | Implemented |
| Multiple answer styles          | Implemented |
| Source cards                    | Implemented |
| Open source detail page         | Implemented |
| Build / rebuild graph           | Implemented |
| View document graph             | Implemented |
| Compare two documents           | Implemented |
| Delete selected document        | Implemented |
| Clear browser workspace cache   | Implemented |
| Feedback submission             | Implemented |

### Admin Features

| Feature                           | Status      |
| --------------------------------- | ----------- |
| Hidden admin page                 | Implemented |
| Secure admin monitoring dashboard | Implemented |
| Admin email allowlist             | Implemented |
| Admin dashboard key               | Implemented |
| Storage monitoring                | Implemented |
| Route monitoring                  | Implemented |
| Security configuration report     | Implemented |
| Feedback monitoring               | Implemented |
| Feedback JSONL export             | Implemented |
| Admin audit logging               | Implemented |

---

## System Architecture

```text
User Browser
    |
    | Upload / Ask / Compare / Feedback
    v
FastAPI Backend
    |
    |-- Document Upload
    |-- Document Parsing
    |-- Chunking + Metadata
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
    |-- Answer Generation
    |      |-- Retrieved Context
    |      |-- LLM Response
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

## How It Works

```text
1. User uploads a document.
2. Backend assigns a document ID.
3. Document text is extracted.
4. Text is split into smaller chunks.
5. Each chunk stores metadata such as:
   - document ID
   - file name
   - page number when available
   - chunk ID
   - text preview
6. Chunks are indexed for retrieval.
7. Optional document graph is built using entities and relations.
8. User asks a question.
9. Retriever finds relevant chunks.
10. Graph context can add relationship-aware context.
11. LLM generates an answer using retrieved context.
12. UI shows a clean answer in the chat area.
13. Source panel shows supporting chunks separately.
14. User can open source details for verification.
```

---

## GraphRAG Layer

GraphResearcher includes a GraphRAG layer to capture relationships inside uploaded documents.

| Component              | Purpose                                                 |
| ---------------------- | ------------------------------------------------------- |
| Entity extraction      | Finds important concepts/entities from chunks           |
| Relation extraction    | Finds relationships between extracted entities          |
| Graph storage          | Stores nodes and edges for each document                |
| Graph visualization    | Allows users to inspect the document graph              |
| Graph context          | Adds graph-based context to answers                     |
| Graph-guided retrieval | Uses graph information to support retrieval             |
| Graph fusion           | Combines normal retrieval and graph-supported retrieval |

### Graph Endpoints

| Method | Route                                         | Purpose                    |
| ------ | --------------------------------------------- | -------------------------- |
| POST   | `/documents/{document_id}/graph/build`        | Build document graph       |
| GET    | `/documents/{document_id}/graph`              | Get graph data             |
| GET    | `/documents/{document_id}/graph/view`         | View graph visualization   |
| GET    | `/documents/{document_id}/graph/entities`     | Inspect entities           |
| GET    | `/documents/{document_id}/graph/search`       | Search graph               |
| GET    | `/documents/{document_id}/graph/neighborhood` | Inspect graph neighborhood |

---

## Metrics and Measurable Indicators

### Product Metrics

| Metric                               | Value |
| ------------------------------------ | ----: |
| Core user workflows supported        |   10+ |
| Main user-facing pages               |     3 |
| Secure admin dashboard               |     1 |
| Answer styles                        |     5 |
| Feedback categories                  |     5 |
| Document comparison mode             |     1 |
| Source verification fields           |    4+ |
| Runtime storage categories monitored |     4 |
| Feedback storage modes               |     2 |
| Admin monitoring sections            |     5 |

### Retrieval and Answering Metrics

| Metric                                     |   Current Value |
| ------------------------------------------ | --------------: |
| Default retrieval top-k                    |         8 to 10 |
| Graph entity limit                         |              12 |
| Graph retrieval top-k                      |          6 to 8 |
| Source preview length in UI                | ~260 characters |
| Feedback rating scale                      |          1 to 5 |
| Answer fallback for short answers          |         Enabled |
| Query improvement for step/build questions |         Enabled |

### Source Verification Coverage

| Verification Item                    | Available           |
| ------------------------------------ | ------------------- |
| Document name                        | Yes                 |
| Page number metadata                 | Yes, when available |
| Chunk ID                             | Yes                 |
| Source preview                       | Yes                 |
| Open source button                   | Yes                 |
| Source detail page                   | Yes                 |
| Citations separated from main answer | Yes                 |

### Admin Monitoring Metrics

The secure admin dashboard tracks:

| Monitoring Metric          | Purpose                                       |
| -------------------------- | --------------------------------------------- |
| Uploaded runtime items     | Shows uploaded files/items in runtime storage |
| Processed document folders | Shows indexed/processed document folders      |
| Runtime storage size       | Tracks storage usage                          |
| Runtime file count         | Tracks number of runtime files                |
| Routes count               | Shows available FastAPI routes                |
| Product DB status          | Confirms product database availability        |
| Admin key status           | Confirms admin dashboard key configuration    |
| Session secret status      | Confirms session security setup               |
| OAuth status               | Shows whether OAuth keys are configured       |
| Feedback count             | Shows collected feedback                      |
| Admin audit logs           | Tracks admin access events                    |

---

## Tech Stack

| Layer                | Technology                                            |
| -------------------- | ----------------------------------------------------- |
| Backend API          | FastAPI                                               |
| Data validation      | Pydantic                                              |
| Frontend             | HTML, CSS, JavaScript                                 |
| Deployment           | Hugging Face Spaces                                   |
| LLM provider         | Hugging Face Inference-compatible provider            |
| Deployed LLM setting | `Qwen/Qwen3-4B-Instruct-2507`                         |
| Runtime database     | SQLite                                                |
| Feedback backup      | Hugging Face Dataset                                  |
| Graph layer          | Custom entity-relation graph modules                  |
| Retrieval            | Hybrid retrieval + reranking + graph fusion           |
| Runtime storage      | `/tmp/graphrag/...`                                   |
| Admin security       | Session login + admin email allowlist + dashboard key |

---

## Important Routes

### User Routes

| Method | Route              | Purpose                 |
| ------ | ------------------ | ----------------------- |
| GET    | `/`                | Landing page            |
| GET    | `/app`             | Main user app           |
| GET    | `/login`           | Login page              |
| POST   | `/feedback`        | Submit feedback         |
| GET    | `/feedback/status` | Feedback storage status |

### Document Routes

| Method | Route                                               | Purpose                |
| ------ | --------------------------------------------------- | ---------------------- |
| POST   | `/documents/upload`                                 | Upload document        |
| POST   | `/documents/{document_id}/index`                    | Index/process document |
| POST   | `/documents/{document_id}/graph/build`              | Build graph            |
| GET    | `/documents/{document_id}/graph/view`               | View graph             |
| GET    | `/documents/{document_id}/sources/{source_id}/view` | Open source detail     |
| GET    | `/documents/{document_id}/storage`                  | Check document storage |
| DELETE | `/documents/{document_id}/delete`                   | Delete document        |
| POST   | `/documents/compare`                                | Compare two documents  |

### Admin Routes

| Method | Route                         | Purpose                  |
| ------ | ----------------------------- | ------------------------ |
| GET    | `/admin`                      | Basic hidden admin panel |
| GET    | `/admin/secure`               | Secure admin dashboard   |
| GET    | `/admin/api/monitor/overview` | Admin overview           |
| GET    | `/admin/api/monitor/storage`  | Storage monitoring       |
| GET    | `/admin/api/monitor/security` | Security monitoring      |
| GET    | `/admin/api/monitor/routes`   | Route monitoring         |
| GET    | `/admin/api/feedback`         | View feedback            |
| GET    | `/admin/api/feedback/export`  | Export feedback JSONL    |

---

## Environment Variables

### LLM / Hugging Face

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
ADMIN_EMAILS=admin@gmail.com
SESSION_SECRET_KEY=<long-random-secret>
ADMIN_DASHBOARD_KEY=<strong-admin-password>
```

### Feedback Backup

```env
HF_FEEDBACK_DATASET=yugbirla/graphresearcher-feedback
HF_FEEDBACK_TOKEN=<huggingface-write-token>
```

---

## Runtime Storage

Current runtime paths:

```text
Original uploaded files: /tmp/graphrag/uploads
Processed chunks/graphs: /tmp/graphrag/processed
Vector database/runtime index: /tmp/graphrag/qdrant
Evaluation reports: /tmp/graphrag/evaluation
Feedback local files: /tmp/graphrag/feedback
```

Important note:

> Hugging Face runtime storage can reset after rebuild, restart, or runtime reset.
> Feedback can be backed up permanently to a private Hugging Face Dataset when `HF_FEEDBACK_DATASET` and `HF_FEEDBACK_TOKEN` are configured.

---

## Local Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd GraphResearcher
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/app
```

---

## User Workflow

```text
1. Open /app.
2. Clear Workspace Cache if needed.
3. Upload a PDF/document.
4. Ask a question.
5. View the answer in the chat area.
6. Check sources in the right-side source panel.
7. Open source detail if needed.
8. Build or view the document graph.
9. Upload a second document for comparison.
10. Submit feedback if answer quality or UI behavior needs improvement.
```

---

## Admin Workflow

```text
1. Login using admin dev session or configured login.
2. Open /admin/secure.
3. Enter ADMIN_DASHBOARD_KEY.
4. Monitor:
   - runtime storage,
   - FastAPI routes,
   - security configuration,
   - feedback,
   - admin audit logs.
5. Export feedback if required.
```

---

## Manual Smoke Test Checklist

| Test                      | Expected Result              |
| ------------------------- | ---------------------------- |
| Open `/`                  | Landing page loads           |
| Open `/app`               | App UI loads                 |
| Clear Workspace Cache     | Browser state resets         |
| Upload PDF                | Document appears in sidebar  |
| Ask normal question       | Answer appears               |
| Ask step-by-step question | Structured answer appears    |
| Change answer style       | Output style changes         |
| Open source               | Source detail opens          |
| Build graph               | Graph status updates         |
| View graph                | Graph visualization opens    |
| Upload second document    | Second document appears      |
| Compare documents         | Side-by-side answer appears  |
| Submit feedback           | Feedback is saved            |
| Open `/admin/secure`      | Secure admin dashboard opens |

---

## Limitations

| Limitation                              | Explanation                                                                                         |
| --------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Temporary document storage              | Uploaded files may disappear after Hugging Face rebuild/restart unless persistent storage is added. |
| OCR not fully productionized            | Scanned PDFs may need stronger OCR support.                                                         |
| Answer quality depends on retrieval     | Poor retrieval can lead to weak answers.                                                            |
| Feedback permanence needs token         | Permanent backup requires Hugging Face write token.                                                 |
| Multi-user storage is basic             | Full persistent per-user workspace is future work.                                                  |
| Vector deletion may need deeper cleanup | Runtime files are deleted, but vector DB point-level deletion may need extra backend work.          |

---

## Future Improvements

* Persistent document storage
* Stronger OCR for scanned PDFs
* Production Google OAuth flow
* Vector DB point-level deletion
* Better automatic evaluation metrics
* Role-based multi-user workspaces
* Stronger prompt optimization
* Persistent production database

---

## 30-Second Explanation

GraphResearcher is a document intelligence app where users can upload PDFs, ask questions, and verify answers using citations and source chunks. It combines RAG-style retrieval with a GraphRAG layer that extracts entities and relationships from documents. The app also supports graph visualization, multi-document comparison, feedback collection, and a secure admin monitoring dashboard.

---

## 2-Minute Explanation

GraphResearcher is a full-stack AI application for document-based question answering. The user uploads a document, and the backend processes it into searchable chunks while preserving metadata like document ID, page number, and chunk ID. When the user asks a question, the system retrieves relevant chunks, optionally uses graph context from extracted entities and relationships, and generates a grounded answer.

The app keeps the main answer clean and shows sources separately, so users can verify the answer using the right-side source panel or open the exact source detail page. It also includes graph visualization to inspect relationships inside the document and a comparison mode to compare two uploaded documents.

For admin use, the project includes a secure monitoring dashboard that tracks runtime storage, available routes, security configuration, feedback, and audit logs. Feedback can be saved locally and permanently backed up to a private Hugging Face Dataset. The project is deployed on Hugging Face Spaces and designed as a practical GraphRAG application with honest limitations around temporary runtime storage and OCR support.

---

## License

This project is licensed under the MIT License.
