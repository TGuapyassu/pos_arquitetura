from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.application.dtos.peca_dto import PecaEstoqueIn, PecaIn, PecaOut
from app.application.mapping.dto_mappers import peca_to_out
from app.domain.entities import Peca
from app.domain.exceptions import NotFoundError
from app.infrastructure.repositories.sqlalchemy_peca import SqlAlchemyPecaRepository


def _r(s: Session) -> SqlAlchemyPecaRepository:
    return SqlAlchemyPecaRepository(s)


def criar(s: Session, body: PecaIn) -> PecaOut:
    p = Peca(
        nome=body.nome,
        preco=Decimal(body.preco).quantize(Decimal("0.01")),
        quantidade_estoque=body.quantidade_estoque,
    )
    _r(s).add(p)
    return peca_to_out(p)


def listar(s: Session) -> list[PecaOut]:
    return [peca_to_out(x) for x in _r(s).listar()]


def obter(s: Session, id: int) -> PecaOut:
    p = _r(s).get_by_id(id)
    if p is None:
        raise NotFoundError("Peça não encontrada.")
    return peca_to_out(p)


def atualizar(s: Session, id: int, body: PecaIn) -> PecaOut:
    repo = _r(s)
    p = repo.get_by_id(id)
    if p is None:
        raise NotFoundError("Peça não encontrada.")
    p.nome = body.nome
    p.preco = Decimal(body.preco).quantize(Decimal("0.01"))
    p.definir_estoque(body.quantidade_estoque)
    repo.update(p)
    return peca_to_out(p)


def atualizar_estoque(s: Session, id: int, body: PecaEstoqueIn) -> PecaOut:
    repo = _r(s)
    p = repo.get_by_id(id)
    if p is None:
        raise NotFoundError("Peça não encontrada.")
    if body.ajuste_absoluto:
        p.definir_estoque(body.quantidade)
    else:
        novo = p.quantidade_estoque + body.quantidade
        p.definir_estoque(novo)
    repo.update(p)
    return peca_to_out(p)


def deletar(s: Session, id: int) -> None:
    _r(s).delete(id)
