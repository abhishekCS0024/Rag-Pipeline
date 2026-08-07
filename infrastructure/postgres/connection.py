# establish and manage connectivity to PostgreSQL

from sqlalchemy import create_engine

from src.shared.config import get_settings


settings = get_settings()


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)