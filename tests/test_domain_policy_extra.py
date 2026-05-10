from app.domain.enums import OrdemServicoStatus
from app.domain.services.ordem_servico_status import (
    requer_execucao,
    transicao_apos_aprovacao,
    transicao_status_via_patch_permitida,
)
from app.domain.exceptions import AprovacaoNecessariaError, TransicaoStatusInvalidaError
import pytest


def test_requer_execucao() -> None:
    assert requer_execucao(OrdemServicoStatus.EM_EXECUCAO) is True
    assert requer_execucao(OrdemServicoStatus.RECEBIDA) is False


def test_transicao_apos_aprovacao_apenas_de_aguardando() -> None:
    with pytest.raises(TransicaoStatusInvalidaError):
        transicao_apos_aprovacao(OrdemServicoStatus.RECEBIDA)
    assert (
        transicao_apos_aprovacao(OrdemServicoStatus.AGUARDANDO_APROVACAO)
        == OrdemServicoStatus.EM_EXECUCAO
    )


def test_same_status_noop() -> None:
    transicao_status_via_patch_permitida(
        OrdemServicoStatus.EM_DIAGNOSTICO, OrdemServicoStatus.EM_DIAGNOSTICO
    )


def test_transicao_patch_invalida() -> None:
    with pytest.raises(TransicaoStatusInvalidaError):
        transicao_status_via_patch_permitida(
            OrdemServicoStatus.EM_DIAGNOSTICO, OrdemServicoStatus.ENTREGUE
        )
