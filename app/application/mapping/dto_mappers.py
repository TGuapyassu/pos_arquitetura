from __future__ import annotations

from decimal import Decimal

from app.application.dtos import (
    ClienteOut,
    OrdemOut,
    OrdemPublicaOut,
    PecaOut,
    ServicoOut,
    VeiculoOut,
)
from app.domain.entities import Cliente, OrdemServico, Peca, ServicoOficina, Veiculo


def cliente_to_out(c: Cliente) -> ClienteOut:
    return ClienteOut(
        id=c.id or 0,
        nome=c.nome,
        contato=c.contato,
        cpf_cnpj=c.cpf_cnpj,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def veiculo_to_out(v: Veiculo) -> VeiculoOut:
    return VeiculoOut(
        id=v.id or 0,
        cliente_id=v.cliente_id,
        placa=v.placa,
        marca=v.marca,
        modelo=v.modelo,
        ano=v.ano,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )


def servico_to_out(s: ServicoOficina) -> ServicoOut:
    return ServicoOut(
        id=s.id or 0,
        nome=s.nome,
        preco=Decimal(s.preco),
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def peca_to_out(p: Peca) -> PecaOut:
    return PecaOut(
        id=p.id or 0,
        nome=p.nome,
        preco=Decimal(p.preco),
        quantidade_estoque=p.quantidade_estoque,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def ordem_to_out(o: OrdemServico) -> OrdemOut:
    from app.application.dtos.ordem_dto import OrdemItemOut

    v = o.valor_total or o.calcular_valor_total()
    return OrdemOut(
        id=o.id or 0,
        cliente_id=o.cliente_id,
        veiculo_id=o.veiculo_id,
        status=o.status,
        valor_total=v,
        aprovada_em=o.aprovada_em,
        created_at=o.created_at,
        updated_at=o.updated_at,
        data_finalizacao=o.data_finalizacao,
        data_entrega=o.data_entrega,
        servicos=[
            OrdemItemOut(
                servico_id=i.servico_id, peca_id=None, quantidade=i.quantidade, preco_unitario=i.preco_unitario
            )
            for i in o.itens_servico
        ],
        pecas=[
            OrdemItemOut(
                servico_id=None, peca_id=i.peca_id, quantidade=i.quantidade, preco_unitario=i.preco_unitario
            )
            for i in o.itens_peca
        ],
    )


def ordem_to_publica(o: OrdemServico) -> OrdemPublicaOut:
    v = o.valor_total or o.calcular_valor_total()
    return OrdemPublicaOut(
        id=o.id or 0,
        status=o.status,
        valor_total=v,
        data_finalizacao=o.data_finalizacao,
        data_entrega=o.data_entrega,
    )
