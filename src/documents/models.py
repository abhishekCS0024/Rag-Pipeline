import uuid
from dataclasses import dataclass
from datetime import datetime

from src.shared.constants import DocumentStatus


@dataclass
class Document:
    id: uuid.UUID
    tenant_id: uuid.UUID
    filename: str
    content_type: str
    storage_key: str
    status: DocumentStatus
    checksum: str | None
    created_at: datetime
    updated_at: datetime
