# schema defines the shape of data entering or leaving a part of the application.

import uuid

from pydantic import BaseModel

from src.shared.constants import DocumentStatus


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: DocumentStatus


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    file_name: str
    status: DocumentStatus
