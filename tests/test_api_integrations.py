def _headers(token: str | None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _webhook_headers() -> dict[str, str]:
    return {"X-Webhook-Key": "chave-webhook-teste"}


def test_webhook_sem_chave_retorna_401(test_client):
    r = test_client.post(
        "/integrations/os/1/orcamento",
        json={"aprovado": True},
    )
    assert r.status_code == 401


def test_webhook_aprovar_orcamento(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", is_admin=True))
    client_id = test_client.post(
        "/clientes",
        json={"nome": "João", "contato": "joao@mail.com", "cpf_cnpj": "52998224725"},
        headers=h,
    ).json()["id"]
    v_id = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "ABC1234",
            "marca": "Fiat",
            "modelo": "Uno",
            "ano": 2015,
        },
        headers=h,
    ).json()["id"]
    s_id = test_client.post(
        "/servicos", json={"nome": "Troca óleo", "preco": "100.00"}, headers=h
    ).json()["id"]
    os_id = test_client.post(
        "/os",
        json={
            "cliente_id": client_id,
            "veiculo_id": v_id,
            "servicos": [{"servico_id": s_id, "quantidade": 1}],
            "pecas": [],
        },
        headers=h,
    ).json()["id"]
    test_client.patch(
        f"/os/{os_id}/status", json={"status": "EM_DIAGNOSTICO"}, headers=h
    )
    test_client.patch(
        f"/os/{os_id}/status", json={"status": "AGUARDANDO_APROVACAO"}, headers=h
    )

    r = test_client.post(
        f"/integrations/os/{os_id}/orcamento",
        json={"aprovado": True, "referencia_externa": "n8n-1"},
        headers=_webhook_headers(),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "EM_EXECUCAO"
    assert r.json()["status_descricao"] == "Execução"


def test_webhook_recusar_orcamento(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", is_admin=True))
    client_id = test_client.post(
        "/clientes",
        json={"nome": "Ana", "contato": "ana@mail.com", "cpf_cnpj": "52998224725"},
        headers=h,
    ).json()["id"]
    v_id = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "DEF5678",
            "marca": "VW",
            "modelo": "Gol",
            "ano": 2020,
        },
        headers=h,
    ).json()["id"]
    s_id = test_client.post(
        "/servicos", json={"nome": "Alinhamento", "preco": "80.00"}, headers=h
    ).json()["id"]
    os_id = test_client.post(
        "/os",
        json={
            "cliente_id": client_id,
            "veiculo_id": v_id,
            "servicos": [{"servico_id": s_id, "quantidade": 1}],
            "pecas": [],
        },
        headers=h,
    ).json()["id"]
    test_client.patch(
        f"/os/{os_id}/status", json={"status": "EM_DIAGNOSTICO"}, headers=h
    )
    test_client.patch(
        f"/os/{os_id}/status", json={"status": "AGUARDANDO_APROVACAO"}, headers=h
    )

    r = test_client.post(
        f"/integrations/os/{os_id}/orcamento",
        json={"aprovado": False, "referencia_externa": "email-recusa"},
        headers=_webhook_headers(),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ORCAMENTO_RECUSADO"


def test_webhook_atualizar_status(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", is_admin=True))
    client_id = test_client.post(
        "/clientes",
        json={"nome": "Luiz", "contato": "luiz@mail.com", "cpf_cnpj": "52998224725"},
        headers=h,
    ).json()["id"]
    v_id = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "GHI9012",
            "marca": "Ford",
            "modelo": "Ka",
            "ano": 2018,
        },
        headers=h,
    ).json()["id"]
    os_id = test_client.post(
        "/os",
        json={"cliente_id": client_id, "veiculo_id": v_id, "servicos": [], "pecas": []},
        headers=h,
    ).json()["id"]

    r = test_client.post(
        f"/integrations/os/{os_id}/status",
        json={"status": "EM_DIAGNOSTICO", "referencia_externa": "zapier-9"},
        headers=_webhook_headers(),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "EM_DIAGNOSTICO"
    assert r.json()["status_descricao"] == "Diagnóstico"


def test_consulta_status_publica(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", is_admin=True))
    client_id = test_client.post(
        "/clientes",
        json={"nome": "Pedro", "contato": "pedro@mail.com", "cpf_cnpj": "52998224725"},
        headers=h,
    ).json()["id"]
    v_id = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "JKL3456",
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2019,
        },
        headers=h,
    ).json()["id"]
    os_id = test_client.post(
        "/os",
        json={"cliente_id": client_id, "veiculo_id": v_id, "servicos": [], "pecas": []},
        headers=h,
    ).json()["id"]

    r = test_client.get(f"/public/ordens-servico/{os_id}/status")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == os_id
    assert body["status"] == "RECEBIDA"
    assert body["status_descricao"] == "Recebida"
