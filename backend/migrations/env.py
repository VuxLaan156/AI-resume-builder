import os
from pathlib import Path

from alembic import context
from dotenv import dotenv_values
from sqlalchemy import URL, create_engine, pool


if context.is_offline_mode():
    context.configure(dialect_name="postgresql", literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        settings = {
            **dotenv_values(Path(__file__).resolve().parents[2] / "infrastructure/.env"),
            **os.environ,
        }
        password = settings.get("POSTGRES_PASSWORD")
        if not password:
            raise RuntimeError("Set DATABASE_URL or POSTGRES_PASSWORD in infrastructure/.env")
        database_url = URL.create(
            "postgresql+psycopg",
            username="resume_user",
            password=password,
            host="127.0.0.1",
            port=int(settings.get("POSTGRES_PORT") or "15432"),
            database="resume_db",
        )
    engine = create_engine(database_url, poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
