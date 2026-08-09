# pydantic-settings Settings loaded from .env; central config for the ingestion pipeline (extend, don't read os.environ directly).
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "rag-platform"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Storage
    storage_provider: str = "minio"  # local | minio | s3
    s3_bucket: str = "rag-documents"
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint: str = ""
    s3_use_ssl: bool = False
    local_storage_path: str = "./data/uploads"

    max_upload_size_mb: int = 100
    allowed_file_types: str = "pdf,docx,pptx,txt"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_document_exchange: str = "rag.documents"
    rabbitmq_process_queue: str = "rag.document.processing"
    rabbitmq_reindex_queue: str = "rag.document.reindex"
    rabbitmq_delete_queue: str = "rag.document.delete"
    rabbitmq_process_routing_key: str = "document.process"
    rabbitmq_reindex_routing_key: str = "document.reindex"
    rabbitmq_delete_routing_key: str = "document.delete"
    rabbitmq_dlq: str = "rag.document.dlq"
    rabbitmq_retry_queue: str = "rag.document.retry"
    rabbitmq_max_retries: int = 3
    rabbitmq_prefetch_count: int = 2

    # Embeddings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str = ""
    embedding_batch_size: int = 32
    embedding_dimension: int = 1536

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100
    include_page_metadata: bool = True
    include_section_metadata: bool = True

    # API
    cors_origins: str = "http://localhost:8501"
    request_id_header: str = "X-Request-ID"
    enable_api_docs: bool = True

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @computed_field
    @property
    def allowed_file_types_list(self) -> list[str]:
        return [t.strip().lower() for t in self.allowed_file_types.split(",") if t.strip()]

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()