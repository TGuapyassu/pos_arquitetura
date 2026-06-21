from __future__ import annotations

from decimal import Decimal
from typing import List

from app.domain.entities import (
    Cliente,
    ItemPecaOS,
    ItemServicoOS,
    OrdemServico,
    Peca,
    ServicoOficina,
    Usuario,
    Veiculo,
)
from app.infrastructure.database.models import (
    ClienteOrm,
    OrdemServicoOrm,
    OrdemServicoPecaOrm,
    OrdemServicoServicoOrm,
    PecaOrm,
    ServicoOrm,
    UsuarioOrm,
    VeiculoOrm,
)


def cliente_orm_to_domain(m: ClienteOrm) -> Cliente:
    return Cliente(
        id=m.id,
        cpf_cnpj=m.cpf_cnpj,
        nome=m.nome,
        contato=m.contato,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def veiculo_orm_to_domain(m: VeiculoOrm) -> Veiculo:
    return Veiculo(
        id=m.id,
        cliente_id=m.cliente_id,
        placa=m.placa,
        marca=m.marca,
        modelo=m.modelo,
        ano=m.ano,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def servico_orm_to_domain(m: ServicoOrm) -> ServicoOficina:
    return ServicoOficina(
        id=m.id,
        nome=m.nome,
        preco=m.preco,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def peca_orm_to_domain(m: PecaOrm) -> Peca:
    return Peca(
        id=m.id,
        nome=m.nome,
        preco=m.preco,
        quantidade_estoque=m.quantidade_estoque,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def os_orm_to_domain(m: OrdemServicoOrm) -> OrdemServico:
    it_s: List[ItemServicoOS] = [
        ItemServicoOS(
            servico_id=i.servico_id,
            quantidade=i.quantidade,
            preco_unitario=Decimal(i.preco_unitario),
        )
        for i in m.itens_servico
    ]
    it_p: List[ItemPecaOS] = [
        ItemPecaOS(
            peca_id=i.peca_id,
            quantidade=i.quantidade,
            preco_unitario=Decimal(i.preco_unitario),
        )
        for i in m.itens_peca
    ]
    o = OrdemServico(
        id=m.id,
        cliente_id=m.cliente_id,
        veiculo_id=m.veiculo_id,
        status=m.status,
        itens_servico=it_s,
        itens_peca=it_p,
        valor_total=Decimal(m.valor_total) if m.valor_total is not None else None,
        aprovada_em=m.aprovada_em,
        recusada_em=m.recusada_em,
        referencia_externa=m.referencia_externa,
        created_at=m.created_at,
        updated_at=m.updated_at,
        data_finalizacao=m.data_finalizacao,
        data_entrega=m.data_entrega,
    )
    o.alinhar_valor_total_ao_carregar()
    return o


def sync_os_domain_to_orm(o: OrdemServico, m: OrdemServicoOrm) -> OrdemServicoOrm:
    m.cliente_id = o.cliente_id
    m.veiculo_id = o.veiculo_id
    m.status = o.status
    m.valor_total = o.valor_total
    m.aprovada_em = o.aprovada_em
    m.recusada_em = o.recusada_em
    m.referencia_externa = o.referencia_externa
    m.data_finalizacao = o.data_finalizacao
    m.data_entrega = o.data_entrega
    m.itens_servico = [
        OrdemServicoServicoOrm(
            servico_id=i.servico_id, quantidade=i.quantidade, preco_unitario=i.preco_unitario
        )
        for i in o.itens_servico
    ]
    m.itens_peca = [
        OrdemServicoPecaOrm(
            peca_id=i.peca_id, quantidade=i.quantidade, preco_unitario=i.preco_unitario
        )
        for i in o.itens_peca
    ]
    return m


def usuario_orm_to_domain(m: UsuarioOrm) -> Usuario:
    return Usuario(
        id=m.id,
        email=m.email,
        senha_hash=m.senha_hash,
        is_admin=m.is_admin,
        is_active=m.is_active,
        created_at=m.created_at,
    )
