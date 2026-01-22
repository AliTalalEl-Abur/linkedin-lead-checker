from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

Base = declarative_base()


@lru_cache(maxsize=1)
def get_engine():
    """Create a cached SQLAlchemy engine using settings."""
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory() -> sessionmaker:
    """Return a configured session factory bound to the engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator:
    """FastAPI dependency that provides a scoped session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
