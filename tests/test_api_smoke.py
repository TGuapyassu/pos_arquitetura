"""Cobre rotas de autenticação e CRUD básico adicional para cobertura."""

from tests.conftest import auth_headers


def test_auth_login_token(test_client):
    r = test_client.post(
        "/auth/login", json={"email": "a@test.com", "senha": "x"}
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_broad(test_client):
    h = auth_headers()
    p = test_client.get("/pecas", headers=h)
    assert p.status_code == 200
    c = test_client.get("/clientes", headers=h)
    assert c.status_code == 200
    s = test_client.get("/servicos", headers=h)
    assert s.status_code == 200
    v = test_client.get("/veiculos", headers=h)
    assert v.status_code == 200
    o = test_client.get("/os", headers=h)
    assert o.status_code == 200
