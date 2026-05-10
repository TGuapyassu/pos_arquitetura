from __future__ import annotations

from app.domain.enums import OrdemServicoStatus
from app.domain.exceptions import AprovacaoNecessariaError, TransicaoStatusInvalidaError

# Transições permitidas via operação genérica (ex.: PATCH).
# O salto para EM_EXECUÇAO a partir de AGUARDANDO_APROVACAO só via POST /aprovar.
_ALLOWED_PATCH: dict[OrdemServicoStatus, frozenset[OrdemServicoStatus]] = {
    OrdemServicoStatus.RECEBIDA: frozenset({OrdemServicoStatus.EM_DIAGNOSTICO}),
    OrdemServicoStatus.EM_DIAGNOSTICO: frozenset(
        {OrdemServicoStatus.AGUARDANDO_APROVACAO}
    ),
    OrdemServicoStatus.AGUARDANDO_APROVACAO: frozenset(),  # aprovar é caminho explícito
    OrdemServicoStatus.EM_EXECUCAO: frozenset({OrdemServicoStatus.FINALIZADA}),
    OrdemServicoStatus.FINALIZADA: frozenset({OrdemServicoStatus.ENTREGUE}),
    OrdemServicoStatus.ENTREGUE: frozenset(),
}


def transicao_status_via_patch_permitida(
    origem: OrdemServicoStatus, destino: OrdemServicoStatus
) -> None:
    if origem == destino:
        return
    if destino == OrdemServicoStatus.EM_EXECUCAO and origem in (
        OrdemServicoStatus.AGUARDANDO_APROVACAO,
    ):
        raise AprovacaoNecessariaError(
            "A OS deve ser aprovada (POST /aprovar) antes de entrar em execução."
        )
    permitidos = _ALLOWED_PATCH.get(origem, frozenset())
    if destino not in permitidos:
        raise TransicaoStatusInvalidaError(
            f"Transição de {origem.value} para {destino.value} não é permitida."
        )


def transicao_apos_aprovacao(origem: OrdemServicoStatus) -> OrdemServicoStatus:
    if origem != OrdemServicoStatus.AGUARDANDO_APROVACAO:
        raise TransicaoStatusInvalidaError("Só é possível aprovar em AGUARDANDO_APROVACAO.")
    return OrdemServicoStatus.EM_EXECUCAO


def requer_execucao(status: OrdemServicoStatus) -> bool:
    return status == OrdemServicoStatus.EM_EXECUCAO
