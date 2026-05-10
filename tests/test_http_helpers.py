from app.domain.exceptions import (
    AprovacaoNecessariaError,
    AutenticacaoError,
    ConflictError,
    DomainError,
    EstoqueInsuficienteError,
    NotFoundError,
    TransicaoStatusInvalidaError,
)
from app.infrastructure.security import create_token, verify_token
import pytest

from app.infrastructure.config import get_settings, reset_settings_cache
from app.main import app
from app.presentation.httpxx import errmap


def test_errmap_mapeia_excecoes() -> None:
    assert errmap(NotFoundError("x"))[0] == 404
    assert errmap(AutenticacaoError("x"))[0] == 401
    assert errmap(TransicaoStatusInvalidaError("x"))[0] == 400
    assert errmap(AprovacaoNecessariaError("a"))[0] == 400
    c, m = errmap(DomainError("b"))
    assert c == 400
    assert "b" in m
    assert errmap(EstoqueInsuficienteError(1, 2, 0))[0] == 409
    assert errmap(ConflictError("c"))[0] == 409
    assert errmap(ValueError("v"))[0] == 500


def test_jwt_baseline() -> None:
    reset_settings_cache()
    t = create_token(99, "z@test.com", True)
    p = verify_token(t)
    assert p is not None
    assert p.user_id == 99
    assert p.is_admin is True
    p2 = verify_token("a.b.c")
    assert p2 is None


def test_health() -> None:
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        r = c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_settings_cors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost,http://app")
    reset_settings_cache()
    s = get_settings()
    assert "http://localhost" in s.get_cors_origins_list()


def test_dinheiro_e_placa() -> None:
    from decimal import Decimal
    from app.domain.value_objects.dinheiro import Dinheiro
    from app.domain.value_objects.placa import Placa
    d = Dinheiro.from_reais(Decimal("10.50"))
    assert d.centavos == 1050
    p = Placa("ABC-1234")
    assert "1234" in p.value or len(p.value) == 7
