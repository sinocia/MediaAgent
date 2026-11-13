"""Database engine and session configuration."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for persisted application models."""


def database_url() -> str:
    """Return the configured database URL; SQLite keeps local setup friction low."""
    return os.getenv("DATABASE_URL", "sqlite:///./media_agent.db")


def make_engine(url: str | None = None):
    selected_url = url or database_url()
    options = {"check_same_thread": False} if selected_url.startswith("sqlite") else {}
    return create_engine(selected_url, connect_args=options, pool_pre_ping=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
