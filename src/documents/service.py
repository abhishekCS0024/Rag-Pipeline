# What operation the application is trying to perform
# DocumentService - orchestrates upload validation, storage, DB persistence, RabbitMQ event publishing.

            #     HTTP Request
            #          │
            #          ▼
            #   API / Controller
            #          │
            #          ▼
            #     schemas.py
            #   "What data came in?"
            #          │
            #          ▼
            #     service.py
            #   "What should happen?"
            #          │
            #          ▼
            #   repository.py
            #   "Get/save the data"
            #          │
            #          ▼
            #      models.py
            #   "What is stored?"
            #          │
            #          ▼
            #      Database

import uuid
from typing import BinaryIO

from infrastructure.rabbitmq.publisher import publish_document_uploaded
from infrastructure.storage.base import StorageBackend
from src.documents.models import Document
from src.documents.repository import DocumentRepository
from src.shared.config import get_settings
from src.shared.exceptions import UnsupportedFileTypeError


class DocumentService:
    def __init__(self, repository: DocumentRepository, storage: StorageBackend):
        self._repository = repository
        self._storage = storage
        self._settings = get_settings()

    def upload(
        self,
        tenant_id: uuid.UUID,
        filename: str,
        content_type: str,
        fileobj: BinaryIO,
        size_bytes: int,
    ) -> Document:
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in self._settings.allowed_file_types_list:
            raise UnsupportedFileTypeError(f"file type '{extension}' is not allowed")

        max_bytes = self._settings.max_upload_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise UnsupportedFileTypeError(
                f"file exceeds max upload size of {self._settings.max_upload_size_mb}MB"
            )

        document_id = uuid.uuid4()
        storage_key = f"tenants/{tenant_id}/documents/{document_id}/{filename}"
        self._storage.upload(storage_key, fileobj, content_type)

        document = self._repository.create(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            storage_key=storage_key,
            checksum=None,
        )

        publish_document_uploaded(
            document_id=document.id,
            tenant_id=tenant_id,
            s3_key=storage_key,
        )

        return document
