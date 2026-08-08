import uuid

from pydantic import BaseModel


class DocumentUploadedEvent(BaseModel):
    event: str = "document.uploaded"
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    s3_key: str
