from __future__ import annotations

from functools import lru_cache
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

SessionFactory: Optional[sessionmaker[Session]] = None


@lru_cache
def get_engine() -> Engine:
    from app.infrastructure.config import get_settings

    url = get_settings().database_url
    if url.startswith("sqlite"):
        return create_engine(
            url, pool_pre_ping=True, future=True, connect_args={"check_same_thread": False}
        )
    return create_engine(url, pool_pre_ping=True, future=True)


def get_session() -> Generator[Session, None, None]:
    global SessionFactory
    if SessionFactory is None:
        SessionFactory = sessionmaker(
            get_engine(), autoflush=False, autocommit=False, future=True, expire_on_commit=False
        )
    db: Session = SessionFactory()
    try:
        yield db
    finally:
        db.close()


def reset_engine_and_session() -> None:
    global SessionFactory
    f = get_engine
    if hasattr(f, "cache_clear"):
        f.cache_clear()  # type: ignore[union-attr]
    SessionFactory = None
