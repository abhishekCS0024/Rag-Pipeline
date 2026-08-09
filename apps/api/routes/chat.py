# Query/RAG chat route: POST /rag/query (embed -> retrieve -> generate -> cite).
import uuid

from fastapi import APIRouter, Depends

from apps.api.dependencies import get_generation_service, get_retrieval_service
from src.generation.schemas import ChatQueryRequest, ChatQueryResponse, CitationResponse
from src.generation.service import GenerationService
from src.retrieval.service import RetrievalService

router = APIRouter()

# TODO: replace with tenant resolved from auth once AUTH_ENABLED is wired up.
DEFAULT_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


@router.post("/rag/query", response_model=ChatQueryResponse)
def query(
    request: ChatQueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    generation_service: GenerationService = Depends(get_generation_service),
) -> ChatQueryResponse:
    chunks = retrieval_service.retrieve(DEFAULT_TENANT_ID, request.query)
    result = generation_service.generate(request.query, chunks)

    return ChatQueryResponse(
        answer=result.answer,
        citations=[
            CitationResponse(
                document_id=c.document_id,
                chunk_index=c.chunk_index,
                section=c.section,
                page=c.page,
            )
            for c in result.citations
        ],
    )
