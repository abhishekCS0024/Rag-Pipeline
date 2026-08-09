# API request/response Pydantic schemas for the /rag/query chat endpoint.
import uuid

from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    query: str


class CitationResponse(BaseModel):
    document_id: uuid.UUID
    chunk_index: int
    section: str | None
    page: int | None


class ChatQueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
