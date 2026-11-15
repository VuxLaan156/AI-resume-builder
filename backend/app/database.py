import os
from functools import cache
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


def get_database_url() -> str | URL:
    if database_url := os.environ.get("DATABASE_URL"):
        return database_url

    env_file = Path(__file__).resolve().parents[2] / "infrastructure/.env"
    settings = {**dotenv_values(env_file), **os.environ}
    if database_url := settings.get("DATABASE_URL"):
        return database_url

    password = settings.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("Set DATABASE_URL or POSTGRES_PASSWORD in infrastructure/.env")
    return URL.create(
        "postgresql+psycopg",
        username="resume_user",
        password=password,
        host="127.0.0.1",
        port=int(settings.get("POSTGRES_PORT") or "15432"),
        database="resume_db",
    )


@cache
def get_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)


def get_session():
    with Session(get_engine()) as session:
        yield session
