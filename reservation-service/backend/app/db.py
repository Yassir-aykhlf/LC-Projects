from __future__ import annotations

from collections.abc import Generator
import os

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


PRODUCTION_DATABASE_NAMES = frozenset({"slotwise_prod"})
PRODUCTION_OVERRIDE_ENV = "SLOTWISE_ALLOW_PRODUCTION"


def assert_not_production(
    database_url: str,
    *,
    operation: str,
    allow_override: bool = True,
) -> None:
    """Refuse to point a routine operation at the production database.

    Production changes go through ``./ops/prod-migrate.sh``, which sets
    ``SLOTWISE_ALLOW_PRODUCTION`` for the one operation that is allowed to
    write there. Destructive fixtures never get that escape hatch.
    """
    name = make_url(database_url).database or ""
    if name not in PRODUCTION_DATABASE_NAMES:
        return
    if allow_override and os.getenv(PRODUCTION_OVERRIDE_ENV) == "1":
        return
    raise RuntimeError(
        f"Refusing to run {operation} against the production database {name!r}. "
        "Production changes go through ./ops/prod-migrate.sh; see ops/README.md."
    )


def create_database_engine(database_url: str) -> Engine:
    """Create the PostgreSQL engine shared by API request sessions."""
    if make_url(database_url).get_backend_name() != "postgresql":
        raise ValueError("SlotWise requires a PostgreSQL DATABASE_URL")
    assert_not_production(database_url, operation="the application")
    return create_engine(database_url, pool_pre_ping=True)


def get_db(request: Request) -> Generator[Session, None, None]:
    db = request.app.state.SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://slotwise:slotwise@127.0.0.1:5432/slotwise_local",
)
