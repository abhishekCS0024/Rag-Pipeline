import io
import uuid

import pytest

from src.documents.service import DocumentService
from src.shared.config import Settings
from src.shared.exceptions import UnsupportedFileTypeError


class FakeStorage:
    def __init__(self):
        self.uploads: list[tuple[str, bytes, str]] = []

    def upload(self, key, fileobj, content_type):
        self.uploads.append((key, fileobj.read(), content_type))

    def download(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError


class FakeDocumentRepository:
    def __init__(self):
        self.created = []

    def create(self, **kwargs):
        from src.documents.models import Document
        from src.shared.constants import DocumentStatus

        document = Document(
            id=uuid.uuid4(),
            status=DocumentStatus.UPLOADED,
            created_at=None,
            updated_at=None,
            **kwargs,
        )
        self.created.append(document)
        return document

    def get_by_id(self, document_id):
        raise NotImplementedError

    def update_status(self, document_id, status):
        raise NotImplementedError


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
        allowed_file_types="pdf,docx,txt",
        max_upload_size_mb=1,
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def _make_service(monkeypatch, repository, storage, settings=None, publish=None):
    monkeypatch.setattr("src.documents.service.get_settings", lambda: settings or _settings())
    monkeypatch.setattr(
        "src.documents.service.publish_document_uploaded",
        publish or (lambda **kwargs: None),
    )
    return DocumentService(repository, storage)


def test_upload_stores_file_creates_record_and_publishes_event(monkeypatch):
    repository = FakeDocumentRepository()
    storage = FakeStorage()
    published = []
    service = _make_service(
        monkeypatch, repository, storage, publish=lambda **kwargs: published.append(kwargs)
    )
    tenant_id = uuid.uuid4()

    document = service.upload(
        tenant_id=tenant_id,
        filename="report.pdf",
        content_type="application/pdf",
        fileobj=io.BytesIO(b"hello"),
        size_bytes=5,
    )

    assert document in repository.created
    assert storage.uploads == [(document.storage_key, b"hello", "application/pdf")]
    assert document.storage_key.startswith(f"tenants/{tenant_id}/documents/")
    assert document.storage_key.endswith("/report.pdf")
    assert published == [
        {"document_id": document.id, "tenant_id": tenant_id, "s3_key": document.storage_key}
    ]


def test_upload_rejects_disallowed_extension(monkeypatch):
    repository = FakeDocumentRepository()
    storage = FakeStorage()
    service = _make_service(monkeypatch, repository, storage)

    with pytest.raises(UnsupportedFileTypeError):
        service.upload(
            tenant_id=uuid.uuid4(),
            filename="malware.exe",
            content_type="application/octet-stream",
            fileobj=io.BytesIO(b"x"),
            size_bytes=1,
        )

    assert repository.created == []
    assert storage.uploads == []


def test_upload_rejects_file_with_no_extension(monkeypatch):
    repository = FakeDocumentRepository()
    storage = FakeStorage()
    service = _make_service(monkeypatch, repository, storage)

    with pytest.raises(UnsupportedFileTypeError):
        service.upload(
            tenant_id=uuid.uuid4(),
            filename="noext",
            content_type="text/plain",
            fileobj=io.BytesIO(b"x"),
            size_bytes=1,
        )


def test_upload_rejects_file_exceeding_max_size(monkeypatch):
    repository = FakeDocumentRepository()
    storage = FakeStorage()
    service = _make_service(monkeypatch, repository, storage, settings=_settings(max_upload_size_mb=1))

    with pytest.raises(UnsupportedFileTypeError):
        service.upload(
            tenant_id=uuid.uuid4(),
            filename="big.pdf",
            content_type="application/pdf",
            fileobj=io.BytesIO(b"x"),
            size_bytes=2 * 1024 * 1024,
        )

    assert storage.uploads == []


def test_upload_uses_returned_document_id_for_publish_not_local_storage_key_id(monkeypatch):
    """Regression guard: the storage_key is built from a locally generated id
    before the repository assigns the real one (a real SQL-backed repository
    generates its own id independently), so the published event must use the
    id the repository actually returned, not the one embedded in the key.
    """
    repository = FakeDocumentRepository()
    storage = FakeStorage()
    published = []
    service = _make_service(
        monkeypatch, repository, storage, publish=lambda **kwargs: published.append(kwargs)
    )

    document = service.upload(
        tenant_id=uuid.uuid4(),
        filename="doc.txt",
        content_type="text/plain",
        fileobj=io.BytesIO(b"x"),
        size_bytes=1,
    )

    assert published[0]["document_id"] == document.id
