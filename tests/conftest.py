from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "chave-secreta-para-testes-32b---"
os.environ["WEBHOOK_API_KEY"] = "chave-webhook-teste"
os.environ["EMAIL_ENABLED"] = "false"
os.environ["APP_ENV"] = "development"
os.environ["PYTEST_CURRENT_TEST"] = "1"

from app.infrastructure.config import reset_settings_cache
from app.infrastructure.database import connection, get_session
from app.infrastructure.database.models import Base, UsuarioOrm
from app.infrastructure.security import create_token, hash_password
from app import main as main_mod


def auth_headers() -> dict[str, str]:
    t = create_token(1, "a@test.com", is_admin=True)
    return {"Authorization": f"Bearer {t}"}


def _new_engine():
    e = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
        echo=False,
    )
    return e


def _rebuild_schema(e) -> None:
    Base.metadata.drop_all(e, checkfirst=True)  # type: ignore[func-returns-value]
    Base.metadata.create_all(e, checkfirst=True)  # type: ignore[func-returns-value]


@pytest.fixture
def test_engine():
    e = _new_engine()
    _rebuild_schema(e)
    return e


@pytest.fixture
def test_client(test_engine, monkeypatch) -> Generator[TestClient, None, None]:
    reset_settings_cache()
    connection.reset_engine_and_session()
    if hasattr(connection.get_engine, "cache_clear"):
        connection.get_engine.cache_clear()
    monkeypatch.setattr(connection, "get_engine", lambda: test_engine)

    Sf = sessionmaker(
        test_engine, autocommit=False, autoflush=False, expire_on_commit=False, future=True
    )

    def _s():
        d = Sf()
        try:
            yield d
        finally:
            d.close()

    app = main_mod.app
    app.dependency_overrides = {}
    app.dependency_overrides[get_session] = _s

    with TestClient(app, base_url="http://test") as c:
        s = Sf()
        s.add(
            UsuarioOrm(
                id=1,
                email="a@test.com",
                senha_hash=hash_password("x"),
                is_admin=True,
                is_active=True,
            )
        )
        s.commit()
        s.close()
        try:
            yield c
        finally:
            app.dependency_overrides = {}


def unit_auth_headers() -> dict[str, str]:
    return auth_headers()
