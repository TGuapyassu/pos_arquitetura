from __future__ import annotations

from datetime import datetime

from app.domain.entities import OrdemServico
from app.domain.enums import OrdemServicoStatus

_PRIORIDADE: dict[OrdemServicoStatus, int] = {
    OrdemServicoStatus.EM_EXECUCAO: 0,
    OrdemServicoStatus.AGUARDANDO_APROVACAO: 1,
    OrdemServicoStatus.ORCAMENTO_RECUSADO: 2,
    OrdemServicoStatus.EM_DIAGNOSTICO: 3,
    OrdemServicoStatus.RECEBIDA: 4,
}

_STATUS_ATIVOS = frozenset(
    {
        OrdemServicoStatus.RECEBIDA,
        OrdemServicoStatus.EM_DIAGNOSTICO,
        OrdemServicoStatus.AGUARDANDO_APROVACAO,
        OrdemServicoStatus.ORCAMENTO_RECUSADO,
        OrdemServicoStatus.EM_EXECUCAO,
    }
)

_DESCRICOES: dict[OrdemServicoStatus, str] = {
    OrdemServicoStatus.RECEBIDA: "Recebida",
    OrdemServicoStatus.EM_DIAGNOSTICO: "Diagnóstico",
    OrdemServicoStatus.AGUARDANDO_APROVACAO: "Aguardando Aprovação",
    OrdemServicoStatus.ORCAMENTO_RECUSADO: "Orçamento Recusado",
    OrdemServicoStatus.EM_EXECUCAO: "Execução",
    OrdemServicoStatus.FINALIZADA: "Finalizada",
    OrdemServicoStatus.ENTREGUE: "Entregue",
}


def prioridade_listagem(status: OrdemServicoStatus) -> int:
    return _PRIORIDADE.get(status, 99)


def eh_status_ativo(status: OrdemServicoStatus) -> bool:
    return status in _STATUS_ATIVOS


def descricao_status(status: OrdemServicoStatus) -> str:
    return _DESCRICOES.get(status, status.value)


def chave_ordenacao_ativa(o: OrdemServico) -> tuple[int, datetime]:
    return (prioridade_listagem(o.status), o.created_at)


def ordenar_ordens_ativas(ordens: list[OrdemServico]) -> list[OrdemServico]:
    return sorted(ordens, key=chave_ordenacao_ativa)
