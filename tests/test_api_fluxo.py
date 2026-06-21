def _headers(t):
    return {"Authorization": f"Bearer {t}"} if t else {}


def test_criar_os_muda_status_aprovar(test_client):
    from app.infrastructure.security import create_token

    token = create_token(1, "a@test.com", is_admin=True)
    h = _headers(token)

    r0 = test_client.post(
        "/clientes",
        json={
            "nome": "José",
            "contato": "a@a.com",
            "cpf_cnpj": "52998224725",
        },
        headers=h,
    )
    assert r0.status_code in (201, 200)
    client_id = r0.json()["id"]

    r1 = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "ABC1234",
            "marca": "Fiat",
            "modelo": "Uno",
            "ano": 2015,
        },
        headers=h,
    )
    assert r1.status_code in (201, 200)
    v_id = r1.json()["id"]

    r2 = test_client.post(
        "/servicos", json={"nome": "Troca óleo", "preco": "100.00"}, headers=h
    )
    s_id = r2.json()["id"]
    r3 = test_client.post(
        "/pecas",
        json={"nome": "Filtro", "preco": "25.00", "quantidade_estoque": 10},
        headers=h,
    )
    p_id = r3.json()["id"]

    ro = test_client.post(
        "/os",
        json={
            "cliente_id": client_id,
            "veiculo_id": v_id,
            "servicos": [{"servico_id": s_id, "quantidade": 1}],
            "pecas": [{"peca_id": p_id, "quantidade": 2}],
        },
        headers=h,
    )
    assert ro.status_code == 201
    os_id = ro.json()["id"]
    assert os_id > 0

    det = test_client.get(f"/os/{os_id}", headers=h).json()
    assert det["status"] == "RECEBIDA"
    assert float(det["valor_total"]) == 150.0

    p_get = test_client.get(f"/pecas/{p_id}", headers=h).json()
    assert p_get["quantidade_estoque"] == 8  # 10-2

    t1 = test_client.patch(
        f"/os/{os_id}/status",
        json={"status": "EM_DIAGNOSTICO"},
        headers=h,
    )
    assert t1.status_code == 200
    t2 = test_client.patch(
        f"/os/{os_id}/status", json={"status": "AGUARDANDO_APROVACAO"}, headers=h
    )
    assert t2.status_code == 200
    t_bad = test_client.patch(
        f"/os/{os_id}/status", json={"status": "EM_EXECUCAO"}, headers=h
    )
    assert t_bad.status_code in (400, 409)  # bloqueia sem aprovar

    ap = test_client.post(f"/os/{os_id}/aprovar", headers=h)
    assert ap.status_code == 200
    assert ap.json()["status"] == "EM_EXECUCAO"
    t3 = test_client.patch(
        f"/os/{os_id}/status", json={"status": "FINALIZADA"}, headers=h
    )
    assert t3.status_code == 200
    t4 = test_client.patch(
        f"/os/{os_id}/status", json={"status": "ENTREGUE"}, headers=h
    )
    assert t4.status_code == 200
    assert t4.json()["status"] == "ENTREGUE"
    assert t4.json()["data_entrega"] is not None

    pub = test_client.get(f"/public/ordens-servico/{os_id}")
    assert pub.status_code == 200
    pub_body = pub.json()
    assert pub_body["valor_total"] is not None
    assert pub_body["status"] == "ENTREGUE"
    assert "cliente_id" not in pub_body
    assert "servicos" not in pub_body


def test_criar_os_estoque_insuficiente_retorna_409(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", is_admin=True))
    r0 = test_client.post(
        "/clientes",
        json={"nome": "Ana", "contato": "a@a.com", "cpf_cnpj": "52998224725"},
        headers=h,
    )
    client_id = r0.json()["id"]
    r1 = test_client.post(
        "/veiculos",
        json={
            "cliente_id": client_id,
            "placa": "ABC1234",
            "marca": "Fiat",
            "modelo": "Uno",
            "ano": 2015,
        },
        headers=h,
    )
    v_id = r1.json()["id"]
    r3 = test_client.post(
        "/pecas",
        json={"nome": "Filtro", "preco": "25.00", "quantidade_estoque": 1},
        headers=h,
    )
    p_id = r3.json()["id"]
    ro = test_client.post(
        "/os",
        json={
            "cliente_id": client_id,
            "veiculo_id": v_id,
            "servicos": [],
            "pecas": [{"peca_id": p_id, "quantidade": 5}],
        },
        headers=h,
    )
    assert ro.status_code == 409
    p_get = test_client.get(f"/pecas/{p_id}", headers=h).json()
    assert p_get["quantidade_estoque"] == 1


def test_consulta_publica_os_inexistente_retorna_404(test_client):
    r = test_client.get("/public/ordens-servico/99999")
    assert r.status_code == 404


def test_peca_estoque_endpoint(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", True))
    r = test_client.post(
        "/pecas",
        json={"nome": "A", "preco": 1, "quantidade_estoque": 3},
        headers=h,
    )
    pid = r.json()["id"]
    p = test_client.patch(
        f"/pecas/{pid}/estoque", json={"quantidade": 10, "ajuste_absoluto": True}, headers=h
    )
    assert p.json()["quantidade_estoque"] == 10
    p2 = test_client.patch(
        f"/pecas/{pid}/estoque", json={"quantidade": -1, "ajuste_absoluto": False}, headers=h
    )
    assert p2.json()["quantidade_estoque"] == 9


def test_peca_estoque_delta_negativo_alem_disponivel_retorna_409(test_client):
    from app.infrastructure.security import create_token

    h = _headers(create_token(1, "a@test.com", True))
    r = test_client.post(
        "/pecas",
        json={"nome": "B", "preco": 1, "quantidade_estoque": 2},
        headers=h,
    )
    pid = r.json()["id"]
    bad = test_client.patch(
        f"/pecas/{pid}/estoque",
        json={"quantidade": -5, "ajuste_absoluto": False},
        headers=h,
    )
    assert bad.status_code in (400, 409)
    ok = test_client.get(f"/pecas/{pid}", headers=h)
    assert ok.json()["quantidade_estoque"] == 2
