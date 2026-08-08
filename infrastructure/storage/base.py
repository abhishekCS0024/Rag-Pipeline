from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    @abstractmethod
    def upload(self, key: str, fileobj: BinaryIO, content_type: str) -> None: ...

    @abstractmethod
    def download(self, key: str) -> bytes: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...
