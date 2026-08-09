# Pydantic schemas for RabbitMQ event payloads (e.g. DocumentUploadedEvent).
import uuid

from pydantic import BaseModel


class DocumentUploadedEvent(BaseModel):
    event: str = "document.uploaded"
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    s3_key: str


class DocumentReindexEvent(BaseModel):
    event: str = "document.reindex"
    document_id: uuid.UUID
    tenant_id: uuid.UUID


class DocumentDeleteEvent(BaseModel):
    event: str = "document.delete"
    document_id: uuid.UUID
    tenant_id: uuid.UUID
