import uuid
from app.product.product_db import (
    init_product_database,
    get_database_status,
    upsert_user,
    list_users,
    register_document_record,
    list_documents,
    create_conversation,
    list_conversations,
    add_message,
    list_messages
)
from app.product.product_schema import (
    CreateLocalUserRequest,
    RegisterDocumentRequest,
    CreateConversationRequest,
    AddMessageRequest
)
from app.evaluation.graphrag_batch_evaluator import run_graphrag_batch_evaluation
from app.evaluation.graph_fusion_evaluator import compare_graph_fusion_retrieval
from app.graph.graph_guided_retriever import graph_guided_retrieve
from app.graph.graph_context_service import build_graph_context_for_query
from app.graph.graph_visualization import get_graph_visualization_html
from app.graph.graph_builder import build_document_graph
from app.graph.graph_storage import read_document_graph
from app.graph.graph_query_service import (
    list_entities,
    search_entities,
    get_entity_neighborhood
)
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.schemas.query_schema import AskRequest
from app.schemas.evaluation_schema import (
    RetrievalTestCaseCreate,
    RetrievalEvaluationRunRequest,
    AnswerTestCaseCreate,
    AnswerEvaluationRunRequest
)
from app.ingestion.ingestion_service import process_uploaded_file
from app.ingestion.reprocessing_service import reprocess_document_by_id
from app.storage.status_storage import (
    read_document_status,
    list_document_statuses
)
from app.storage.processed_storage import (
    read_processed_chunks,
    read_processed_metadata
)
from app.storage.document_delete_service import delete_document_by_id
from app.retrieval.indexing_service import index_document_chunks
from app.retrieval.hybrid_search_service import retrieve_chunks
from app.generation.answer_service import answer_question
from app.generation.llm_service import get_llm_status, get_loaded_llm_info
from app.deployment.hf_status import (
    get_deployment_health,
    get_deployment_config,
    get_demo_html, get_graphrag_demo_html
)
from app.evaluation.retrieval_eval_storage import (
    load_retrieval_test_cases,
    add_retrieval_test_case,
    delete_retrieval_test_case
)
from app.evaluation.retrieval_evaluator import run_retrieval_evaluation
from app.evaluation.answer_eval_storage import (
    load_answer_test_cases,
    add_answer_test_case,
    delete_answer_test_case
)
from app.evaluation.answer_evaluator import run_answer_evaluation


app = FastAPI(
    title=settings.APP_NAME,
    description="A production-grade multimodal GraphRAG research assistant",
    version=settings.APP_VERSION
)


if settings.ENABLE_STATIC_ASSETS:
    app.mount(
        "/processed-assets",
        StaticFiles(directory=str(settings.PROCESSED_DIR)),
        name="processed-assets"
    )


@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": f"{settings.APP_NAME} backend is alive",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "phase": "Phase 23 - Product Database Foundation"
    }


@app.get("/llm/status")
def llm_status():
    return get_llm_status()


@app.get("/llm/load-test")
def llm_load_test():
    return get_loaded_llm_info()


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return await process_uploaded_file(file)


@app.get("/documents")
def list_documents():
    documents = list_document_statuses()

    return {
        "total_documents": len(documents),
        "documents": documents
    }


@app.get("/documents/{document_id}/status")
def get_document_status(document_id: str):
    status = read_document_status(document_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document status not found."
        )

    return status


@app.get("/documents/{document_id}/chunks")
def get_document_chunks(
    document_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    content_type: Optional[str] = None
):
    chunks = read_processed_chunks(document_id)
    metadata = read_processed_metadata(document_id)

    if chunks is None:
        raise HTTPException(
            status_code=404,
            detail="Chunks not found for this document."
        )

    if content_type is not None:
        chunks = [
            chunk for chunk in chunks
            if chunk.content_type == content_type
        ]

    total_chunks = len(chunks)
    paginated_chunks = chunks[offset: offset + limit]

    return {
        "document_id": document_id,
        "metadata": metadata,
        "total_chunks": total_chunks,
        "returned_chunks": len(paginated_chunks),
        "offset": offset,
        "limit": limit,
        "content_type_filter": content_type,
        "chunks": paginated_chunks
    }


