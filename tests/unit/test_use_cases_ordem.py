from __future__ import annotations

from decimal import Decimal

import pytest

from app.application.dtos.ordem_dto import (
    OrdemCreateIn,
    OrdemItemPecaIn,
    OrdemItemServicoIn,
    OrcamentoDecisaoIn,
    OrdemUpdateStatusIn,
)
from app.application.use_cases.ordem_servico import (
    AprovarOrdemServico,
    AtualizarStatusOrdem,
    CriarOrdemServico,
    DecidirOrcamentoExterno,
    ListarOrdensServicoAtivas,
)
from app.domain.entities import Cliente, OrdemServico, Peca, ServicoOficina, Veiculo
from app.domain.enums import OrdemServicoStatus
from app.domain.exceptions import (
    AprovacaoNecessariaError,
    ConflictError,
    EstoqueInsuficienteError,
)
from tests.fakes import FakeRepositories
from tests.helpers.notifier import NoOpOsStatusNotifier


@pytest.fixture
def fake_repos() -> FakeRepositories:
    return FakeRepositories.vazio()


@pytest.fixture
def notifier(fake_repos: FakeRepositories) -> NoOpOsStatusNotifier:
    return NoOpOsStatusNotifier()


def _seed_basico(repos: FakeRepositories) -> tuple[int, int, int, int]:
    c = repos.clientes.add(Cliente(nome="José", contato="a@a.com", cpf_cnpj="52998224725"))
    v = repos.veiculos.add(
        Veiculo(cliente_id=c.id, placa="ABC1234", marca="Fiat", modelo="Uno", ano=2015)
    )
    s = repos.servicos.add(ServicoOficina(nome="Troca óleo", preco=Decimal("100.00")))
    p = repos.pecas.add(
        Peca(nome="Filtro", preco=Decimal("25.00"), quantidade_estoque=10)
    )
    return c.id, v.id, s.id, p.id  # type: ignore[misc]


def test_criar_os_retorna_id(fake_repos: FakeRepositories):
    c_id, v_id, s_id, p_id = _seed_basico(fake_repos)
    uc = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    out = uc.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[OrdemItemPecaIn(peca_id=p_id, quantidade=2)],
        )
    )
    assert out.id == 1
    peca = fake_repos.pecas.get_by_id(p_id)
    assert peca is not None
    assert peca.quantidade_estoque == 8


def test_criar_os_estoque_insuficiente(fake_repos: FakeRepositories):
    c_id, v_id, s_id, p_id = _seed_basico(fake_repos)
    uc = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    with pytest.raises(EstoqueInsuficienteError):
        uc.execute(
            OrdemCreateIn(
                cliente_id=c_id,
                veiculo_id=v_id,
                servicos=[],
                pecas=[OrdemItemPecaIn(peca_id=p_id, quantidade=100)],
            )
        )
    peca = fake_repos.pecas.get_by_id(p_id)
    assert peca is not None
    assert peca.quantidade_estoque == 10


def test_criar_os_veiculo_de_outro_cliente(fake_repos: FakeRepositories):
    c_id, v_id, s_id, p_id = _seed_basico(fake_repos)
    outro = fake_repos.clientes.add(
        Cliente(nome="Maria", contato="b@b.com", cpf_cnpj="39053344705")
    )
    uc = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    with pytest.raises(ConflictError):
        uc.execute(
            OrdemCreateIn(
                cliente_id=outro.id,  # type: ignore[arg-type]
                veiculo_id=v_id,
                servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
                pecas=[],
            )
        )


def test_patch_em_execucao_sem_aprovar(fake_repos: FakeRepositories, notifier: NoOpOsStatusNotifier):
    c_id, v_id, s_id, _ = _seed_basico(fake_repos)
    criar = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    os_out = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    patch = AtualizarStatusOrdem(fake_repos.ordens, notifier)
    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))
    with pytest.raises(AprovacaoNecessariaError):
        patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_EXECUCAO))


def test_aprovar_e_ciclo_ate_entregue(fake_repos: FakeRepositories, notifier: NoOpOsStatusNotifier):
    c_id, v_id, s_id, _ = _seed_basico(fake_repos)
    criar = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    os_out = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    patch = AtualizarStatusOrdem(fake_repos.ordens, notifier)
    aprovar = AprovarOrdemServico(fake_repos.ordens, notifier)

    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))
    ap = aprovar.execute(os_out.id)
    assert ap.status == OrdemServicoStatus.EM_EXECUCAO
    assert ap.aprovada_em is not None

    fin = patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.FINALIZADA))
    assert fin.data_finalizacao is not None

    ent = patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.ENTREGUE))
    assert ent.status == OrdemServicoStatus.ENTREGUE
    assert ent.data_entrega is not None


def test_recusa_orcamento_externa(fake_repos: FakeRepositories, notifier: NoOpOsStatusNotifier):
    c_id, v_id, s_id, _ = _seed_basico(fake_repos)
    criar = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    os_out = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    patch = AtualizarStatusOrdem(fake_repos.ordens, notifier)
    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os_out.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))

    decidir = DecidirOrcamentoExterno(fake_repos.ordens, notifier)
    out = decidir.execute(
        os_out.id,
        OrcamentoDecisaoIn(aprovado=False, referencia_externa="email-123"),
    )
    assert out.status == OrdemServicoStatus.ORCAMENTO_RECUSADO
    assert out.status_descricao == "Orçamento Recusado"


def test_listagem_ativa_exclui_finalizadas_e_ordenada(
    fake_repos: FakeRepositories, notifier: NoOpOsStatusNotifier
):
    c_id, v_id, s_id, _ = _seed_basico(fake_repos)
    criar = CriarOrdemServico(
        fake_repos.clientes,
        fake_repos.veiculos,
        fake_repos.servicos,
        fake_repos.pecas,
        fake_repos.ordens,
    )
    patch = AtualizarStatusOrdem(fake_repos.ordens, notifier)
    aprovar = AprovarOrdemServico(fake_repos.ordens, notifier)
    listar = ListarOrdensServicoAtivas(fake_repos.ordens)

    os1 = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    os2 = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    patch.execute(os2.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os2.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))
    aprovar.execute(os2.id)

    patch.execute(os1.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os1.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))
    aprovar.execute(os1.id)

    os3 = criar.execute(
        OrdemCreateIn(
            cliente_id=c_id,
            veiculo_id=v_id,
            servicos=[OrdemItemServicoIn(servico_id=s_id, quantidade=1)],
            pecas=[],
        )
    )
    patch.execute(os3.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.EM_DIAGNOSTICO))
    patch.execute(os3.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.AGUARDANDO_APROVACAO))
    aprovar.execute(os3.id)
    patch.execute(os3.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.FINALIZADA))
    patch.execute(os3.id, OrdemUpdateStatusIn(status=OrdemServicoStatus.ENTREGUE))

    ativas = listar.execute()
    ids = [o.id for o in ativas]
    assert os3.id not in ids
    assert len(ativas) == 2
    assert ativas[0].status == OrdemServicoStatus.EM_EXECUCAO
    assert ativas[0].id == os1.id
    assert ativas[1].id == os2.id
