import io

import pytest

from infrastructure.storage.local import LocalStorageBackend
from src.shared.config import Settings
from src.shared.exceptions import StorageError


def _settings(local_storage_path: str, **overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
        local_storage_path=local_storage_path,
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_init_creates_storage_root_if_missing(tmp_path):
    root = tmp_path / "uploads"
    assert not root.exists()

    LocalStorageBackend(_settings(str(root)))

    assert root.is_dir()


def test_upload_then_download_round_trips_bytes(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    backend.upload("tenants/t1/documents/d1/report.pdf", io.BytesIO(b"hello world"), "application/pdf")

    assert backend.download("tenants/t1/documents/d1/report.pdf") == b"hello world"


def test_upload_creates_intermediate_directories(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    backend.upload("a/b/c/file.txt", io.BytesIO(b"x"), "text/plain")

    assert (tmp_path / "a" / "b" / "c" / "file.txt").read_bytes() == b"x"


def test_download_missing_key_raises_storage_error(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    with pytest.raises(StorageError):
        backend.download("does/not/exist.txt")


def test_delete_removes_existing_file(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))
    backend.upload("file.txt", io.BytesIO(b"x"), "text/plain")

    backend.delete("file.txt")

    assert not (tmp_path / "file.txt").exists()


def test_delete_missing_key_is_a_no_op(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    backend.delete("never/existed.txt")  # must not raise


def test_path_traversal_key_raises_storage_error_on_upload(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    with pytest.raises(StorageError):
        backend.upload("../../escape.txt", io.BytesIO(b"x"), "text/plain")


def test_path_traversal_key_raises_storage_error_on_download(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    with pytest.raises(StorageError):
        backend.download("../outside.txt")


def test_path_traversal_key_raises_storage_error_on_delete(tmp_path):
    backend = LocalStorageBackend(_settings(str(tmp_path)))

    with pytest.raises(StorageError):
        backend.delete("../outside.txt")
