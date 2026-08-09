# Filesystem-based StorageBackend implementation, with path traversal protection.
from pathlib import Path
from typing import BinaryIO

from infrastructure.storage.base import StorageBackend
from src.shared.config import Settings
from src.shared.exceptions import StorageError


class LocalStorageBackend(StorageBackend):
    def __init__(self, settings: Settings):
        self._root = Path(settings.local_storage_path)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if self._root.resolve() not in path.parents and path != self._root.resolve():
            raise StorageError(f"invalid storage key: {key}")
        return path

    def upload(self, key: str, fileobj: BinaryIO, content_type: str) -> None:
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(fileobj.read())

    def download(self, key: str) -> bytes:
        path = self._path_for(key)
        if not path.exists():
            raise StorageError(f"object not found: {key}")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        path.unlink(missing_ok=True)