@app.post("/documents/{document_id}/index")
def index_document(document_id: str):
    result = index_document_chunks(document_id)

    if result["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result


@app.get("/search")
def search_documents(
    query: str = Query(..., min_length=1),
    document_id: Optional[str] = None,
    top_k: int = Query(5, ge=1, le=20),
    retrieval_mode: str = Query("hybrid")
):
    return retrieve_chunks(
        query=query,
        document_id=document_id,
        top_k=top_k,
        retrieval_mode=retrieval_mode
    )


@app.post("/ask")
def ask_question(request: AskRequest):
    return answer_question(
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k,
        retrieval_mode=request.retrieval_mode,
        use_reranker=request.use_reranker,
        use_llm=request.use_llm,
        use_graph=request.use_graph,
        graph_entity_limit=request.graph_entity_limit,
        use_graph_retrieval=request.use_graph_retrieval,
        graph_retrieval_top_k=request.graph_retrieval_top_k
    )


@app.get("/evaluation/retrieval/test-cases")
def list_retrieval_test_cases():
    test_cases = load_retrieval_test_cases()

    return {
        "total_test_cases": len(test_cases),
        "test_cases": test_cases
    }


@app.post("/evaluation/retrieval/test-cases")
def create_retrieval_test_case(test_case: RetrievalTestCaseCreate):
    created_test_case = add_retrieval_test_case(test_case)

    return {
        "status": "success",
        "message": "Retrieval test case created.",
        "test_case": created_test_case
    }


@app.delete("/evaluation/retrieval/test-cases/{test_case_id}")
def remove_retrieval_test_case(test_case_id: str):
    deleted = delete_retrieval_test_case(test_case_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Retrieval test case not found."
        )

    return {
        "status": "success",
        "message": "Retrieval test case deleted.",
        "test_case_id": test_case_id
    }


@app.post("/evaluation/retrieval/run")
def run_retrieval_eval(request: RetrievalEvaluationRunRequest):
    return run_retrieval_evaluation(request)


@app.get("/evaluation/answer/test-cases")
def list_answer_test_cases():
    test_cases = load_answer_test_cases()

    return {
        "total_test_cases": len(test_cases),
        "test_cases": test_cases
    }


@app.post("/evaluation/answer/test-cases")
def create_answer_test_case(test_case: AnswerTestCaseCreate):
    created_test_case = add_answer_test_case(test_case)

    return {
        "status": "success",
        "message": "Answer test case created.",
        "test_case": created_test_case
    }


@app.delete("/evaluation/answer/test-cases/{test_case_id}")
def remove_answer_test_case(test_case_id: str):
    deleted = delete_answer_test_case(test_case_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Answer test case not found."
        )

    return {
        "status": "success",
        "message": "Answer test case deleted.",
        "test_case_id": test_case_id
    }


@app.post("/evaluation/answer/run")
def run_answer_eval(request: AnswerEvaluationRunRequest):
    return run_answer_evaluation(request)


@app.post("/documents/{document_id}/reprocess")
def reprocess_document(document_id: str):
    try:
        result = reprocess_document_by_id(document_id)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document re-processing failed: {str(error)}"
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return result


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    deletion_result = delete_document_by_id(document_id)

    if deletion_result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "status": "success",
        "message": "Document deleted successfully.",
        "deletion_result": deletion_result
    }


# Hugging Face deployment endpoints

@app.get("/deployment/health")
def deployment_health():
    return get_deployment_health()


@app.get("/deployment/config")
def deployment_config():
    return get_deployment_config()


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return get_demo_html()


# Graph foundation endpoints

@app.post("/documents/{document_id}/graph/build")
def build_graph_for_document(document_id: str):
    result = build_document_graph(document_id)

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Graph build failed.")
        )

    return result


@app.get("/documents/{document_id}/graph")
def get_document_graph(document_id: str):
    graph = read_document_graph(document_id)

    if graph is None:
        raise HTTPException(
            status_code=404,
            detail="Graph not found. Build the graph first."
        )

    return graph


