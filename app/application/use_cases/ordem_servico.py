from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.application.dtos import OrdemCreateIn, OrdemOut, OrdemUpdateStatusIn
from app.application.dtos.ordem_dto import OrdemPublicaOut
from app.application.mapping.dto_mappers import ordem_to_out, ordem_to_publica
from app.domain.entities import (
    ItemPecaOS,
    ItemServicoOS,
    OrdemServico,
    Peca,
)
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.value_objects import CpfCnpj, Placa
from app.infrastructure.repositories.sqlalchemy_cliente import SqlAlchemyClienteRepository
from app.infrastructure.repositories.sqlalchemy_ordem_servico import SqlAlchemyOrdemServicoRepository
from app.infrastructure.repositories.sqlalchemy_peca import SqlAlchemyPecaRepository
from app.infrastructure.repositories.sqlalchemy_servico import SqlAlchemyServicoOficinaRepository
from app.infrastructure.repositories.sqlalchemy_veiculo import SqlAlchemyVeiculoRepository


def _get_repos(
    s: Session,
) -> tuple[
    SqlAlchemyClienteRepository,
    SqlAlchemyVeiculoRepository,
    SqlAlchemyServicoOficinaRepository,
    SqlAlchemyPecaRepository,
    SqlAlchemyOrdemServicoRepository,
]:
    return (
        SqlAlchemyClienteRepository(s),
        SqlAlchemyVeiculoRepository(s),
        SqlAlchemyServicoOficinaRepository(s),
        SqlAlchemyPecaRepository(s),
        SqlAlchemyOrdemServicoRepository(s),
    )


def criar_ordem(
    s: Session,
    body: OrdemCreateIn,
) -> OrdemOut:
    c_repo, v_repo, svc_repo, p_repo, o_repo = _get_repos(s)
    cli = c_repo.get_by_id(body.cliente_id)
    if not cli:
        raise NotFoundError("Cliente não encontrado.")
    _ = CpfCnpj.parse(cli.cpf_cnpj)  # valida documento em cadastros anteriores

    v = v_repo.get_by_id(body.veiculo_id)
    if not v:
        raise NotFoundError("Veículo não encontrado.")
    _ = Placa.parse(v.placa)
    if v.cliente_id != body.cliente_id:
        raise ConflictError("Veículo não pertence ao cliente informado.")

    it_s: list[ItemServicoOS] = []
    for lin in body.servicos:
        so = svc_repo.get_by_id(lin.servico_id)
        if not so:
            raise NotFoundError(f"Serviço id={lin.servico_id} não encontrado.")
        it_s.append(
            ItemServicoOS(
                servico_id=so.id or lin.servico_id,
                quantidade=lin.quantidade,
                preco_unitario=Decimal(so.preco).quantize(Decimal("0.01")),
            )
        )

    ag_p: dict[int, int] = defaultdict(int)
    for lin in body.pecas:
        ag_p[lin.peca_id] += lin.quantidade

    peca_map: dict[int, Peca] = {}
    for pid, q in ag_p.items():
        p = p_repo.get_by_id(pid)
        if not p:
            raise NotFoundError(f"Peça id={pid} não encontrada.")
        p.reservar_ou_baixar(q)
        peca_map[pid] = p
        p_repo.update(p)

    it_p: list[ItemPecaOS] = []
    for lin in body.pecas:
        p = peca_map[lin.peca_id]
        it_p.append(
            ItemPecaOS(
                peca_id=p.id or lin.peca_id,
                quantidade=lin.quantidade,
                preco_unitario=Decimal(p.preco).quantize(Decimal("0.01")),
            )
        )

    os_ = OrdemServico.abrir_nova(cliente_id=body.cliente_id, veiculo_id=body.veiculo_id)
    os_.atribuir_itens(it_s, it_p)
    o_repo.add(os_)
    return ordem_to_out(o_repo.get_by_id(os_.id) or os_)  # type: ignore[arg-type]


def listar_os(s: Session) -> list[OrdemOut]:
    _, _, _, _, o_repo = _get_repos(s)
    return [ordem_to_out(o) for o in o_repo.listar()]


def obter_os(s: Session, id: int) -> OrdemOut:
    _, _, _, _, o_repo = _get_repos(s)
    o = o_repo.get_by_id(id)
    if o is None:
        raise NotFoundError("OS não encontrada.")
    return ordem_to_out(o)


def public_obter_os(s: Session, id: int) -> OrdemPublicaOut:
    o = _get_repos(s)[-1].get_by_id(id)
    if o is None:
        raise NotFoundError("OS não encontrada.")
    return ordem_to_publica(o)


def patch_status(
    s: Session,
    id: int,
    body: OrdemUpdateStatusIn,
) -> OrdemOut:
    _, _, _, _, o_repo = _get_repos(s)
    o = o_repo.get_by_id(id)
    if o is None:
        raise NotFoundError("OS não encontrada.")
    o.transicionar_por_patch(body.status)
    o_repo.update(o)
    return ordem_to_out(o_repo.get_by_id(id) or o)


def aprovar(s: Session, id: int) -> OrdemOut:
    _, _, _, _, o_repo = _get_repos(s)
    o = o_repo.get_by_id(id)
    if o is None:
        raise NotFoundError("OS não encontrada.")
    o.aprovar_orcamento()
    o_repo.update(o)
    return ordem_to_out(o_repo.get_by_id(id) or o)
