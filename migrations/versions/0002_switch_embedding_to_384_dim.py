"""switch document_chunks.embedding to 384 dims (huggingface all-MiniLM-L6-v2)

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_DIMENSION = 1536
NEW_DIMENSION = 384


def upgrade() -> None:
    # Existing 1536-dim (OpenAI) vectors are incompatible with the new 384-dim
    # (sentence-transformers) model — dev environment, no data worth preserving.
    op.execute("TRUNCATE TABLE document_chunks")
    op.drop_column("document_chunks", "embedding")
    op.add_column("document_chunks", sa.Column("embedding", Vector(NEW_DIMENSION), nullable=False))


def downgrade() -> None:
    op.execute("TRUNCATE TABLE document_chunks")
    op.drop_column("document_chunks", "embedding")
    op.add_column("document_chunks", sa.Column("embedding", Vector(OLD_DIMENSION), nullable=False))
