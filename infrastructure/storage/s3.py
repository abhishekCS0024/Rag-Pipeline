# boto3-based StorageBackend implementation, supporting both AWS S3 and MinIO.
from typing import BinaryIO

import boto3

from infrastructure.storage.base import StorageBackend
from src.shared.config import Settings
from src.shared.exceptions import StorageError


class S3StorageBackend(StorageBackend):
    def __init__(self, settings: Settings):
        self._bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint or None,
            aws_access_key_id=settings.s3_access_key or None,
            aws_secret_access_key=settings.s3_secret_key or None,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
        )

    def upload(self, key: str, fileobj: BinaryIO, content_type: str) -> None:
        try:
            self._client.upload_fileobj(
                fileobj,
                self._bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
        except Exception as exc:
            raise StorageError(f"failed to upload {key}: {exc}") from exc

    def download(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except Exception as exc:
            raise StorageError(f"failed to download {key}: {exc}") from exc

    def delete(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except Exception as exc:
            raise StorageError(f"failed to delete {key}: {exc}") from exc
