"""Creates the ANN index on document_chunks.embedding. Run once after the
initial migration (ivfflat needs data present to pick good list counts, but
an empty-table build is fine for local/dev use)."""
from sqlalchemy import text

from infrastructure.postgres.connection import engine

if __name__ == "__main__":
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding "
                "ON document_chunks USING ivfflat (embedding vector_cosine_ops) "
                "WITH (lists = 100)"
            )
        )
    print("pgvector index created")
