# Orchestrates the ingestion pipeline: download from storage, parse with Docling, then chunk.
import os
import tempfile
from pathlib import Path

from infrastructure.storage.base import StorageBackend
from src.documents.models import Document
from src.ingestion.chunker import chunk_document
from src.ingestion.models import Chunk
from src.ingestion.parser import DocumentParser
from src.shared.config import get_settings


class IngestionService:
    def __init__(self, storage: StorageBackend, parser: DocumentParser | None = None):
        self._storage = storage
        self._parser = parser or DocumentParser()
        self._settings = get_settings()

    def process(self, document: Document) -> list[Chunk]:
        content = self._storage.download(document.storage_key)
        suffix = Path(document.filename).suffix

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            parsed = self._parser.parse(tmp_path)
        finally:
            os.unlink(tmp_path)

        return chunk_document(
            parsed,
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            include_section_metadata=self._settings.include_section_metadata,
            include_page_metadata=self._settings.include_page_metadata,
        )
