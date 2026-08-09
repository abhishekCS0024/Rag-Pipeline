# Session factory used to hand out SQLAlchemy DB sessions to repositories/routes.

from sqlalchemy.orm import sessionmaker

from infrastructure.postgres.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)