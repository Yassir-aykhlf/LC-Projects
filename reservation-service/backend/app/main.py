from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import sessionmaker

from .api import reservations, sessions
from .db import DEFAULT_DATABASE_URL, create_database_engine


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    """Build the API and its request-scoped database session factory.

    Schema migration and demo-data seeding are explicit CLI operations and are
    intentionally not application-factory side effects.
    """
    application = FastAPI(title="SlotWise API", version="0.1.0")
    engine = create_database_engine(database_url)
    application.state.engine = engine
    application.state.SessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    application.include_router(sessions.router)
    application.include_router(reservations.router)

    # The observation UI is served from the same origin as the API, so there is
    # no CORS configuration and no second port. Mounted last and at the root:
    # every API route lives under /api/, and Starlette matches routes in
    # registration order, so this cannot shadow one.
    if FRONTEND_DIR.is_dir():
        application.mount(
            "/",
            StaticFiles(directory=FRONTEND_DIR, html=True),
            name="frontend",
        )
    return application


app = create_app()
