from __future__ import annotations

import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

BACKEND = Path(__file__).parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.db import assert_not_production  # noqa: E402
from app.main import create_app  # noqa: E402
from app.seed import seed  # noqa: E402


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Use ./scripts/test-postgres.sh to run the visible tests")

# This suite truncates every table. It must never reach a real database.
assert_not_production(
    DATABASE_URL,
    operation="the destructive test fixture",
    allow_override=False,
)


@pytest.fixture()
def app():
    application = create_app(DATABASE_URL)
    assert application.state.engine.dialect.name == "postgresql"
    with application.state.engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE reservation_audits, reservations, sessions, users "
                "RESTART IDENTITY CASCADE"
            )
        )
    with application.state.SessionLocal() as session:
        seed(session)
    yield application
    application.state.engine.dispose()


@pytest.fixture()
def client(app):
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def db(app):
    with app.state.SessionLocal() as session:
        yield session


def auth(user_id: int = 1) -> dict[str, str]:
    return {"X-User-ID": str(user_id)}
