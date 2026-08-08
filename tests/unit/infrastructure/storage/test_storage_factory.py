from infrastructure.storage import get_storage_backend
from infrastructure.storage.local import LocalStorageBackend
from infrastructure.storage.s3 import S3StorageBackend
from src.shared.config import Settings


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_returns_local_backend_when_provider_is_local(tmp_path):
    settings = _settings(storage_provider="local", local_storage_path=str(tmp_path))

    backend = get_storage_backend(settings)

    assert isinstance(backend, LocalStorageBackend)


def test_returns_s3_backend_for_any_non_local_provider():
    settings = _settings(storage_provider="minio")

    backend = get_storage_backend(settings)

    assert isinstance(backend, S3StorageBackend)
