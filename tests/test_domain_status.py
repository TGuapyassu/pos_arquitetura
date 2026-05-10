import pytest
from decimal import Decimal

from app.domain.entities import OrdemServico, ItemPecaOS, ItemServicoOS, Peca
from app.domain.enums import OrdemServicoStatus
from app.domain.exceptions import (
    AprovacaoNecessariaError,
    EstoqueInsuficienteError,
    DomainError,
)
from app.domain.value_objects.cpf_cnpj import CpfCnpj


def test_cpf_cnpj_valido():
    c = CpfCnpj.parse("529.982.247-25")
    assert len(c.value) == 11
    c2 = CpfCnpj.parse("00.000.000/0001-91")
    assert len(c2.value) == 14


def test_vida_os_e_aprovacao_e_calculo():
    o = OrdemServico.abrir_nova(1, 1)
    assert o.status == OrdemServicoStatus.RECEBIDA
    s = [ItemServicoOS(1, 2, Decimal("50.00"))]
    p = [ItemPecaOS(1, 1, Decimal("25.00"))]
    o.atribuir_itens(s, p)
    assert o.valor_total == Decimal("125.00")

    o.transicionar_por_patch(OrdemServicoStatus.EM_DIAGNOSTICO)
    o.transicionar_por_patch(OrdemServicoStatus.AGUARDANDO_APROVACAO)
    with pytest.raises(AprovacaoNecessariaError):
        o.transicionar_por_patch(OrdemServicoStatus.EM_EXECUCAO)
    o.aprovar_orcamento()
    assert o.status == OrdemServicoStatus.EM_EXECUCAO
    assert o.aprovada_em is not None
    o.transicionar_por_patch(OrdemServicoStatus.FINALIZADA)
    assert o.data_finalizacao is not None
    o.transicionar_por_patch(OrdemServicoStatus.ENTREGUE)


def test_peca_estoque_negativo_bloqueia():
    p = Peca("f", Decimal("1"), 2, id=9)
    with pytest.raises(EstoqueInsuficienteError):
        p.reservar_ou_baixar(5)
    p.reservar_ou_baixar(1)
    assert p.quantidade_estoque == 1
    p.definir_estoque(0)
    with pytest.raises(DomainError):
        p.definir_estoque(-1)
