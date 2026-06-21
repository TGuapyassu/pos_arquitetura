from datetime import datetime, timezone

from app.domain.entities import OrdemServico
from app.domain.enums import OrdemServicoStatus
from app.domain.services.ordem_servico_listagem import (
    descricao_status,
    ordenar_ordens_ativas,
    prioridade_listagem,
)


def test_prioridade_listagem():
    assert prioridade_listagem(OrdemServicoStatus.EM_EXECUCAO) < prioridade_listagem(
        OrdemServicoStatus.AGUARDANDO_APROVACAO
    )
    assert prioridade_listagem(OrdemServicoStatus.ORCAMENTO_RECUSADO) == 2


def test_descricao_status():
    assert descricao_status(OrdemServicoStatus.ORCAMENTO_RECUSADO) == "Orçamento Recusado"


def test_ordenar_mais_antigas_primeiro_mesma_prioridade():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    o1 = OrdemServico(
        cliente_id=1,
        veiculo_id=1,
        status=OrdemServicoStatus.RECEBIDA,
        id=1,
        created_at=base,
    )
    o2 = OrdemServico(
        cliente_id=1,
        veiculo_id=1,
        status=OrdemServicoStatus.RECEBIDA,
        id=2,
        created_at=base.replace(day=2),
    )
    ordenadas = ordenar_ordens_ativas([o2, o1])
    assert [x.id for x in ordenadas] == [1, 2]
