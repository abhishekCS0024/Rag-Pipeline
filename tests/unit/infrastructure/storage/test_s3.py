import io

import pytest

from infrastructure.storage.s3 import S3StorageBackend
from src.shared.config import Settings
from src.shared.exceptions import StorageError


class FakeBody:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeBotoClient:
    def __init__(self):
        self.uploaded: list[tuple] = []
        self.deleted: list[tuple] = []
        self._get_object_response: dict | None = None
        self._raise: Exception | None = None

    def upload_fileobj(self, fileobj, bucket, key, ExtraArgs=None):
        if self._raise:
            raise self._raise
        self.uploaded.append((fileobj, bucket, key, ExtraArgs))

    def get_object(self, Bucket, Key):
        if self._raise:
            raise self._raise
        return self._get_object_response

    def delete_object(self, Bucket, Key):
        if self._raise:
            raise self._raise
        self.deleted.append((Bucket, Key))


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
        s3_bucket="rag-documents",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def _backend(fake_client: FakeBotoClient) -> S3StorageBackend:
    backend = S3StorageBackend(_settings())
    backend._client = fake_client
    return backend


def test_upload_delegates_to_boto_client_with_content_type():
    fake_client = FakeBotoClient()
    backend = _backend(fake_client)
    fileobj = io.BytesIO(b"data")

    backend.upload("key.pdf", fileobj, "application/pdf")

    assert fake_client.uploaded == [(fileobj, "rag-documents", "key.pdf", {"ContentType": "application/pdf"})]


def test_upload_wraps_client_exception_in_storage_error():
    fake_client = FakeBotoClient()
    fake_client._raise = RuntimeError("boom")
    backend = _backend(fake_client)

    with pytest.raises(StorageError):
        backend.upload("key.pdf", io.BytesIO(b"data"), "application/pdf")


def test_download_returns_body_bytes_from_client():
    fake_client = FakeBotoClient()
    fake_client._get_object_response = {"Body": FakeBody(b"contents")}
    backend = _backend(fake_client)

    assert backend.download("key.pdf") == b"contents"


def test_download_wraps_client_exception_in_storage_error():
    fake_client = FakeBotoClient()
    fake_client._raise = RuntimeError("boom")
    backend = _backend(fake_client)

    with pytest.raises(StorageError):
        backend.download("key.pdf")


def test_delete_delegates_to_boto_client():
    fake_client = FakeBotoClient()
    backend = _backend(fake_client)

    backend.delete("key.pdf")

    assert fake_client.deleted == [("rag-documents", "key.pdf")]


def test_delete_wraps_client_exception_in_storage_error():
    fake_client = FakeBotoClient()
    fake_client._raise = RuntimeError("boom")
    backend = _backend(fake_client)

    with pytest.raises(StorageError):
        backend.delete("key.pdf")
