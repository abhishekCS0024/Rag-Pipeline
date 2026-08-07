from sqlalchemy import text

from infrastructure.postgres.connection import engine


with engine.connect() as connection:
    result = connection.execute(
        text("SELECT 1")
    )

    print(result.scalar())