from infrastructure.storage.base import StorageBackend
from infrastructure.storage.local import LocalStorageBackend
from infrastructure.storage.s3 import S3StorageBackend
from src.shared.config import Settings


def get_storage_backend(settings: Settings) -> StorageBackend:
    if settings.storage_provider == "local":
        return LocalStorageBackend(settings)
    return S3StorageBackend(settings)