@app.get("/documents/{document_id}/graph/entities")
def get_graph_entities(
    document_id: str,
    limit: int = Query(50, ge=1, le=500),
    entity_type: Optional[str] = None
):
    result = list_entities(
        document_id=document_id,
        limit=limit,
        entity_type=entity_type
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result


@app.get("/documents/{document_id}/graph/search")
def search_graph_entities(
    document_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    result = search_entities(
        document_id=document_id,
        query=query,
        limit=limit
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result


@app.get("/documents/{document_id}/graph/neighborhood")
def get_graph_neighborhood(
    document_id: str,
    entity: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200)
):
    result = get_entity_neighborhood(
        document_id=document_id,
        entity=entity,
        limit=limit
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=404,
            detail=result.get("message")
        )

    return result


# Graph visualization endpoint

@app.get("/documents/{document_id}/graph/view", response_class=HTMLResponse)
def view_document_graph(document_id: str):
    return get_graph_visualization_html(document_id)


# Graph context debug endpoint

@app.get("/documents/{document_id}/graph/context")
def get_graph_context_for_question(
    document_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(8, ge=1, le=30)
):
    return build_graph_context_for_query(
        document_id=document_id,
        query=query,
        limit=limit
    )


# Graph-guided retrieval endpoint

@app.get("/documents/{document_id}/graph/retrieve")
def graph_guided_retrieval_endpoint(
    document_id: str,
    query: str = Query(..., min_length=1),
    graph_entity_limit: int = Query(8, ge=1, le=30),
    top_k: int = Query(5, ge=1, le=20)
):
    result = graph_guided_retrieve(
        document_id=document_id,
        query=query,
        graph_entity_limit=graph_entity_limit,
        top_k=top_k
    )

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result


# GraphRAG fusion evaluation endpoint

@app.get("/documents/{document_id}/evaluation/graph-fusion")
def evaluate_graph_fusion_for_document(
    document_id: str,
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    retrieval_mode: str = Query("hybrid"),
    use_reranker: bool = True,
    graph_entity_limit: int = Query(8, ge=1, le=30),
    graph_retrieval_top_k: int = Query(5, ge=1, le=20)
):
    return compare_graph_fusion_retrieval(
        document_id=document_id,
        query=query,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        use_reranker=use_reranker,
        graph_entity_limit=graph_entity_limit,
        graph_retrieval_top_k=graph_retrieval_top_k
    )


# GraphRAG batch evaluation endpoint

@app.get("/documents/{document_id}/evaluation/graph-fusion/batch")
def evaluate_graph_fusion_batch_for_document(
    document_id: str,
    custom_queries: Optional[str] = None,
    top_k: int = Query(5, ge=1, le=20),
    retrieval_mode: str = Query("hybrid"),
    use_reranker: bool = True,
    graph_entity_limit: int = Query(8, ge=1, le=30),
    graph_retrieval_top_k: int = Query(5, ge=1, le=20),
    compact: bool = True
):
    return run_graphrag_batch_evaluation(
        document_id=document_id,
        custom_queries=custom_queries,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        use_reranker=use_reranker,
        graph_entity_limit=graph_entity_limit,
        graph_retrieval_top_k=graph_retrieval_top_k,
        compact=compact
    )


# GraphRAG demo UI endpoint

@app.get("/graphrag-demo", response_class=HTMLResponse)
def graphrag_demo_page():
    return get_graphrag_demo_html()


# Product database foundation endpoints

@app.on_event("startup")
def initialize_product_database_on_startup():
    init_product_database()


@app.get("/product/db/status")
def product_database_status():
    return get_database_status()


@app.post("/product/users/local")
def create_or_update_local_user(request: CreateLocalUserRequest):
    user_id = "local_" + request.email.lower().replace("@", "_").replace(".", "_")

    return upsert_user(
        user_id=user_id,
        email=request.email,
        name=request.name,
        role=request.role,
        auth_provider="local"
    )


@app.get("/product/users")
def get_product_users(limit: int = Query(100, ge=1, le=500)):
    return {
        "users": list_users(limit=limit)
    }


@app.post("/product/documents/register")
def register_product_document(request: RegisterDocumentRequest):
    return register_document_record(
        document_id=request.document_id,
        source_file_name=request.source_file_name,
        owner_user_id=request.owner_user_id
    )


@app.get("/product/documents")
def get_product_documents(limit: int = Query(100, ge=1, le=500)):
    return {
        "documents": list_documents(limit=limit)
    }


@app.post("/product/conversations")
def create_product_conversation(request: CreateConversationRequest):
    conversation_id = str(uuid.uuid4())

    return create_conversation(
        conversation_id=conversation_id,
        owner_user_id=request.owner_user_id,
        document_id=request.document_id,
        title=request.title
    )


@app.get("/product/conversations")
def get_product_conversations(limit: int = Query(100, ge=1, le=500)):
    return {
        "conversations": list_conversations(limit=limit)
    }


@app.post("/product/messages")
def add_product_message(request: AddMessageRequest):
    message_id = str(uuid.uuid4())

    return add_message(
        message_id=message_id,
        conversation_id=request.conversation_id,
        role=request.role,
        content=request.content
    )


@app.get("/product/conversations/{conversation_id}/messages")
def get_product_conversation_messages(conversation_id: str):
    return {
        "conversation_id": conversation_id,
        "messages": list_messages(conversation_id=conversation_id)
    }
