def _headers(token: str | None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def test_rota_admin_sem_token_retorna_401(test_client):
    r = test_client.get("/clientes")
    assert r.status_code == 401


def test_rota_admin_token_invalido_retorna_401(test_client):
    r = test_client.get("/clientes", headers=_headers("token-invalido"))
    assert r.status_code == 401


def test_login_credenciais_invalidas_retorna_401(test_client):
    r = test_client.post("/auth/login", json={"email": "a@test.com", "senha": "errada"})
    assert r.status_code == 401


def test_login_sucesso(test_client):
    r = test_client.post("/auth/login", json={"email": "a@test.com", "senha": "x"})
    assert r.status_code == 200
    assert "access_token" in r.json()
